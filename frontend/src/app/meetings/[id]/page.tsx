'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { Users, MapPin, Share2, Play, ThumbsUp, CheckCircle, Navigation, ExternalLink, Calendar, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import InteractiveMap from '@/components/map/InteractiveMap';
import { Meeting, Candidate } from '@/types';

export default function MeetingDetailPage() {
  const { id } = useParams() as { id: string };
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [inviteUrl, setInviteUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const loadData = async () => {
    try {
      const res = await fetch(`/api/v1/meetings/${id}`);
      if (res.ok) {
        const m = await res.json();
        setMeeting(m);
      }
      const cRes = await fetch(`/api/v1/meetings/${id}/results`);
      if (cRes.ok) {
        const c = await cRes.json();
        setCandidates(c);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const generateInvite = async () => {
    try {
      const res = await fetch(`/api/v1/meetings/${id}/invitations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const data = await res.json();
        setInviteUrl(data.invite_url);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleLaunchSearch = async () => {
    setSearching(true);
    try {
      await fetch(`/api/v1/meetings/${id}/search`, { method: 'POST' });
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setSearching(false);
    }
  };

  const handleVote = async (candidateId: string) => {
    const participantId = meeting?.participants[0]?.id;
    if (!participantId) return;

    try {
      await fetch(`/api/v1/meetings/${id}/votes?participant_id=${participantId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ candidate_id: candidateId, rank: 1 })
      });
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  const handleConfirm = async (placeId: string) => {
    try {
      await fetch(`/api/v1/meetings/${id}/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ place_id: placeId })
      });
      await loadData();
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-neutral-400">Chargement de la rencontre...</div>;
  }

  if (!meeting) {
    return <div className="text-center py-20 text-neutral-400">Rencontre introuvable.</div>;
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-10 space-y-8">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-[#121212] border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-0.5 rounded-full bg-[#ea580c]/20 text-[#f97316] font-mono text-xs font-semibold uppercase">
              Statut : {meeting.status}
            </span>
            <span className="px-2.5 py-0.5 rounded-full bg-white/10 text-neutral-300 font-mono text-xs">
              Stratégie : {meeting.optimization_strategy}
            </span>
          </div>
          <h1 className="text-3xl font-black text-white">{meeting.title}</h1>
          <p className="text-sm text-neutral-400 mt-1">
            {meeting.category} • Budget indicatif: {meeting.max_budget_per_person ? `${meeting.max_budget_per_person}€/pers` : 'Libre'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Button onClick={generateInvite} variant="outline" className="gap-2 rounded-xl text-xs">
            <Share2 className="w-4 h-4" />
            Lien d'invitation
          </Button>

          <Button
            onClick={handleLaunchSearch}
            disabled={searching}
            variant="orange"
            className="gap-2 rounded-xl text-xs font-bold"
          >
            <Play className="w-4 h-4" />
            {searching ? 'Calcul en cours...' : 'Lancer le calcul d\'équité'}
          </Button>
        </div>
      </div>

      {/* Invite Modal/Box if created */}
      {inviteUrl && (
        <div className="p-4 rounded-2xl bg-[#ea580c]/10 border border-[#ea580c]/30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Share2 className="w-5 h-5 text-[#ea580c] shrink-0" />
            <span className="text-xs text-neutral-200 truncate">{inviteUrl}</span>
          </div>
          <Button
            size="sm"
            variant="orange"
            onClick={() => {
              navigator.clipboard.writeText(inviteUrl);
              setCopied(true);
              setTimeout(() => setCopied(false), 2000);
            }}
            className="gap-1 rounded-xl text-xs shrink-0"
          >
            {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
            {copied ? 'Copié !' : 'Copier'}
          </Button>
        </div>
      )}

      {/* Participants Summary */}
      <div className="p-6 rounded-3xl bg-[#121212] border border-white/10">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <Users className="w-5 h-5 text-[#ea580c]" />
          Participants ({meeting.participants.length})
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {meeting.participants.map((p) => (
            <div key={p.id} className="p-3.5 rounded-2xl bg-black/40 border border-white/5 space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-white">{p.name}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-white/10 font-mono text-neutral-400">
                  {p.transport_mode}
                </span>
              </div>
              <p className="text-xs text-neutral-400 truncate">
                📍 {p.departure_label || 'Non renseigné'}
              </p>
              <p className="text-[11px] text-neutral-500">
                Max : {p.max_travel_time_minutes} min • {p.has_submitted ? 'Prêt' : 'En attente'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Confirmed Final Spot if status is CONFIRMED */}
      {meeting.status === 'CONFIRMED' && meeting.confirmed_place && (
        <div className="p-8 rounded-3xl bg-emerald-950/40 border border-emerald-500/40 text-left space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-bold font-mono">
            <CheckCircle className="w-4 h-4" />
            RENCONTRE CONFIRMÉE
          </div>
          <h2 className="text-2xl font-black text-white">{meeting.confirmed_place.name}</h2>
          <p className="text-sm text-neutral-300">{meeting.confirmed_place.address}</p>
          <div className="flex gap-4">
            <a
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                meeting.confirmed_place.address
              )}`}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-emerald-500 text-black hover:bg-emerald-400"
            >
              <Navigation className="w-4 h-4" />
              Ouvrir l'itinéraire GPS
            </a>
          </div>
        </div>
      )}

      {/* Main Grid: Candidates List & Interactive Map */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Candidates List */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold flex items-center justify-between">
            <span>Lieux candidats & Classement</span>
            <span className="text-xs font-mono text-neutral-500">{candidates.length} lieux analysés</span>
          </h2>

          {candidates.length === 0 ? (
            <div className="p-12 text-center rounded-3xl bg-[#121212] border border-white/10 text-neutral-500 text-sm">
              Aucun calcul lancé. Cliquez sur "Lancer le calcul d'équité" pour trouver les meilleurs spots.
            </div>
          ) : (
            candidates.map((cand, idx) => (
              <div
                key={cand.id}
                className={`p-5 rounded-2xl border transition-all ${
                  cand.is_eligible
                    ? 'bg-[#121212] border-white/10 hover:border-white/30'
                    : 'bg-red-950/10 border-red-900/20 opacity-60'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="w-6 h-6 rounded-full bg-white/10 text-white font-mono text-xs flex items-center justify-center font-bold">
                        #{idx + 1}
                      </span>
                      <h3 className="font-bold text-white text-base">{cand.place.name}</h3>
                    </div>
                    <p className="text-xs text-neutral-400 mt-1">{cand.place.address}</p>
                  </div>

                  <div className="text-right">
                    <span className="text-xl font-black text-[#ea580c] font-mono">
                      {Math.round(cand.total_score)}
                    </span>
                    <span className="text-[10px] text-neutral-500 block">/100 score</span>
                  </div>
                </div>

                <p className="text-xs text-neutral-300 mt-3 p-2.5 rounded-xl bg-white/5 border border-white/5">
                  {cand.explanation}
                </p>

                {/* Individual travel times breakdown */}
                {cand.routes_summary && cand.routes_summary.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2 text-[11px] font-mono text-neutral-400">
                    {cand.routes_summary.map((r: any, rIdx: number) => (
                      <span key={rIdx} className="px-2 py-0.5 rounded bg-black/40 border border-white/5">
                        {r.participant_name} : {Math.round(r.duration_seconds / 60)} min ({r.mode})
                      </span>
                    ))}
                  </div>
                )}

                {/* Actions: Vote & Confirm */}
                <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleVote(cand.id)}
                    className="gap-1.5 text-xs rounded-xl"
                  >
                    <ThumbsUp className="w-3.5 h-3.5 text-[#ea580c]" />
                    Voter ({cand.votes_count})
                  </Button>

                  {meeting.status !== 'CONFIRMED' && (
                    <Button
                      size="sm"
                      variant="orange"
                      onClick={() => handleConfirm(cand.place.id)}
                      className="text-xs rounded-xl font-bold"
                    >
                      Choisir ce lieu
                    </Button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Map View */}
        <div className="sticky top-24 h-[550px]">
          <InteractiveMap
            places={candidates.map((c) => ({
              id: c.place.id,
              name: c.place.name,
              latitude: c.place.latitude,
              longitude: c.place.longitude,
              total_score: c.total_score,
            }))}
          />
        </div>
      </div>
    </div>
  );
}
