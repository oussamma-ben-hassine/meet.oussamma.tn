import pytest
from app.models.models import Place, MeetingParticipant
from app.services.scoring import check_mandatory_constraints, evaluate_candidate

@pytest.mark.asyncio
async def test_mandatory_halal_constraint():
    halal_place = Place(
        id="1", name="Halal Grill", category="restaurant",
        address="Paris", latitude=48.85, longitude=2.35, is_halal=True
    )
    non_halal_place = Place(
        id="2", name="Pork Bistrot", category="restaurant",
        address="Paris", latitude=48.85, longitude=2.35, is_halal=False
    )
    
    p = MeetingParticipant(
        id="p1", meeting_id="m1", name="Karim",
        dietary_constraints=["halal"], departure_lat=48.85, departure_lon=2.30
    )
    
    ok1, _ = check_mandatory_constraints(halal_place, {"halal": True}, [p])
    assert ok1 is True
    
    ok2, reason = check_mandatory_constraints(non_halal_place, {"halal": True}, [p])
    assert ok2 is False
    assert "Halal" in reason

@pytest.mark.asyncio
async def test_minimax_scoring():
    place = Place(
        id="1", name="Central Spot", category="cafe",
        address="Chatelet", latitude=48.8584, longitude=2.3470,
        is_halal=True, has_terrace=True, price_level=2
    )
    p1 = MeetingParticipant(
        id="p1", meeting_id="m1", name="Alice",
        departure_lat=48.8600, departure_lon=2.3400, max_travel_time_minutes=45
    )
    p2 = MeetingParticipant(
        id="p2", meeting_id="m1", name="Bob",
        departure_lat=48.8500, departure_lon=2.3500, max_travel_time_minutes=45
    )
    
    eval_res = await evaluate_candidate(
        place=place,
        participants=[p1, p2],
        strategy="MINIMAX",
        mandatory_criteria={},
        optional_preferences={"has_terrace": True}
    )
    
    assert eval_res["is_eligible"] is True
    assert eval_res["total_score"] > 80.0
    assert len(eval_res["routes_summary"]) == 2
