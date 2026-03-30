import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  MapPin, Star, ArrowLeft, Waves, AlertTriangle,
  ChevronLeft, ChevronRight, Car, Droplets, Coffee, ShieldCheck
} from 'lucide-react';
import { getSpot } from '../lib/api';
import type { SurfSpotDetail } from '../types';

export function SpotDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [spot, setSpot] = useState<SurfSpotDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImage, setActiveImage] = useState(0);

  useEffect(() => {
    if (slug) {
      setLoading(true);
      setError(null);
      getSpot(slug)
        .then(setSpot)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }
  }, [slug]);

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
          borderTopColor: '#f97316',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    );
  }

  if (error || !spot) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: '#ffffff',
        padding: '24px'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', marginBottom: '16px' }}>
            {error || 'Spot not found'}
          </h1>
          <Link to="/spots" style={{ color: '#f97316', textDecoration: 'none' }}>
            Back to spots
          </Link>
        </div>
      </div>
    );
  }

  const images = spot.images?.length > 0
    ? spot.images.map(img => img.image)
    : ['https://images.unsplash.com/photo-1509914398892-963f53e6e2f1?w=1200&h=800&fit=crop'];

  const getWaveLabel = (type: string) => {
    const labels: Record<string, string> = {
      'beach': 'Beach Break',
      'reef': 'Reef Break',
      'point': 'Point Break'
    };
    return labels[type] || type;
  };

  const getCrowdLabel = (level: string) => {
    const labels: Record<string, { label: string; color: string; bg: string }> = {
      'empty': { label: 'Empty', color: '#059669', bg: '#d1fae5' },
      'few': { label: 'Few people', color: '#16a34a', bg: '#dcfce7' },
      'moderate': { label: 'Moderate', color: '#ca8a04', bg: '#fef3c7' },
      'crowded': { label: 'Crowded', color: '#ea580c', bg: '#ffedd5' },
      'packed': { label: 'Very crowded', color: '#dc2626', bg: '#fee2e2' }
    };
    return labels[level] || { label: level, color: '#64748b', bg: '#f1f5f9' };
  };

  const crowdInfo = getCrowdLabel(spot.crowd_level);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Back Button */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '16px 24px'
      }}>
        <Link
          to="/spots"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            color: '#64748b',
            textDecoration: 'none',
            fontSize: '14px',
            fontWeight: 500
          }}
        >
          <ArrowLeft style={{ width: '18px', height: '18px' }} />
          Back to spots
        </Link>
      </div>

      {/* Image Gallery */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 24px 32px'
      }}>
        <div style={{
          position: 'relative',
          aspectRatio: '16/9',
          maxHeight: '500px',
          borderRadius: '24px',
          overflow: 'hidden',
          backgroundColor: '#f1f5f9'
        }}>
          <img
            src={images[activeImage]}
            alt={spot.name}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />

          {images.length > 1 && (
            <>
              <button
                onClick={() => setActiveImage((activeImage - 1 + images.length) % images.length)}
                style={{
                  position: 'absolute',
                  left: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '44px',
                  height: '44px',
                  backgroundColor: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                }}
              >
                <ChevronLeft style={{ width: '24px', height: '24px', color: '#0f172a' }} />
              </button>
              <button
                onClick={() => setActiveImage((activeImage + 1) % images.length)}
                style={{
                  position: 'absolute',
                  right: '16px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  width: '44px',
                  height: '44px',
                  backgroundColor: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
                }}
              >
                <ChevronRight style={{ width: '24px', height: '24px', color: '#0f172a' }} />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 24px 80px',
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '48px'
      }} className="lg:grid-cols-[1fr_380px]">
        {/* Main Content */}
        <div>
          {/* Header */}
          <div style={{ marginBottom: '32px' }}>
            <span style={{
              display: 'inline-block',
              padding: '6px 14px',
              backgroundColor: '#fff7ed',
              color: '#ea580c',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              marginBottom: '12px'
            }}>
              {getWaveLabel(spot.wave_type)}
            </span>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 700,
              color: '#0f172a',
              margin: '0 0 12px'
            }}>
              {spot.name}
            </h1>
            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              gap: '16px',
              color: '#64748b',
              fontSize: '15px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin style={{ width: '18px', height: '18px' }} />
                {spot.region_name}, {spot.country_name}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Star style={{ width: '18px', height: '18px', fill: '#0f172a', color: '#0f172a' }} />
                <span style={{ fontWeight: 600, color: '#0f172a' }}>{Number(spot.rating).toFixed(1)}</span>
              </div>
            </div>

            {/* Skill Levels */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
              {spot.skill_levels.map(level => (
                <span
                  key={level}
                  style={{
                    padding: '6px 14px',
                    backgroundColor: level === 'beginner' ? '#dcfce7' : level === 'intermediate' ? '#fef3c7' : '#fce7f3',
                    color: level === 'beginner' ? '#166534' : level === 'intermediate' ? '#92400e' : '#9d174d',
                    borderRadius: '20px',
                    fontSize: '13px',
                    fontWeight: 500,
                    textTransform: 'capitalize'
                  }}
                >
                  {level}
                </span>
              ))}
            </div>
          </div>

          {/* Wave Info */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '12px',
            marginBottom: '32px'
          }}>
            <div style={{
              padding: '20px',
              backgroundColor: '#f8fafc',
              borderRadius: '16px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                <Waves style={{ width: '18px', height: '18px', color: '#64748b' }} />
                <span style={{ fontSize: '13px', color: '#64748b' }}>Direction</span>
              </div>
              <p style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: 0 }}>
                {spot.wave_direction === 'both' ? 'A-Frame' : spot.wave_direction === 'left' ? 'Left' : 'Right'}
              </p>
            </div>

            <div style={{
              padding: '20px',
              backgroundColor: crowdInfo.bg,
              borderRadius: '16px'
            }}>
              <span style={{ fontSize: '13px', color: crowdInfo.color }}>Crowd</span>
              <p style={{ fontSize: '16px', fontWeight: 600, color: crowdInfo.color, margin: '8px 0 0' }}>
                {crowdInfo.label}
              </p>
            </div>

            {spot.best_tide && (
              <div style={{
                padding: '20px',
                backgroundColor: '#f8fafc',
                borderRadius: '16px'
              }}>
                <span style={{ fontSize: '13px', color: '#64748b' }}>Best Tide</span>
                <p style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: '8px 0 0', textTransform: 'capitalize' }}>
                  {spot.best_tide}
                </p>
              </div>
            )}
          </div>

          {/* Description */}
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
              About this spot
            </h3>
            <p style={{ fontSize: '15px', lineHeight: 1.7, color: '#475569', whiteSpace: 'pre-line' }}>
              {spot.description || spot.short_description}
            </p>
          </div>

          {/* Hazards */}
          {(spot.has_rocks || spot.has_reef || spot.has_currents || spot.has_sharks || spot.hazards) && (
            <div style={{
              padding: '24px',
              backgroundColor: '#fef3c7',
              borderRadius: '16px',
              marginBottom: '32px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <AlertTriangle style={{ width: '20px', height: '20px', color: '#b45309' }} />
                <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#92400e', margin: 0 }}>
                  Hazards & Warnings
                </h3>
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {spot.has_rocks && (
                  <span style={{ padding: '6px 14px', backgroundColor: '#fde68a', color: '#92400e', borderRadius: '20px', fontSize: '13px', fontWeight: 500 }}>
                    Rocks
                  </span>
                )}
                {spot.has_reef && (
                  <span style={{ padding: '6px 14px', backgroundColor: '#fde68a', color: '#92400e', borderRadius: '20px', fontSize: '13px', fontWeight: 500 }}>
                    Reef Bottom
                  </span>
                )}
                {spot.has_currents && (
                  <span style={{ padding: '6px 14px', backgroundColor: '#fde68a', color: '#92400e', borderRadius: '20px', fontSize: '13px', fontWeight: 500 }}>
                    Strong Currents
                  </span>
                )}
                {spot.has_sharks && (
                  <span style={{ padding: '6px 14px', backgroundColor: '#fecaca', color: '#b91c1c', borderRadius: '20px', fontSize: '13px', fontWeight: 500 }}>
                    Sharks
                  </span>
                )}
              </div>
              {spot.hazards && (
                <p style={{ fontSize: '14px', color: '#92400e', margin: '16px 0 0' }}>{spot.hazards}</p>
              )}
            </div>
          )}

          {/* Nearby Camps */}
          {spot.nearby_camps && spot.nearby_camps.length > 0 && (
            <div>
              <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
                Nearby Surf Camps
              </h3>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '16px'
              }}>
                {spot.nearby_camps.map(camp => (
                  <Link
                    key={camp.id}
                    to={`/camps/${camp.slug}`}
                    style={{
                      display: 'flex',
                      gap: '16px',
                      padding: '16px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '16px',
                      textDecoration: 'none',
                      color: 'inherit'
                    }}
                  >
                    <img
                      src={camp.main_image || 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=200&h=150&fit=crop'}
                      alt={camp.name}
                      style={{
                        width: '100px',
                        height: '80px',
                        objectFit: 'cover',
                        borderRadius: '12px'
                      }}
                    />
                    <div>
                      <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', margin: '0 0 4px' }}>
                        {camp.name}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '4px' }}>
                        <Star style={{ width: '14px', height: '14px', fill: '#fbbf24', color: '#fbbf24' }} />
                        <span style={{ fontSize: '13px', color: '#64748b' }}>{Number(camp.rating).toFixed(1)}</span>
                      </div>
                      <p style={{ fontSize: '15px', fontWeight: 600, color: '#0ea5e9', margin: 0 }}>
                        ${Number(camp.price_per_night).toFixed(0)}/night
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Facilities */}
        <div className="hidden lg:block">
          <div style={{
            position: 'sticky',
            top: '100px',
            padding: '28px',
            backgroundColor: 'white',
            borderRadius: '20px',
            border: '1px solid #e2e8f0',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)'
          }}>
            <h4 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', marginBottom: '20px' }}>
              Facilities
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {[
                { icon: Car, label: 'Parking', available: spot.has_parking },
                { icon: Droplets, label: 'Showers', available: spot.has_showers },
                { icon: Coffee, label: 'Cafe', available: spot.has_cafe },
                { icon: ShieldCheck, label: 'Lifeguard', available: spot.has_lifeguard },
              ].map(facility => (
                <div
                  key={facility.label}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '14px',
                    backgroundColor: facility.available ? '#f0fdf4' : '#f8fafc',
                    borderRadius: '12px'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <facility.icon style={{
                      width: '20px',
                      height: '20px',
                      color: facility.available ? '#16a34a' : '#94a3b8'
                    }} />
                    <span style={{
                      fontSize: '14px',
                      fontWeight: 500,
                      color: facility.available ? '#166534' : '#94a3b8'
                    }}>
                      {facility.label}
                    </span>
                  </div>
                  {facility.available && (
                    <span style={{ fontSize: '12px', color: '#16a34a' }}>Available</span>
                  )}
                </div>
              ))}
            </div>

            <Link
              to="/map"
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                width: '100%',
                padding: '16px',
                marginTop: '24px',
                background: 'linear-gradient(135deg, #f97316, #ea580c)',
                color: 'white',
                textDecoration: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 600
              }}
            >
              <MapPin style={{ width: '18px', height: '18px' }} />
              View on Map
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
