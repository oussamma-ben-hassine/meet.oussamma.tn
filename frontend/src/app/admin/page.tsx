'use client';

import React, { useEffect, useState } from 'react';
import { Shield, Users, MapPin, Calendar, Server, Cpu, Database } from 'lucide-react';

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/admin/stats')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => setStats(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 text-red-400 font-mono text-xs mb-2">
            <Shield className="w-3.5 h-3.5" />
            SuperAdmin Console
          </div>
          <h1 className="text-3xl font-black">Administration MeetSpot</h1>
          <p className="text-sm text-neutral-400">
            Supervision de l'écosystème oussamma.tn, quotas LiteLLM, et état des services.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-neutral-500">Chargement des métriques...</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl bg-[#121212] border border-white/10">
            <Users className="w-6 h-6 text-[#ea580c] mb-3" />
            <p className="text-xs text-neutral-400">Utilisateurs enregistrés</p>
            <p className="text-3xl font-black mt-1">{stats?.users || 0}</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121212] border border-white/10">
            <Calendar className="w-6 h-6 text-blue-400 mb-3" />
            <p className="text-xs text-neutral-400">Rencontres créées</p>
            <p className="text-3xl font-black mt-1">{stats?.meetings || 0}</p>
          </div>

          <div className="p-6 rounded-2xl bg-[#121212] border border-white/10">
            <MapPin className="w-6 h-6 text-emerald-400 mb-3" />
            <p className="text-xs text-neutral-400">Lieux au catalogue</p>
            <p className="text-3xl font-black mt-1">{stats?.places || 0}</p>
          </div>
        </div>
      )}

      {/* System integrations */}
      <div className="p-6 rounded-3xl bg-[#121212] border border-white/10 space-y-4">
        <h2 className="text-lg font-bold">Services & Intégrations Actives</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Server className="w-4 h-4 text-[#ea580c]" />
              <span>SSO oussamma.tn</span>
            </div>
            <span className="text-emerald-400">Actif (OIDC)</span>
          </div>

          <div className="p-4 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="w-4 h-4 text-blue-400" />
              <span>LiteLLM AI Gateway</span>
            </div>
            <span className="text-emerald-400">{stats?.litellm_model || 'gpt-5.4'}</span>
          </div>

          <div className="p-4 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-purple-400" />
              <span>PostgreSQL + PostGIS</span>
            </div>
            <span className="text-emerald-400">Connecté</span>
          </div>

          <div className="p-4 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="w-4 h-4 text-amber-400" />
              <span>Moteur de routage</span>
            </div>
            <span className="text-emerald-400">{stats?.routing_provider || 'Mock / Urban Multi-mode'}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
