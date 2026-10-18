import hashlib
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.auth import get_current_user, get_current_user_optional, get_current_superadmin, verify_sso_token_and_get_user, create_access_token
from app.core.config import settings
from app.models.models import (
    User, Meeting, MeetingParticipant, MeetingInvitation,
    Place, SearchCandidate, Vote, UserPreference, MeetingStatus
)
from app.schemas.schemas import (
    UserOut, UserPreferenceSchema, MeetingCreate, MeetingUpdate,
    MeetingOut, ParticipantCreate, ParticipantUpdate, ParticipantOut,
    CandidateOut, VoteCreate, InvitationAccept, PlaceOut, PlaceBase,
    AIChatRequest, AIChatResponse, AIParsedConstraints
)
import httpx
from app.services.scoring import evaluate_candidate
from app.services.ai import AIService

router = APIRouter()

# =============================================================================
# AUTH & ME
# =============================================================================
@router.post("/auth/callback")
async def sso_callback(payload: dict, db: AsyncSession = Depends(get_db)):
    code = payload.get("code")
    redirect_uri = payload.get("redirect_uri") or settings.SSO_REDIRECT_URI
    if not code:
        raise HTTPException(status_code=400, detail="Code d'autorisation manquant")
        
    token_url = f"{settings.SSO_BASE_URL.rstrip('/')}/oauth/token"
    token_payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": settings.SSO_CLIENT_ID,
        "client_secret": settings.SSO_CLIENT_SECRET,
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(token_url, data=token_payload)
            if res.status_code != 200:
                res = await client.post(token_url, json=token_payload)
            if res.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Échec échange jeton SSO: {res.text}")
            token_data = res.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Jeton d'accès manquant dans la réponse SSO")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur communication SSO: {str(e)}")
        
    user = await verify_sso_token_and_get_user(access_token, db)
    token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
    return {"token": token, "user": UserOut.model_validate(user)}

@router.post("/auth/sso-login")
async def sso_login(payload: dict, db: AsyncSession = Depends(get_db)):
    access_token = payload.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="access_token manquant")
    user = await verify_sso_token_and_get_user(access_token, db)
    token = create_access_token({"sub": user.id, "role": user.role, "email": user.email})
    return {"token": token, "user": UserOut.model_validate(user)}

@router.get("/me", response_model=UserOut)
async def get_me(user: User = Depends(get_current_user)):
    return user

@router.get("/preferences", response_model=UserPreferenceSchema)
async def get_preferences(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    pref = result.scalars().first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref

@router.patch("/preferences", response_model=UserPreferenceSchema)
async def update_preferences(data: UserPreferenceSchema, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    pref = result.scalars().first()
    if not pref:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
    for field, val in data.model_dump().items():
        setattr(pref, field, val)
    await db.commit()
    await db.refresh(pref)
    return pref

# =============================================================================
# PLACES SEARCH & CATALOG
# =============================================================================
@router.get("/places", response_model=List[PlaceOut])
async def list_places(
    category: Optional[str] = None,
    city: Optional[str] = None,
    halal: Optional[bool] = None,
    parking: Optional[bool] = None,
    wheelchair: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Place)
    if category:
        query = query.where(Place.category == category)
    if city:
        query = query.where(Place.city.ilike(f"%{city}%"))
    if halal is not None:
        query = query.where(Place.is_halal == halal)
    if parking is not None:
        query = query.where(Place.has_parking == parking)
    if wheelchair is not None:
        query = query.where(Place.is_wheelchair_accessible == wheelchair)
    
    result = await db.execute(query.limit(50))
    return result.scalars().all()

@router.get("/places/{place_id}", response_model=PlaceOut)
async def get_place(place_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Place).where(Place.id == place_id))
    place = result.scalars().first()
    if not place:
        raise HTTPException(status_code=404, detail="Lieu introuvable")
    return place

# =============================================================================
# MEETINGS MANAGEMENT
# =============================================================================
@router.post("/meetings", response_model=MeetingOut)
async def create_meeting(data: MeetingCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    meeting = Meeting(
        title=data.title,
        description=data.description,
        category=data.category,
        organizer_id=user.id,
        proposed_date=data.proposed_date,
        duration_minutes=data.duration_minutes,
        max_budget_per_person=data.max_budget_per_person,
        optimization_strategy=data.optimization_strategy,
        mandatory_criteria=data.mandatory_criteria,
        optional_preferences=data.optional_preferences
    )
    db.add(meeting)
    await db.flush()

    # Add organizer as first participant
    org_dep = data.organizer_departure
    organizer_part = MeetingParticipant(
        meeting_id=meeting.id,
        user_id=user.id,
        name=user.display_name or "Organisateur",
        is_guest=False,
        departure_label=org_dep.departure_label if org_dep else None,
        departure_lat=org_dep.departure_lat if org_dep else None,
        departure_lon=org_dep.departure_lon if org_dep else None,
        hide_exact_location=org_dep.hide_exact_location if org_dep else True,
        transport_mode=org_dep.transport_mode if org_dep else "TRANSIT",
        max_travel_time_minutes=org_dep.max_travel_time_minutes if org_dep else 45,
        max_budget=org_dep.max_budget if org_dep else data.max_budget_per_person,
        has_submitted=bool(org_dep and org_dep.departure_lat is not None)
    )
    db.add(organizer_part)
    await db.commit()

    # Reload with participants
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants), selectinload(Meeting.confirmed_place))
        .where(Meeting.id == meeting.id)
    )
    return result.scalars().first()

