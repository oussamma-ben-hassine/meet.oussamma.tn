'use client';

import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

interface MapProps {
  center?: [number, number];
  zoom?: number;
  places?: Array<{
    id: string;
    name: string;
    latitude: number;
    longitude: number;
    total_score?: number;
  }>;
  onSelectPlace?: (id: string) => void;
}

export default function InteractiveMap({
  center = [2.3522, 48.8566],
  zoom = 12,
  places = [],
  onSelectPlace
}: MapProps) {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    map.current = new maplibregl.Map({
      container: mapContainer.current,
      style: 'https://tiles.openfreemap.org/styles/liberty',
      center: center,
      zoom: zoom,
    });

    map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
  }, [center, zoom]);

  // Update markers when places change
  useEffect(() => {
    if (!map.current) return;

    // Add markers for each place
    places.forEach((p) => {
      const el = document.createElement('div');
      el.className = 'w-8 h-8 rounded-full bg-[#ea580c] text-white flex items-center justify-center font-bold text-xs shadow-lg cursor-pointer border-2 border-white hover:scale-110 transition-transform';
      el.innerText = p.total_score ? `${Math.round(p.total_score)}` : '📍';
      
      el.addEventListener('click', () => {
        if (onSelectPlace) onSelectPlace(p.id);
      });

      new maplibregl.Marker({ element: el })
        .setLngLat([p.longitude, p.latitude])
        .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(`<strong>${p.name}</strong>`))
        .addTo(map.current!);
    });
  }, [places, onSelectPlace]);

  return (
    <div className="w-full h-full min-h-[350px] rounded-2xl overflow-hidden border border-white/10 relative">
      <div ref={mapContainer} className="w-full h-full" />
    </div>
  );
}
