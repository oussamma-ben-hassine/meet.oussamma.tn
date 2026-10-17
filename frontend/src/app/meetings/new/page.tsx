'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Calendar, Clock, DollarSign, MapPin, Sliders, Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function NewMeetingPage() {
  const router = useRouter();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('restaurant');
  const [strategy, setStrategy] = useState('BALANCED');
  const [maxBudget, setMaxBudget] = useState<number | ''>(30);
  
  // Mandatory criteria
  const [halal, setHalal] = useState(false);
  const [parking, setParking] = useState(false);
  const [wheelchair, setWheelchair] = useState(false);
  const [terrace, setTerrace] = useState(false);

  // Organizer departure
  const [myLocation, setMyLocation] = useState('Châtelet, Paris');
  const [myLat, setMyLat] = useState(48.8584);
  const [myLon, setMyLon] = useState(2.3470);
  const [myTransport, setMyTransport] = useState('TRANSIT');
  const [myMaxTime, setMyMaxTime] = useState(45);

  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const payload = {
      title: title || 'Rencontre entre amis',
      description,
      category,
      max_budget_per_person: maxBudget === '' ? null : Number(maxBudget),
      optimization_strategy: strategy,
      mandatory_criteria: {
        halal,
        parking,
        wheelchair,
        terrace
      },
      optional_preferences: {},
      organizer_departure: {
        name: 'Moi (Organisateur)',
        departure_label: myLocation,
        departure_lat: myLat,
        departure_lon: myLon,
        transport_mode: myTransport,
        max_travel_time_minutes: myMaxTime,
        max_budget: maxBudget === '' ? null : Number(maxBudget),
        hide_exact_location: true
      }
    };

    try {
      const res = await fetch('/api/v1/meetings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const meeting = await res.json();
        router.push(`/meetings/${meeting.id}`);
      } else {
        alert("Erreur lors de la création de la rencontre.");
      }
    } catch (err) {
      console.error(err);
      alert("Erreur réseau");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-black mb-2">Créer une nouvelle rencontre</h1>
        <p className="text-sm text-neutral-400">
          Configurez votre projet de rencontre. Vous obtiendrez un lien d'invitation à envoyer à vos proches.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Basic info */}
        <div className="p-6 rounded-2xl bg-[#121212] border border-white/10 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Calendar className="w-5 h-5 text-[#ea580c]" />
            Détails de l'événement
          </h2>
          <div>
            <label className="block text-xs font-semibold text-neutral-400 mb-1">Titre de la rencontre</label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Dîner retrouvailles vendredi"
              className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-neutral-400 mb-1">Catégorie de lieu</label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
              >
                <option value="restaurant">Restaurant</option>
                <option value="cafe">Café / Salon de thé</option>
                <option value="park">Parc / Plein air</option>
                <option value="bar">Bar / Soirée</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-neutral-400 mb-1">Budget max estimé (€/pers)</label>
              <input
                type="number"
                value={maxBudget}
                onChange={(e) => setMaxBudget(e.target.value === '' ? '' : Number(e.target.value))}
                placeholder="Ex: 30"
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
              />
            </div>
          </div>
        </div>

        {/* Strategy */}
        <div className="p-6 rounded-2xl bg-[#121212] border border-white/10 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Sliders className="w-5 h-5 text-[#ea580c]" />
            Stratégie d'équité de calcul
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { id: 'BALANCED', name: 'Équilibré (Recommandé)', desc: 'Limite les écarts de temps entre tous.' },
              { id: 'MINIMAX', name: 'Minimax', desc: 'Minimise le trajet du plus éloigné.' },
              { id: 'TOTAL', name: 'Temps global', desc: 'Minimise la somme cumulée des trajets.' },
            ].map((strat) => (
              <div
                key={strat.id}
                onClick={() => setStrategy(strat.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  strategy === strat.id
                    ? 'border-[#ea580c] bg-[#ea580c]/10 text-white'
                    : 'border-white/10 bg-black/30 text-neutral-400 hover:border-white/20'
                }`}
              >
                <p className="font-bold text-sm text-white">{strat.name}</p>
                <p className="text-xs mt-1">{strat.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Mandatory constraints */}
        <div className="p-6 rounded-2xl bg-[#121212] border border-white/10 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Shield className="w-5 h-5 text-[#ea580c]" />
            Critères obligatoires stricts (Non négociables)
          </h2>
          <p className="text-xs text-neutral-400">
            Tout lieu ne validant pas ces critères sera immédiatement éliminé par le moteur.
          </p>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { id: 'halal', label: 'Halal garanti', checked: halal, set: setHalal },
              { id: 'parking', label: 'Parking à proximité', checked: parking, set: setParking },
              { id: 'wheelchair', label: 'Accès PMR', checked: wheelchair, set: setWheelchair },
              { id: 'terrace', label: 'Terrasse', checked: terrace, set: setTerrace },
            ].map((crit) => (
              <label
                key={crit.id}
                className={`flex items-center gap-2 p-3 rounded-xl border text-xs font-semibold cursor-pointer select-none transition-all ${
                  crit.checked
                    ? 'border-[#ea580c] bg-[#ea580c]/10 text-white'
                    : 'border-white/10 bg-black/30 text-neutral-400 hover:border-white/20'
                }`}
              >
                <input
                  type="checkbox"
                  checked={crit.checked}
                  onChange={(e) => crit.set(e.target.checked)}
                  className="rounded text-[#ea580c] focus:ring-0"
                />
                {crit.label}
              </label>
            ))}
          </div>
        </div>

        {/* Organizer departure */}
        <div className="p-6 rounded-2xl bg-[#121212] border border-white/10 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <MapPin className="w-5 h-5 text-[#ea580c]" />
            Votre point de départ (Organisateur)
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-neutral-400 mb-1">Votre quartier / Ville</label>
              <input
                type="text"
                value={myLocation}
                onChange={(e) => setMyLocation(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-neutral-400 mb-1">Moyen de transport</label>
              <select
                value={myTransport}
                onChange={(e) => setMyTransport(e.target.value)}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
              >
                <option value="TRANSIT">Transports en commun</option>
                <option value="DRIVING">Voiture</option>
                <option value="CYCLING">Vélo</option>
                <option value="WALKING">À pied</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-neutral-400 mb-1">Trajet max (min)</label>
              <input
                type="number"
                value={myMaxTime}
                onChange={(e) => setMyMaxTime(Number(e.target.value))}
                className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#ea580c]"
              />
            </div>
          </div>
        </div>

        <Button type="submit" variant="orange" size="lg" disabled={loading} className="w-full h-12 rounded-xl text-base font-bold shadow-lg">
          {loading ? "Création en cours..." : "Créer la rencontre et générer le lien"}
        </Button>
      </form>
    </div>
  );
}
