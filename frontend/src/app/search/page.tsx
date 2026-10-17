'use client';

import React, { useEffect, useState } from 'react';
import { Search, MapPin, SlidersHorizontal, Star, ExternalLink, ShieldCheck } from 'lucide-react';
import InteractiveMap from '@/components/map/InteractiveMap';
import { Place } from '@/types';

export default function IndividualSearchPage() {
  const [places, setPlaces] = useState<Place[]>([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [halal, setHalal] = useState(false);
  const [parking, setParking] = useState(false);
  const [wheelchair, setWheelchair] = useState(false);

  const fetchPlaces = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (category) params.set('category', category);
      if (halal) params.set('halal', 'true');
      if (parking) params.set('parking', 'true');
      if (wheelchair) params.set('wheelchair', 'true');

      const res = await fetch(`/api/v1/places?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setPlaces(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPlaces();
  }, [category, halal, parking, wheelchair]);

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h1 className="text-3xl font-black mb-2">Recherche individuelle de lieux</h1>
        <p className="text-sm text-neutral-400">
          Explorez le catalogue des cafés, restaurants et parcs vérifiés avec filtres stricts.
        </p>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-2xl bg-[#121212] border border-white/10 flex flex-wrap items-center gap-4 text-xs">
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="bg-black/50 border border-white/10 rounded-xl px-3 py-2 text-white focus:outline-none focus:border-[#ea580c]"
        >
          <option value="">Toutes catégories</option>
          <option value="restaurant">Restaurants</option>
          <option value="cafe">Cafés</option>
          <option value="park">Parcs</option>
        </select>

        <label className="flex items-center gap-1.5 cursor-pointer text-neutral-300">
          <input
            type="checkbox"
            checked={halal}
            onChange={(e) => setHalal(e.target.checked)}
            className="rounded text-[#ea580c]"
          />
          Halal uniquement
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer text-neutral-300">
          <input
            type="checkbox"
            checked={parking}
            onChange={(e) => setParking(e.target.checked)}
            className="rounded text-[#ea580c]"
          />
          Avec Parking
        </label>

        <label className="flex items-center gap-1.5 cursor-pointer text-neutral-300">
          <input
            type="checkbox"
            checked={wheelchair}
            onChange={(e) => setWheelchair(e.target.checked)}
            className="rounded text-[#ea580c]"
          />
          Accès PMR
        </label>
      </div>

      {/* Grid: Places & Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-4">
          {loading ? (
            <div className="p-10 text-center text-neutral-500">Chargement...</div>
          ) : places.length === 0 ? (
            <div className="p-10 text-center text-neutral-500 rounded-2xl bg-[#121212] border border-white/10">
              Aucun lieu correspondant aux filtres stricts.
            </div>
          ) : (
            places.map((place) => (
              <div
                key={place.id}
                className="p-5 rounded-2xl bg-[#121212] border border-white/10 hover:border-white/20 transition-all flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-white/10 text-[#ea580c]">
                        {place.category}
                      </span>
                      <h3 className="text-lg font-bold text-white mt-1">{place.name}</h3>
                      <p className="text-xs text-neutral-400 mt-0.5">{place.address}</p>
                    </div>
                    <span className="text-xs font-mono font-bold px-2 py-1 rounded bg-black/40 border border-white/10">
                      {place.estimated_price_eur ? `~${place.estimated_price_eur}€` : 'Prix moyen'}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2 mt-4 text-[11px] text-neutral-400 font-mono">
                    {place.is_halal && <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400">✓ Halal</span>}
                    {place.has_parking && <span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400">✓ Parking</span>}
                    {place.has_terrace && <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400">✓ Terrasse</span>}
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-xs">
                  <span className="text-neutral-500">Données vérifiées OSM</span>
                  <a
                    href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.address)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[#f97316] hover:underline"
                  >
                    Ouvrir sur la carte
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>
            ))
          )}
        </div>

        <div className="sticky top-24 h-[550px]">
          <InteractiveMap
            places={places.map((p) => ({
              id: p.id,
              name: p.name,
              latitude: p.latitude,
              longitude: p.longitude,
            }))}
          />
        </div>
      </div>
    </div>
  );
}
