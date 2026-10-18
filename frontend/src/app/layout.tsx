import type { Metadata } from 'next';
import './globals.css';

import { Navbar } from '@/components/Navbar';

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
        <Navbar />

        <main className="flex-1">{children}</main>

        <footer className="border-t border-white/10 py-8 px-6 text-center text-xs text-neutral-500">
          <p>© 2026 MeetSpot. Fait partie de l'écosystème <a href="https://oussamma.tn" className="underline hover:text-white">oussamma.tn</a>. Tous droits réservés.</p>
        </footer>
      </body>
    </html>
  );
}
