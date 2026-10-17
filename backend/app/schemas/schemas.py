from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# User Schemas
class UserBase(BaseModel):
    email: Optional[str] = None
    display_name: str
    avatar_url: Optional[str] = None
    role: str = "USER"

class UserCreate(UserBase):
    sso_sub: Optional[str] = None
    sso_issuer: Optional[str] = None

class UserOut(UserBase):
    id: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class UserPreferenceSchema(BaseModel):
    default_city: Optional[str] = None
    default_transport_mode: str = "TRANSIT"
    default_budget: Optional[float] = None
    dietary_preferences: List[str] = []
    accessibility_needs: List[str] = []
    preferred_categories: List[str] = []
    language: str = "fr"
    theme: str = "dark"
    share_exact_location: bool = False
    class Config:
        from_attributes = True

# Place Schemas
class PlaceBase(BaseModel):
    name: str
    category: str
    address: str
    city: Optional[str] = None
    latitude: float
    longitude: float
    phone: Optional[str] = None
    website: Optional[str] = None
    booking_url: Optional[str] = None
    price_level: int = 2
    estimated_price_eur: Optional[float] = None
    is_halal: Optional[bool] = None
    has_terrace: Optional[bool] = None
    has_parking: Optional[bool] = None
    is_wheelchair_accessible: Optional[bool] = None
    has_wifi: Optional[bool] = None
    is_quiet: Optional[bool] = None
    opening_hours: Dict[str, Any] = {}
    photos: List[str] = []
    source_attribution: str = "OpenStreetMap / Curated"

class PlaceOut(PlaceBase):
    id: str
    class Config:
        from_attributes = True

# Participant Schemas
class ParticipantCreate(BaseModel):
    name: str
    departure_label: Optional[str] = None
    departure_lat: Optional[float] = None
    departure_lon: Optional[float] = None
    hide_exact_location: bool = True
    transport_mode: str = "TRANSIT"
    max_travel_time_minutes: int = 45
    max_budget: Optional[float] = None
    dietary_constraints: List[str] = []
    accessibility_needs: List[str] = []

class ParticipantUpdate(BaseModel):
    name: Optional[str] = None
    departure_label: Optional[str] = None
    departure_lat: Optional[float] = None
    departure_lon: Optional[float] = None
    hide_exact_location: Optional[bool] = None
    transport_mode: Optional[str] = None
    max_travel_time_minutes: Optional[int] = None
    max_budget: Optional[float] = None
    dietary_constraints: Optional[List[str]] = None
    accessibility_needs: Optional[List[str]] = None
    has_submitted: Optional[bool] = None

class ParticipantOut(BaseModel):
    id: str
    meeting_id: str
    user_id: Optional[str] = None
    name: str
    is_guest: bool
    departure_label: Optional[str] = None
    # If hide_exact_location is True and not requested by the participant themselves, lat/lon masked
    departure_lat: Optional[float] = None
    departure_lon: Optional[float] = None
    hide_exact_location: bool
    transport_mode: str
    max_travel_time_minutes: int
    max_budget: Optional[float] = None
    dietary_constraints: List[str] = []
    accessibility_needs: List[str] = []
    has_submitted: bool
    class Config:
        from_attributes = True

# Meeting Schemas
class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: str = "restaurant"
    proposed_date: Optional[datetime] = None
    duration_minutes: int = 120
    max_budget_per_person: Optional[float] = None
    optimization_strategy: str = "BALANCED" # MINIMAX, TOTAL, BALANCED, BUDGET, CUSTOM
    mandatory_criteria: Dict[str, Any] = {}
    optional_preferences: Dict[str, Any] = {}
    organizer_departure: Optional[ParticipantCreate] = None

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    proposed_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    max_budget_per_person: Optional[float] = None
    optimization_strategy: Optional[str] = None
    mandatory_criteria: Optional[Dict[str, Any]] = None
    optional_preferences: Optional[Dict[str, Any]] = None

class MeetingOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    status: str
    organizer_id: str
    proposed_date: Optional[datetime] = None
    duration_minutes: int
    max_budget_per_person: Optional[float] = None
    optimization_strategy: str
    confirmed_place_id: Optional[str] = None
    confirmed_place: Optional[PlaceOut] = None
    confirmed_at: Optional[datetime] = None
    mandatory_criteria: Dict[str, Any] = {}
    optional_preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    participants: List[ParticipantOut] = []
    class Config:
        from_attributes = True

# Search & Candidate Schemas
class CandidateOut(BaseModel):
    id: str
    meeting_id: str
    place: PlaceOut
    total_score: float
    is_eligible: bool
    disqualification_reason: Optional[str] = None
    max_duration_seconds: int
    mean_duration_seconds: float
    duration_variance: float
    in_shortlist: bool
    routes_summary: List[Dict[str, Any]] = []
    explanation: Optional[str] = None
    votes_count: int = 0
    class Config:
        from_attributes = True

# Vote Schemas
class VoteCreate(BaseModel):
    candidate_id: str
    rank: int = 1

class InvitationAccept(BaseModel):
    token: str
    participant_data: ParticipantCreate

# AI Schemas
class AIParsedConstraints(BaseModel):
    category: Optional[str] = "restaurant"
    budget_max: Optional[float] = None
    max_duration_minutes: Optional[int] = None
    mandatory_criteria: Dict[str, Any] = {}
    optional_preferences: Dict[str, Any] = {}
    participants_locations: List[Dict[str, Any]] = []
    missing_information: List[str] = []
    summary: str

class AIChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class AIChatResponse(BaseModel):
    reply: str
    parsed_filters: Optional[AIParsedConstraints] = None
    suggested_actions: List[str] = []
