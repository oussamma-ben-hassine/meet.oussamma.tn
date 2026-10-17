import json
import logging
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.schemas.schemas import AIParsedConstraints, AIChatResponse

logger = logging.getLogger(__name__)

PARSE_SYSTEM_PROMPT = """Tu es l'assistant IA intelligent de MeetSpot (écosystème oussamma.tn).
Ta mission est d'extraire des contraintes structurées à partir de la demande de l'utilisateur pour une rencontre entre amis.
Tu dois répondre STRICTEMENT sous forme d'un objet JSON valide contenant les clés suivantes :
- category: type de lieu ("restaurant", "cafe", "tea_room", "park", "bar", "coworking", "activity")
- budget_max: nombre flottant ou null
- max_duration_minutes: nombre entier en minutes ou null
- mandatory_criteria: dictionnaire avec clés booléennes possibles (ex: "halal", "parking", "wheelchair", "terrace")
- optional_preferences: dictionnaire avec clés booléennes ou textes
- participants_locations: liste d'objets avec {"label": str, "address": str, "count": int}
- missing_information: liste des informations indispensables encore manquantes
- summary: résumé chaleureux et clair des critères compris

Exemple utilisateur :
"On est cinq, deux à Argenteuil, un à Créteil et deux à Versailles. On veut un restaurant halal avec parking, vendredi soir, moins de 30 € et maximum 40 minutes par personne."

Exemple de sortie JSON :
{
  "category": "restaurant",
  "budget_max": 30.0,
  "max_duration_minutes": 40,
  "mandatory_criteria": {"halal": true, "parking": true},
  "optional_preferences": {},
  "participants_locations": [
    {"label": "Argenteuil", "address": "Argenteuil, France", "count": 2},
    {"label": "Créteil", "address": "Créteil, France", "count": 1},
    {"label": "Versailles", "address": "Versailles, France", "count": 2}
  ],
  "missing_information": [],
  "summary": "Recherche d'un restaurant halal avec parking pour 5 personnes réparties entre Argenteuil, Créteil et Versailles, budget max 30€/personne et temps de trajet max de 40 min."
}
"""

class AIService:
    @staticmethod
    async def parse_prompt(message: str) -> AIParsedConstraints:
        """Call LiteLLM to extract structured filters, with deterministic fallback."""
        url = f"{settings.LITELLM_BASE_URL.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.LITELLM_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": settings.LITELLM_DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": PARSE_SYSTEM_PROMPT},
                {"role": "user", "content": message}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    return AIParsedConstraints(**parsed)
                else:
                    logger.warning(f"LiteLLM call failed with status {res.status_code}: {res.text}")
        except Exception as e:
            logger.error(f"Error calling LiteLLM: {str(e)}")

        # Graceful fallback without breaking execution
        is_halal = "halal" in message.lower()
        has_parking = "parking" in message.lower()
        has_terrace = "terrasse" in message.lower()
        
        return AIParsedConstraints(
            category="restaurant" if "resto" in message.lower() or "restaurant" in message.lower() else "cafe",
            budget_max=35.0 if "€" in message or "euro" in message.lower() else None,
            max_duration_minutes=45,
            mandatory_criteria={"halal": is_halal, "parking": has_parking, "terrace": has_terrace},
            optional_preferences={},
            participants_locations=[],
            missing_information=["Points de départ précis des participants"],
            summary=f"Demande analysée : critères détectés (Halal: {is_halal}, Parking: {has_parking}). Précisez les adresses de départ pour un calcul optimal."
        )

    @staticmethod
    async def chat(message: str, context: Optional[Dict[str, Any]] = None) -> AIChatResponse:
        """Interactive conversational guidance for meeting organization."""
        parsed = await AIService.parse_prompt(message)
        
        reply = (
            f"J'ai bien noté vos critères pour cette rencontre !\n\n"
            f"📍 **Catégorie** : {parsed.category}\n"
            f"⏱️ **Temps max** : {parsed.max_duration_minutes or 'Non spécifié'} min\n"
            f"💶 **Budget max** : {parsed.budget_max or 'Libre'} €/pers\n"
            f"✨ **Critères obligatoires** : {', '.join([k for k, v in parsed.mandatory_criteria.items() if v]) or 'Aucun'}\n\n"
            f"{parsed.summary}"
        )
        
        actions = ["Lancer la recherche", "Modifier les participants", "Ajouter un critère"]
        return AIChatResponse(
            reply=reply,
            parsed_filters=parsed,
            suggested_actions=actions
        )
