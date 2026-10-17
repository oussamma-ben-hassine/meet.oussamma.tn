from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.models import Place

SEED_PLACES = [
    {
        "name": "Le Comptoir de Châtelet",
        "category": "restaurant",
        "address": "12 Rue Saint-Denis, 75001 Paris",
        "city": "Paris",
        "latitude": 48.8584,
        "longitude": 2.3470,
        "phone": "+33 1 42 33 00 11",
        "price_level": 2,
        "estimated_price_eur": 25.0,
        "is_halal": True,
        "has_terrace": True,
        "has_parking": False,
        "is_wheelchair_accessible": True,
        "has_wifi": True,
        "is_quiet": False,
        "photos": ["https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600"]
    },
    {
        "name": "Café de la Défense Hub",
        "category": "cafe",
        "address": "1 Esplanade de la Défense, 92400 Courbevoie",
        "city": "Courbevoie",
        "latitude": 48.8918,
        "longitude": 2.2415,
        "phone": "+33 1 47 78 99 22",
        "price_level": 2,
        "estimated_price_eur": 18.0,
        "is_halal": True,
        "has_terrace": True,
        "has_parking": True,
        "is_wheelchair_accessible": True,
        "has_wifi": True,
        "is_quiet": True,
        "photos": ["https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600"]
    },
    {
        "name": "L'Oasis Berbère & Grill",
        "category": "restaurant",
        "address": "45 Avenue de Saint-Mandé, 75012 Paris",
        "city": "Paris",
        "latitude": 48.8450,
        "longitude": 2.3990,
        "phone": "+33 1 43 45 12 34",
        "price_level": 2,
        "estimated_price_eur": 28.0,
        "is_halal": True,
        "has_terrace": False,
        "has_parking": True,
        "is_wheelchair_accessible": True,
        "has_wifi": True,
        "is_quiet": True,
        "photos": ["https://images.unsplash.com/photo-1544025162-d76694265947?w=600"]
    },
    {
        "name": "Parc Floral & Salon de Thé",
        "category": "park",
        "address": "Route de la Pyramide, 75012 Paris",
        "city": "Paris",
        "latitude": 48.8385,
        "longitude": 2.4430,
        "phone": "+33 1 55 94 20 00",
        "price_level": 1,
        "estimated_price_eur": 10.0,
        "is_halal": True,
        "has_terrace": True,
        "has_parking": True,
        "is_wheelchair_accessible": True,
        "has_wifi": False,
        "is_quiet": True,
        "photos": ["https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600"]
    },
    {
        "name": "Bistrot Montparnasse 360",
        "category": "restaurant",
        "address": "22 Boulevard du Montparnasse, 75015 Paris",
        "city": "Paris",
        "latitude": 48.8421,
        "longitude": 2.3195,
        "phone": "+33 1 45 67 89 01",
        "price_level": 3,
        "estimated_price_eur": 42.0,
        "is_halal": False,
        "has_terrace": True,
        "has_parking": True,
        "is_wheelchair_accessible": True,
        "has_wifi": True,
        "is_quiet": False,
        "photos": ["https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c?w=600"]
    }
]

async def seed_places(db: AsyncSession):
    result = await db.execute(select(Place))
    existing = result.scalars().all()
    if not existing:
        for p_data in SEED_PLACES:
            p = Place(**p_data)
            db.add(p)
        await db.commit()
