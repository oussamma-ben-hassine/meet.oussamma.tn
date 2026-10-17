import math
from typing import List, Dict, Any, Tuple
from app.models.models import Place, MeetingParticipant, OptimizationStrategy
from app.services.routing import get_routing_provider

def check_mandatory_constraints(place: Place, mandatory: Dict[str, Any], participant_constraints: List[MeetingParticipant]) -> Tuple[bool, str]:
    """
    Check non-negotiable criteria. Returns (is_eligible, disqualification_reason).
    """
    # 1. Dietary / Halal
    req_halal = mandatory.get("halal", False)
    for p in participant_constraints:
        if "halal" in (p.dietary_constraints or []):
            req_halal = True
            break
            
    if req_halal and place.is_halal is False:
        return False, "Ne propose pas d'option Halal garantie"
        
    # 2. Wheelchair accessibility
    req_wheelchair = mandatory.get("wheelchair", False)
    for p in participant_constraints:
        if "wheelchair" in (p.accessibility_needs or []):
            req_wheelchair = True
            break
            
    if req_wheelchair and place.is_wheelchair_accessible is False:
        return False, "Lieu non accessible en fauteuil roulant"
        
    # 3. Terrace
    if mandatory.get("terrace", False) and place.has_terrace is False:
        return False, "Pas de terrasse disponible"

    # 4. Parking
    if mandatory.get("parking", False) and place.has_parking is False:
        return False, "Pas de parking à proximité"

    return True, ""

async def evaluate_candidate(
    place: Place,
    participants: List[MeetingParticipant],
    strategy: str,
    mandatory_criteria: Dict[str, Any],
    optional_preferences: Dict[str, Any]
) -> Dict[str, Any]:
    routing = get_routing_provider()
    
    # Check mandatory place attributes first
    eligible, reason = check_mandatory_constraints(place, mandatory_criteria, participants)
    if not eligible:
        return {
            "place": place,
            "is_eligible": False,
            "disqualification_reason": reason,
            "total_score": 0.0,
            "max_duration_seconds": 999999,
            "mean_duration_seconds": 999999,
            "duration_variance": 999999,
            "routes_summary": [],
            "explanation": reason
        }

    # Calculate travel times for each participant with valid coordinates
    valid_participants = [p for p in participants if p.departure_lat is not None and p.departure_lon is not None]
    
    if not valid_participants:
        return {
            "place": place,
            "is_eligible": True,
            "disqualification_reason": None,
            "total_score": 75.0,
            "max_duration_seconds": 0,
            "mean_duration_seconds": 0,
            "duration_variance": 0,
            "routes_summary": [],
            "explanation": "Aucun point de départ participant renseigné"
        }

    durations = []
    routes_summary = []
    
    for p in valid_participants:
        route = await routing.get_route(
            start_lat=p.departure_lat,
            start_lon=p.departure_lon,
            end_lat=place.latitude,
            end_lon=place.longitude,
            mode=p.transport_mode or "TRANSIT"
        )
        duration_sec = route["duration_seconds"]
        durations.append(duration_sec)
        
        # Check individual max travel time constraint
        max_allowed_sec = (p.max_travel_time_minutes or 60) * 60
        if duration_sec > max_allowed_sec:
            diff_min = int((duration_sec - max_allowed_sec) / 60)
            return {
                "place": place,
                "is_eligible": False,
                "disqualification_reason": f"Dépasse le temps maximum de {p.name} (+{diff_min} min)",
                "total_score": 0.0,
                "max_duration_seconds": max(durations) if durations else 0,
                "mean_duration_seconds": sum(durations)/len(durations) if durations else 0,
                "duration_variance": 0,
                "routes_summary": [],
                "explanation": f"Temps de trajet trop élevé pour {p.name}"
            }
            
        routes_summary.append({
            "participant_id": p.id,
            "participant_name": p.name,
            "duration_seconds": duration_sec,
            "distance_meters": route["distance_meters"],
            "mode": route["mode"],
            "geometry": route.get("geometry", [])
        })

    max_sec = max(durations)
    mean_sec = sum(durations) / len(durations)
    variance_sec = sum((d - mean_sec) ** 2 for d in durations) / len(durations)
    std_dev_sec = math.sqrt(variance_sec)

    # 10. Scoring formulas based on strategy
    # Time normalized score: 100 for 0 min, 0 for 90 min
    time_score_max = max(0.0, 100.0 - (max_sec / 54.0)) # 54s = 0.9 min => 90 min = 0
    time_score_mean = max(0.0, 100.0 - (mean_sec / 54.0))
    fairness_penalty = min(50.0, (std_dev_sec / 60.0) * 2.5) # penalize high disparity

    # Bonus for optional preferences
    preference_bonus = 0.0
    if optional_preferences.get("has_terrace") and place.has_terrace:
        preference_bonus += 5.0
    if optional_preferences.get("has_parking") and place.has_parking:
        preference_bonus += 5.0
    if optional_preferences.get("is_quiet") and place.is_quiet:
        preference_bonus += 5.0
    if optional_preferences.get("has_wifi") and place.has_wifi:
        preference_bonus += 3.0

    if strategy == OptimizationStrategy.MINIMAX.value:
        # Heavily prioritize minimizing the longest commute
        score = (time_score_max * 0.70) + (time_score_mean * 0.20) + preference_bonus
    elif strategy == OptimizationStrategy.TOTAL.value:
        # Prioritize total / average commute time
        score = (time_score_mean * 0.80) + (time_score_max * 0.10) + preference_bonus
    elif strategy == OptimizationStrategy.BALANCED.value:
        # Compromise: mean time minus unfairness between friends
        score = (time_score_mean * 0.50) + (time_score_max * 0.30) - fairness_penalty + preference_bonus
    elif strategy == OptimizationStrategy.BUDGET.value:
        # Factor in price level (1 is cheapest)
        price_factor = (5 - (place.price_level or 2)) * 5.0
        score = (time_score_mean * 0.45) + (time_score_max * 0.25) + price_factor + preference_bonus
    else:
        score = (time_score_mean * 0.5) + (time_score_max * 0.3) + preference_bonus

    score = round(max(0.0, min(100.0, score)), 1)
    
    max_min = round(max_sec / 60)
    mean_min = round(mean_sec / 60)
    explanation = f"Temps moyen de {mean_min} min (trajet max : {max_min} min). Score d'équité : {score}/100."

    return {
        "place": place,
        "is_eligible": True,
        "disqualification_reason": None,
        "total_score": score,
        "max_duration_seconds": max_sec,
        "mean_duration_seconds": mean_sec,
        "duration_variance": variance_sec,
        "routes_summary": routes_summary,
        "explanation": explanation
    }
