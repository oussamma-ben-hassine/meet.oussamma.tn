import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, Table, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

def gen_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    USER = "USER"
    GUEST = "GUEST"

class MeetingStatus(str, Enum):
    DRAFT = "DRAFT"
    COLLECTING = "COLLECTING"
    SEARCHING = "SEARCHING"
    VOTING = "VOTING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    ARCHIVED = "ARCHIVED"

class TransportMode(str, Enum):
    DRIVING = "DRIVING"
    WALKING = "WALKING"
    CYCLING = "CYCLING"
    TRANSIT = "TRANSIT"

class OptimizationStrategy(str, Enum):
    MINIMAX = "MINIMAX"
    TOTAL = "TOTAL"
    BALANCED = "BALANCED"
    BUDGET = "BUDGET"
    CUSTOM = "CUSTOM"

# 1. USERS
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, index=True, nullable=True)
    display_name = Column(String(255), nullable=False)
    avatar_url = Column(String(512), nullable=True)
    role = Column(String(50), default=UserRole.USER.value, nullable=False)
    sso_sub = Column(String(255), unique=True, index=True, nullable=True)
    sso_issuer = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    saved_locations = relationship("SavedLocation", back_populates="user", cascade="all, delete-orphan")
    organized_meetings = relationship("Meeting", back_populates="organizer", cascade="all, delete-orphan")
    participations = relationship("MeetingParticipant", back_populates="user")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")

# 2. USER PREFERENCES
class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    default_city = Column(String(100), nullable=True)
    default_transport_mode = Column(String(50), default=TransportMode.TRANSIT.value)
    default_budget = Column(Float, nullable=True)
    dietary_preferences = Column(JSON, default=list)  # ["halal", "vegetarian", etc.]
    accessibility_needs = Column(JSON, default=list) # ["wheelchair", "step_free"]
    preferred_categories = Column(JSON, default=list)
    language = Column(String(10), default="fr")
    theme = Column(String(20), default="dark")
    share_exact_location = Column(Boolean, default=False)

    user = relationship("User", back_populates="preferences")

# 3. SAVED LOCATIONS
class SavedLocation(Base):
    __tablename__ = "saved_locations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    label = Column(String(100), nullable=False)  # Maison, Travail, Bureau...
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="saved_locations")

# 4. MEETINGS
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="restaurant")
    status = Column(String(50), default=MeetingStatus.COLLECTING.value, nullable=False)
    organizer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    proposed_date = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=120)
    max_budget_per_person = Column(Float, nullable=True)
    optimization_strategy = Column(String(50), default=OptimizationStrategy.BALANCED.value)
    
    # Final chosen place if confirmed
    confirmed_place_id = Column(String(36), ForeignKey("places.id", ondelete="SET NULL"), nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Settings & criteria
    mandatory_criteria = Column(JSON, default=dict) # e.g. {"halal": true, "parking": true}
    optional_preferences = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organizer = relationship("User", back_populates="organized_meetings")
    participants = relationship("MeetingParticipant", back_populates="meeting", cascade="all, delete-orphan")
    invitations = relationship("MeetingInvitation", back_populates="meeting", cascade="all, delete-orphan")
    candidates = relationship("SearchCandidate", back_populates="meeting", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="meeting", cascade="all, delete-orphan")
    confirmed_place = relationship("Place", foreign_keys=[confirmed_place_id])

# 5. MEETING INVITATIONS
class MeetingInvitation(Base):
    __tablename__ = "meeting_invitations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(String(255), unique=True, index=True, nullable=False)
    invited_email = Column(String(255), nullable=True)
    is_revoked = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    meeting = relationship("Meeting", back_populates="invitations")

# 6. MEETING PARTICIPANTS
class MeetingParticipant(Base):
    __tablename__ = "meeting_participants"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Guest or logged in display name
    name = Column(String(255), nullable=False)
    is_guest = Column(Boolean, default=False)
    guest_session_token = Column(String(255), nullable=True) # for guest authentication
    
    # Departure point
    departure_label = Column(String(255), nullable=True)
    departure_lat = Column(Float, nullable=True)
    departure_lon = Column(Float, nullable=True)
    hide_exact_location = Column(Boolean, default=True)
    
    # Constraints
    transport_mode = Column(String(50), default=TransportMode.TRANSIT.value)
    max_travel_time_minutes = Column(Integer, default=45)
    max_budget = Column(Float, nullable=True)
    dietary_constraints = Column(JSON, default=list)
    accessibility_needs = Column(JSON, default=list)
    has_submitted = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="participations")

# 7. PLACES (Catalog & Candidates)
class Place(Base):
    __tablename__ = "places"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    provider_id = Column(String(100), nullable=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    address = Column(String(512), nullable=False)
    city = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    
    phone = Column(String(50), nullable=True)
    website = Column(String(512), nullable=True)
    booking_url = Column(String(512), nullable=True)
    price_level = Column(Integer, default=2) # 1 ($), 2 ($$), 3 ($$$), 4 ($$$$)
    estimated_price_eur = Column(Float, nullable=True)
    
    # Specific attributes verified
    is_halal = Column(Boolean, nullable=True)
    has_terrace = Column(Boolean, nullable=True)
    has_parking = Column(Boolean, nullable=True)
    is_wheelchair_accessible = Column(Boolean, nullable=True)
    has_wifi = Column(Boolean, nullable=True)
    is_quiet = Column(Boolean, nullable=True)
    
    opening_hours = Column(JSON, default=dict)
    photos = Column(JSON, default=list)
    source_attribution = Column(String(255), default="OpenStreetMap / Curated")
    
    created_at = Column(DateTime(timezone=True), default=utc_now)

    favorites = relationship("Favorite", back_populates="place")

# 8. SEARCH CANDIDATES & RANKING
class SearchCandidate(Base):
    __tablename__ = "search_candidates"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    
    total_score = Column(Float, default=0.0)
    is_eligible = Column(Boolean, default=True)
    disqualification_reason = Column(String(255), nullable=True)
    
    # Metrics
    max_duration_seconds = Column(Integer, default=0)
    mean_duration_seconds = Column(Float, default=0.0)
    duration_variance = Column(Float, default=0.0)
    in_shortlist = Column(Boolean, default=False)
    
    # Trait details per participant: [{participant_id, duration_sec, distance_m, mode}]
    routes_summary = Column(JSON, default=list)
    explanation = Column(Text, nullable=True)
    
    meeting = relationship("Meeting", back_populates="candidates")
    place = relationship("Place")
    votes = relationship("Vote", back_populates="candidate")

# 9. VOTES
class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    meeting_id = Column(String(36), ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False)
    candidate_id = Column(String(36), ForeignKey("search_candidates.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(String(36), ForeignKey("meeting_participants.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    meeting = relationship("Meeting", back_populates="votes")
    candidate = relationship("SearchCandidate", back_populates="votes")

# 10. FAVORITES
class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    place_id = Column(String(36), ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="favorites")
    place = relationship("Place", back_populates="favorites")

# 11. AI CONVERSATIONS & AUDIT
class AIConversation(Base):
    __tablename__ = "ai_conversations"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(String(255), index=True)
    messages = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AppSetting(Base):
    __tablename__ = "app_settings"

    key = Column(String(100), primary_key=True)
    value = Column(JSON, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
