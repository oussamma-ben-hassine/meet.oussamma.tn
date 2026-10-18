'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { User as UserIcon, LogOut, Shield } from 'lucide-react';

export function Navbar() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('meetspot_user');
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch (e) {
      // ignore
    }

    const handleStorage = () => {
      try {
        const stored = localStorage.getItem('meetspot_user');
        setUser(stored ? JSON.parse(stored) : null);
      } catch (e) {}
    };

    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('meetspot_token');
    localStorage.removeItem('meetspot_user');
    setUser(null);
    window.location.href = '/';
  };

  const ssoAuthorizeUrl =
    'https://sso-a.oussamma.tn/oauth/authorize?client_id=client_meetspot_app&redirect_uri=https://meet.oussamma.tn/auth/callback&response_type=code&scope=openid%20profile%20email';

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-[#080808]/80 border-b border-white/10 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="w-8 h-8 rounded-lg bg-[#ea580c] flex items-center justify-center font-black text-white shadow-md shadow-[#ea580c]/30 group-hover:scale-105 transition-transform">
            M
          </span>
          <span className="font-bold text-lg tracking-tight text-white">
            Meet<span className="text-[#ea580c]">Spot</span>
          </span>
        </Link>
        <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-neutral-400 font-mono hidden sm:inline-block">
          oussamma.tn
        </span>
      </div>

      <nav className="flex items-center gap-4 text-sm font-medium">
        <Link href="/search" className="text-neutral-300 hover:text-white transition-colors">
          Recherche
        </Link>
        <Link href="/meetings" className="text-neutral-300 hover:text-white transition-colors">
          Mes Rencontres
        </Link>

        {user ? (
          <div className="flex items-center gap-3">
            {user.role === 'SUPERADMIN' && (
              <Link
                href="/admin"
                className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 text-neutral-300 hover:text-white text-xs transition-colors"
              >
                <Shield className="w-3.5 h-3.5 text-[#ea580c]" />
                Admin
              </Link>
            )}
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs text-white">
              <UserIcon className="w-3.5 h-3.5 text-[#ea580c]" />
              <span className="max-w-[120px] truncate">{user.display_name || user.email}</span>
            </div>
            <button
              onClick={handleLogout}
              title="Déconnexion"
              className="p-1.5 rounded-full hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <a
            href={ssoAuthorizeUrl}
            className="px-4 py-1.5 rounded-full bg-white text-black font-semibold hover:bg-neutral-200 transition-colors shadow-sm text-xs"
          >
            Connexion SSO
          </a>
        )}
      </nav>
    </header>
  );
}
