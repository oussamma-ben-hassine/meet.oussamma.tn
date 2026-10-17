import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'MeetSpot — Le Meilleur Compromis de Rencontre',
  description: 'Trouvez le meilleur café, restaurant, parc ou activité pour une rencontre équitable entre amis.',
  manifest: '/manifest.json',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="bg-[#080808] text-white flex flex-col min-h-screen antialiased selection:bg-[#ea580c] selection:text-white">
        <header className="sticky top-0 z-50 backdrop-blur-md bg-[#080808]/80 border-b border-white/10 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <a href="/" className="flex items-center gap-2 group">
              <span className="w-8 h-8 rounded-lg bg-[#ea580c] flex items-center justify-center font-black text-white shadow-md shadow-[#ea580c]/30 group-hover:scale-105 transition-transform">
                M
              </span>
              <span className="font-bold text-lg tracking-tight text-white">
                Meet<span className="text-[#ea580c]">Spot</span>
              </span>
            </a>
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-neutral-400 font-mono hidden sm:inline-block">
              oussamma.tn
            </span>
          </div>
          
          <nav className="flex items-center gap-4 text-sm font-medium">
            <a href="/search" className="text-neutral-300 hover:text-white transition-colors">
              Recherche
            </a>
            <a href="/meetings" className="text-neutral-300 hover:text-white transition-colors">
              Mes Rencontres
            </a>
            <a
              href="https://sso-a.oussamma.tn/oauth/authorize?client_id=client_424090bad2dcadc34cdda40f&redirect_uri=https://meet.oussamma.tn/auth/callback&response_type=code&scope=openid%20profile%20email"
              className="px-4 py-1.5 rounded-full bg-white text-black font-semibold hover:bg-neutral-200 transition-colors shadow-sm text-xs"
            >
              Connexion SSO
            </a>
          </nav>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-white/10 py-8 px-6 text-center text-xs text-neutral-500">
          <p>© 2026 MeetSpot. Fait partie de l'écosystème <a href="https://oussamma.tn" className="underline hover:text-white">oussamma.tn</a>. Tous droits réservés.</p>
        </footer>
      </body>
    </html>
  );
}
