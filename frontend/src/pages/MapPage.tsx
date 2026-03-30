import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { Star, Waves, MapPin } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { getCampsMapData, getSpotsMapData } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfCamp, SurfSpot } from '../types';

// Fix for default markers
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: unknown })._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons
const campIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="32" height="32">
      <circle cx="12" cy="12" r="10" fill="#0ea5e9"/>
      <circle cx="12" cy="12" r="5" fill="white"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32],
});

const spotIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;base64,' + btoa(`
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28">
      <circle cx="12" cy="12" r="10" fill="#10b981"/>
      <circle cx="12" cy="12" r="5" fill="white"/>
    </svg>
  `),
  iconSize: [28, 28],
  iconAnchor: [14, 28],
  popupAnchor: [0, -28],
});

// Country centers for zoom
const countryCenters: Record<string, { center: [number, number]; zoom: number }> = {
  IDN: { center: [-8.3405, 115.0920], zoom: 10 },
  LKA: { center: [6.0535, 80.2210], zoom: 9 },
  THA: { center: [8.0250, 98.8170], zoom: 10 },
  PRT: { center: [39.3999, -9.2245], zoom: 8 },
  ESP: { center: [28.2916, -16.6291], zoom: 9 },
  MAR: { center: [30.4278, -9.5981], zoom: 9 },
  CRI: { center: [9.7489, -83.7534], zoom: 8 },
  MEX: { center: [23.6345, -109.6976], zoom: 8 },
  AUS: { center: [-28.0167, 153.4000], zoom: 8 },
  ZAF: { center: [-33.9249, 18.4241], zoom: 9 },
};

function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.setView(center, zoom, { animate: true });
  }, [map, center, zoom]);
  return null;
}

export function MapPage() {
  const { t, language } = useLanguage();
  const [searchParams] = useSearchParams();
  const [camps, setCamps] = useState<SurfCamp[]>([]);
  const [spots, setSpots] = useState<SurfSpot[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCamps, setShowCamps] = useState(true);
  const [showSpots, setShowSpots] = useState(false);

  const countryCode = searchParams.get('country');

  useEffect(() => {
    Promise.all([getCampsMapData(), getSpotsMapData()])
      .then(([campsData, spotsData]) => {
        // Filter by country if specified
        if (countryCode) {
          const filtered = campsData.filter((c: SurfCamp) => c.country_code === countryCode);
          setCamps(filtered.length > 0 ? filtered : campsData);
        } else {
          setCamps(campsData);
        }
        setSpots(spotsData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [countryCode]);

  const { center, zoom } = useMemo(() => {
    if (countryCode && countryCenters[countryCode]) {
      return countryCenters[countryCode];
    }
    if (camps.length > 0) {
      const avgLat = camps.reduce((sum, c) => sum + c.latitude, 0) / camps.length;
      const avgLng = camps.reduce((sum, c) => sum + c.longitude, 0) / camps.length;
      return { center: [avgLat, avgLng] as [number, number], zoom: 6 };
    }
    return { center: [-8.65, 115.1] as [number, number], zoom: 3 };
  }, [countryCode, camps]);

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '3px solid #e2e8f0',
          borderTopColor: '#0ea5e9',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Header */}
      <div style={{
        position: 'sticky',
        top: '72px',
        zIndex: 40,
        backgroundColor: 'white',
        borderBottom: '1px solid #e2e8f0'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '16px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h1 style={{
              fontSize: '20px',
              fontWeight: 700,
              color: '#0f172a',
              margin: 0
            }}>
              {t('map.title')}
            </h1>
            {countryCode && (
              <Link
                to="/map"
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#f1f5f9',
                  borderRadius: '8px',
                  fontSize: '13px',
                  color: '#0ea5e9',
                  textDecoration: 'none',
                  fontWeight: 500,
                }}
              >
                {language === 'ru' ? 'Все страны' : 'All countries'}
              </Link>
            )}
          </div>
          <div style={{ display: 'flex', gap: '20px' }}>
            <label style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              fontSize: '14px'
            }}>
              <input
                type="checkbox"
                checked={showCamps}
                onChange={(e) => setShowCamps(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#0ea5e9' }}
              />
              <span style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <Waves style={{ width: '16px', height: '16px', color: '#0ea5e9' }} />
                {t('map.camps')} ({camps.length})
              </span>
            </label>
            <label style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              cursor: 'pointer',
              fontSize: '14px'
            }}>
              <input
                type="checkbox"
                checked={showSpots}
                onChange={(e) => setShowSpots(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#10b981' }}
              />
              <span style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <MapPin style={{ width: '16px', height: '16px', color: '#10b981' }} />
                {t('map.spots')} ({spots.length})
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Map */}
      <div style={{ height: 'calc(100vh - 140px)' }}>
        <MapContainer
          center={center}
          zoom={zoom}
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapController center={center} zoom={zoom} />

          {showCamps && camps.map((camp) => (
            <Marker
              key={`camp-${camp.id}`}
              position={[camp.latitude, camp.longitude]}
              icon={campIcon}
            >
              <Popup>
                <div style={{ minWidth: '200px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
                    {camp.name}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Star style={{ width: '14px', height: '14px', fill: '#fbbf24', color: '#fbbf24' }} />
                      <span style={{ fontSize: '13px' }}>{Number(camp.rating).toFixed(1)}</span>
                    </div>
                    <span style={{ fontSize: '13px', color: '#64748b' }}>·</span>
                    <span style={{ fontSize: '13px', fontWeight: 600 }}>${Number(camp.price_per_night).toFixed(0)}/{language === 'ru' ? 'ночь' : 'night'}</span>
                  </div>
                  <Link
                    to={`/camps/${camp.slug}`}
                    style={{
                      display: 'inline-block',
                      padding: '8px 16px',
                      backgroundColor: '#0ea5e9',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: 500
                    }}
                  >
                    {t('map.viewDetails')}
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}

          {showSpots && spots.map((spot) => (
            <Marker
              key={`spot-${spot.id}`}
              position={[spot.latitude, spot.longitude]}
              icon={spotIcon}
            >
              <Popup>
                <div style={{ minWidth: '180px' }}>
                  <h3 style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
                    {spot.name}
                  </h3>
                  <p style={{ fontSize: '13px', color: '#64748b', margin: '0 0 12px' }}>
                    {spot.wave_type} · {spot.wave_direction === 'both' ? 'A-Frame' : spot.wave_direction}
                  </p>
                  <Link
                    to={`/spots/${spot.slug}`}
                    style={{
                      display: 'inline-block',
                      padding: '8px 16px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      textDecoration: 'none',
                      borderRadius: '8px',
                      fontSize: '13px',
                      fontWeight: 500
                    }}
                  >
                    {t('map.viewSpot')}
                  </Link>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
