'use client';

import React, { useEffect, useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    const code = searchParams.get('code');
    const error = searchParams.get('error');
    const errorDescription = searchParams.get('error_description');

    if (error) {
      setStatus('error');
      setErrorMessage(errorDescription || error || 'Une erreur est survenue lors de la connexion SSO.');
      return;
    }

    if (!code) {
      setStatus('error');
      setErrorMessage("Aucun code d'autorisation reçu du SSO.");
      return;
    }

    async function handleExchange() {
      try {
        const redirectUri = `${window.location.origin}/auth/callback`;
        const res = await fetch('/api/v1/auth/callback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code,
            redirect_uri: redirectUri,
          }),
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Échec de la validation du jeton de connexion.');
        }

        const data = await res.json();
        if (data.token) {
          localStorage.setItem('meetspot_token', data.token);
          if (data.user) {
            localStorage.setItem('meetspot_user', JSON.stringify(data.user));
          }
          setStatus('success');
          setTimeout(() => {
            router.push('/');
          }, 1200);
        } else {
          throw new Error('Jeton de session non reçu.');
        }
      } catch (err: any) {
        setStatus('error');
        setErrorMessage(err.message || 'Erreur inconnue lors de la connexion.');
      }
    }

    handleExchange();
  }, [searchParams, router]);

  return (
    <div className="min-h-[70vh] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-[#121212] border border-white/10 rounded-2xl p-8 text-center shadow-xl">
        {status === 'loading' && (
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-[#ea580c] animate-spin mb-4" />
            <h2 className="text-xl font-bold mb-2">Authentification en cours</h2>
            <p className="text-sm text-neutral-400">
              Connexion sécurisée à l'écosystème <span className="text-white font-medium">oussamma.tn</span>...
            </p>
          </div>
        )}

        {status === 'success' && (
          <div className="flex flex-col items-center">
            <CheckCircle2 className="w-12 h-12 text-emerald-500 mb-4 animate-bounce" />
            <h2 className="text-xl font-bold text-white mb-2">Connexion réussie !</h2>
            <p className="text-sm text-neutral-400">
              Bienvenue sur MeetSpot. Redirection vers votre tableau de bord...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div className="flex flex-col items-center">
            <AlertCircle className="w-12 h-12 text-rose-500 mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Erreur d'authentification</h2>
            <p className="text-sm text-rose-300 mb-6 bg-rose-500/10 border border-rose-500/20 rounded-lg p-3">
              {errorMessage}
            </p>
            <a
              href="/"
              className="px-6 py-2.5 rounded-full bg-white text-black font-semibold text-sm hover:bg-neutral-200 transition-colors"
            >
              Retour à l'accueil
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[70vh] flex items-center justify-center">
          <Loader2 className="w-10 h-10 text-[#ea580c] animate-spin" />
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
