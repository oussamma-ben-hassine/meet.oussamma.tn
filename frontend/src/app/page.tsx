'use client';

import React, { useState } from 'react';
import { Sparkles, MapPin, Users, Compass, ArrowRight, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  const [naturalQuery, setNaturalQuery] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiResult, setAiResult] = useState<any>(null);

  const handleAiSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!naturalQuery.trim()) return;

    setIsAnalyzing(true);
    try {
      const res = await fetch('/api/v1/ai/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: naturalQuery })
      });
      if (res.ok) {
        const data = await res.json();
        setAiResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="relative overflow-hidden">
      {/* Ambient background glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-[#ea580c]/15 to-[#3b82f6]/10 blur-[130px] -z-10 pointer-events-none" />

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 pt-20 pb-16 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-white/10 bg-white/5 text-xs font-mono text-[#f97316] mb-6">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Algorithme d'équité géographique & transport réel</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-black tracking-tight mb-6">
          Trouvez le lieu idéal où <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-neutral-200 to-neutral-400">
            tout le monde gagne au change.
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-neutral-400 text-base sm:text-lg mb-10">
          MeetSpot calcule le compromis géographique parfait entre amis selon vos temps de trajet réels, vos modes de transport et vos critères indispensables.
        </p>

        {/* 2 Dominant Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <a href="/meetings/new" className="w-full sm:w-auto">
            <Button size="lg" variant="orange" className="w-full gap-2 rounded-xl h-12 text-base font-bold shadow-lg shadow-[#ea580c]/20">
              <Users className="w-5 h-5" />
              Organiser une rencontre
            </Button>
          </a>
          <a href="/search" className="w-full sm:w-auto">
            <Button size="lg" variant="outline" className="w-full gap-2 rounded-xl h-12 text-base font-medium">
              <Compass className="w-5 h-5" />
              Trouver un lieu rapidement
            </Button>
          </a>
        </div>

        {/* AI Natural Search Input */}
        <div className="max-w-3xl mx-auto p-4 sm:p-6 rounded-2xl border border-white/10 bg-[#121212]/90 backdrop-blur-md shadow-2xl text-left">
          <div className="flex items-center gap-2 mb-3 text-xs font-semibold uppercase tracking-wider text-neutral-400">
            <Sparkles className="w-4 h-4 text-[#ea580c]" />
            Recherche conversationnelle LiteLLM
          </div>
          
          <form onSubmit={handleAiSearch} className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={naturalQuery}
              onChange={(e) => setNaturalQuery(e.target.value)}
              placeholder="Ex : On est 5, deux à Argenteuil, un à Créteil et deux à Versailles. Resto halal max 40 min..."
              className="flex-1 bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-neutral-500 focus:outline-none focus:border-[#ea580c]"
            />
            <Button type="submit" variant="orange" disabled={isAnalyzing} className="h-11 rounded-xl font-medium shrink-0">
              {isAnalyzing ? "Analyse en cours..." : "Analyser"}
            </Button>
          </form>

          {aiResult && (
            <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 text-xs text-neutral-300">
              <p className="font-semibold text-white mb-2">{aiResult.summary}</p>
              <div className="flex flex-wrap gap-2 mt-2">
                <span className="px-2 py-1 rounded bg-[#ea580c]/20 text-[#f97316] font-mono">
                  Catégorie : {aiResult.category}
                </span>
                {aiResult.budget_max && (
                  <span className="px-2 py-1 rounded bg-blue-500/20 text-blue-400 font-mono">
                    Budget : ≤ {aiResult.budget_max}€
                  </span>
                )}
                {aiResult.max_duration_minutes && (
                  <span className="px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 font-mono">
                    Trajet max : {aiResult.max_duration_minutes} min
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Feature Grid */}
      <section className="max-w-5xl mx-auto px-6 py-12 border-t border-white/10 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-2xl bg-[#121212] border border-white/5">
          <div className="w-10 h-10 rounded-xl bg-[#ea580c]/10 text-[#ea580c] flex items-center justify-center mb-4">
            <Compass className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold mb-2">Algorithme Minimax & Équité</h3>
          <p className="text-sm text-neutral-400">
            Minimisez le trajet du participant le plus éloigné et équilibrez les temps de trajet en transports, voiture ou vélo.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-[#121212] border border-white/5">
          <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center mb-4">
            <Users className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold mb-2">Invités sans compte & Vote</h3>
          <p className="text-sm text-neutral-400">
            Partagez un lien d'invitation sécurisé via WhatsApp ou SMS. Chacun entre ses contraintes en privé et vote pour sa shortlist préférée.
          </p>
        </div>

        <div className="p-6 rounded-2xl bg-[#121212] border border-white/5">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold mb-2">Vie privée & Données vérifiées</h3>
          <p className="text-sm text-neutral-400">
            Les adresses personnelles sont masquées aux autres participants. Lieux vérifiés, filtres stricts sans concessions.
          </p>
        </div>
      </section>
    </div>
  );
}