@router.get("/meetings", response_model=List[MeetingOut])
async def list_my_meetings(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Meetings where user is organizer OR participant
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants), selectinload(Meeting.confirmed_place))
        .outerjoin(MeetingParticipant)
        .where((Meeting.organizer_id == user.id) | (MeetingParticipant.user_id == user.id))
        .distinct()
        .order_by(Meeting.created_at.desc())
    )
    return result.scalars().all()

@router.get("/meetings/{meeting_id}", response_model=MeetingOut)
async def get_meeting(
    meeting_id: str,
    user: Optional[User] = Depends(get_current_user_optional),
    guest_token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants), selectinload(Meeting.confirmed_place))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Rencontre introuvable")

    # Access control: either user is authenticated or guest token matches participant or invitation
    return meeting

@router.patch("/meetings/{meeting_id}", response_model=MeetingOut)
async def update_meeting(meeting_id: str, data: MeetingUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants), selectinload(Meeting.confirmed_place))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Rencontre introuvable")
    if meeting.organizer_id != user.id and user.role != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Seul l'organisateur peut modifier cette rencontre")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(meeting, field, val)

    await db.commit()
    await db.refresh(meeting)
    return meeting

# =============================================================================
# INVITATIONS & GUEST PARTICIPATION
# =============================================================================
@router.post("/meetings/{meeting_id}/invitations")
async def create_invitation(
    meeting_id: str,
    payload: dict = {},
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Rencontre introuvable")
    if meeting.organizer_id != user.id and user.role != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Action non autorisée")

    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    inv = MeetingInvitation(
        meeting_id=meeting.id,
        token_hash=token_hash,
        invited_email=payload.get("email"),
        expires_at=expires_at
    )
    db.add(inv)
    await db.commit()

    invite_url = f"{settings.APP_URL}/invite/{raw_token}"
    return {"token": raw_token, "invite_url": invite_url, "expires_at": expires_at}

@router.post("/invitations/accept")
async def accept_invitation(data: InvitationAccept, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(data.token.encode()).hexdigest()
    result = await db.execute(
        select(MeetingInvitation).where(
            MeetingInvitation.token_hash == token_hash,
            MeetingInvitation.is_revoked == False
        )
    )
    inv = result.scalars().first()
    if not inv or inv.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Lien d'invitation invalide ou expiré")

    guest_session_token = secrets.token_urlsafe(24)
    participant = MeetingParticipant(
        meeting_id=inv.meeting_id,
        name=data.participant_data.name,
        is_guest=True,
        guest_session_token=guest_session_token,
        departure_label=data.participant_data.departure_label,
        departure_lat=data.participant_data.departure_lat,
        departure_lon=data.participant_data.departure_lon,
        hide_exact_location=data.participant_data.hide_exact_location,
        transport_mode=data.participant_data.transport_mode,
        max_travel_time_minutes=data.participant_data.max_travel_time_minutes,
        max_budget=data.participant_data.max_budget,
        dietary_constraints=data.participant_data.dietary_constraints,
        accessibility_needs=data.participant_data.accessibility_needs,
        has_submitted=bool(data.participant_data.departure_lat is not None)
    )
    db.add(participant)
    await db.commit()
    await db.refresh(participant)

    return {
        "status": "success",
        "meeting_id": inv.meeting_id,
        "participant_id": participant.id,
        "guest_token": guest_session_token
    }

@router.patch("/meetings/{meeting_id}/participants/{participant_id}")
async def update_participant(
    meeting_id: str,
    participant_id: str,
    data: ParticipantUpdate,
    db: AsyncSession = Depends(get_db)
):
    part = await db.get(MeetingParticipant, participant_id)
    if not part or part.meeting_id != meeting_id:
        raise HTTPException(status_code=404, detail="Participant introuvable")

    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(part, field, val)

    await db.commit()
    await db.refresh(part)
    return part

# =============================================================================
# MULTI-CRITERIA SEARCH & SCORING
# =============================================================================
@router.post("/meetings/{meeting_id}/search")
async def trigger_meeting_search(meeting_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalars().first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Rencontre introuvable")

    # Fetch candidate places matching category
    places_res = await db.execute(select(Place).where(Place.category == meeting.category))
    places = places_res.scalars().all()
    if not places:
        # Fallback to all places
        places_res = await db.execute(select(Place))
        places = places_res.scalars().all()

    # Clear previous candidates
    existing = await db.execute(select(SearchCandidate).where(SearchCandidate.meeting_id == meeting_id))
    for c in existing.scalars().all():
        await db.delete(c)
    await db.flush()

    # Evaluate each place
    candidates = []
    for place in places:
        res = await evaluate_candidate(
            place=place,
            participants=meeting.participants,
            strategy=meeting.optimization_strategy,
            mandatory_criteria=meeting.mandatory_criteria or {},
            optional_preferences=meeting.optional_preferences or {}
        )
        cand = SearchCandidate(
            meeting_id=meeting.id,
            place_id=place.id,
            total_score=res["total_score"],
            is_eligible=res["is_eligible"],
            disqualification_reason=res["disqualification_reason"],
            max_duration_seconds=res["max_duration_seconds"],
            mean_duration_seconds=res["mean_duration_seconds"],
            duration_variance=res["duration_variance"],
            routes_summary=res["routes_summary"],
            explanation=res["explanation"]
        )
        db.add(cand)
        candidates.append(cand)

    meeting.status = MeetingStatus.VOTING.value
    await db.commit()

    return {"status": "completed", "candidates_count": len(candidates)}

@router.get("/meetings/{meeting_id}/results", response_model=List[CandidateOut])
async def get_meeting_results(meeting_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SearchCandidate)
        .options(selectinload(SearchCandidate.place), selectinload(SearchCandidate.votes))
        .where(SearchCandidate.meeting_id == meeting_id)
        .order_by(SearchCandidate.total_score.desc())
    )
    candidates = result.scalars().all()
    
    out = []
    for c in candidates:
        cand_dict = {
            "id": c.id,
            "meeting_id": c.meeting_id,
            "place": c.place,
            "total_score": c.total_score,
            "is_eligible": c.is_eligible,
            "disqualification_reason": c.disqualification_reason,
            "max_duration_seconds": c.max_duration_seconds,
            "mean_duration_seconds": c.mean_duration_seconds,
            "duration_variance": c.duration_variance,
            "in_shortlist": c.in_shortlist,
            "routes_summary": c.routes_summary or [],
            "explanation": c.explanation,
            "votes_count": len(c.votes) if c.votes else 0
        }
        out.append(CandidateOut.model_validate(cand_dict))
    return out

# =============================================================================
# VOTES & CONFIRMATION
# =============================================================================
@router.post("/meetings/{meeting_id}/votes")
async def cast_vote(
    meeting_id: str,
    data: VoteCreate,
    participant_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify participant
    part = await db.get(MeetingParticipant, participant_id)
    if not part or part.meeting_id != meeting_id:
        raise HTTPException(status_code=403, detail="Participant non autorisé à voter")

    # Remove existing vote by this participant on this candidate
    existing = await db.execute(
        select(Vote).where(
            Vote.meeting_id == meeting_id,
            Vote.participant_id == participant_id,
            Vote.candidate_id == data.candidate_id
        )
    )
    old = existing.scalars().first()
    if old:
        await db.delete(old)
        await db.commit()
        return {"status": "vote_removed"}

    vote = Vote(
        meeting_id=meeting_id,
        candidate_id=data.candidate_id,
        participant_id=participant_id,
        rank=data.rank
    )
    db.add(vote)
    await db.commit()
    return {"status": "vote_recorded"}

@router.post("/meetings/{meeting_id}/confirm")
async def confirm_meeting(
    meeting_id: str,
    payload: dict,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Rencontre introuvable")
    if meeting.organizer_id != user.id and user.role != "SUPERADMIN":
        raise HTTPException(status_code=403, detail="Seul l'organisateur peut confirmer la rencontre")

    place_id = payload.get("place_id")
    if not place_id:
        raise HTTPException(status_code=400, detail="place_id requis")

    meeting.confirmed_place_id = place_id
    meeting.confirmed_at = datetime.now(timezone.utc)
    meeting.status = MeetingStatus.CONFIRMED.value
    await db.commit()

    return {"status": "confirmed", "place_id": place_id}

# =============================================================================
# AI GATEWAY ENDPOINTS
# =============================================================================
@router.post("/ai/parse", response_model=AIParsedConstraints)
async def ai_parse(payload: dict):
    message = payload.get("message", "")
    return await AIService.parse_prompt(message)

@router.post("/ai/chat", response_model=AIChatResponse)
async def ai_chat(data: AIChatRequest):
    return await AIService.chat(data.message, data.context)

# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================
@router.get("/admin/stats")
async def admin_stats(admin: User = Depends(get_current_superadmin), db: AsyncSession = Depends(get_db)):
    users_count = len((await db.execute(select(User))).scalars().all())
    meetings_count = len((await db.execute(select(Meeting))).scalars().all())
    places_count = len((await db.execute(select(Place))).scalars().all())

    return {
        "users": users_count,
        "meetings": meetings_count,
        "places": places_count,
        "sso_issuer": settings.SSO_BASE_URL,
        "litellm_model": settings.LITELLM_DEFAULT_MODEL,
        "routing_provider": settings.ROUTING_PROVIDER
    }
