import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Star, Waves } from 'lucide-react';
import { getSpots } from '../lib/api';
import type { SurfSpot } from '../types';

export function SpotsPage() {
  const [spots, setSpots] = useState<SurfSpot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSpots = useCallback(() => {
    setLoading(true);
    setError(null);
    getSpots()
      .then((data) => setSpots(data.results))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchSpots();
  }, [fetchSpots]);

  const getWaveLabel = (type: string) => {
    const labels: Record<string, string> = {
      'beach': 'Beach Break',
      'reef': 'Reef Break',
      'point': 'Point Break'
    };
    return labels[type] || type;
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Header */}
      <div style={{
        borderBottom: '1px solid #e2e8f0',
        backgroundColor: 'white'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '32px 24px'
        }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 700,
            color: '#0f172a',
            margin: 0
          }}>
            Surf Spots
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#64748b',
            margin: '8px 0 0'
          }}>
            Discover the best waves around the world
          </p>
        </div>
      </div>

      {/* Content */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '32px 24px'
      }}>
        {error ? (
          <div style={{
            textAlign: 'center',
            padding: '80px 24px'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              backgroundColor: '#fee2e2',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
              fontSize: '28px'
            }}>
              😕
            </div>
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
              Something went wrong
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 24px' }}>{error}</p>
            <button
              onClick={fetchSpots}
              style={{
                padding: '12px 24px',
                backgroundColor: '#0f172a',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '14px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Try Again
            </button>
          </div>
        ) : loading ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i}>
                <div style={{
                  aspectRatio: '4/3',
                  backgroundColor: '#f1f5f9',
                  borderRadius: '16px',
                  marginBottom: '12px'
                }} />
                <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '60%', marginBottom: '8px' }} />
                <div style={{ height: '18px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '80%' }} />
              </div>
            ))}
          </div>
        ) : spots.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '80px 24px'
          }}>
            <Waves style={{ width: '48px', height: '48px', color: '#94a3b8', margin: '0 auto 16px' }} />
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
              No spots found
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b', margin: 0 }}>
              Check back later
            </p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {spots.map((spot) => (
              <Link
                key={spot.id}
                to={`/spots/${spot.slug}`}
                style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}
              >
                <article>
                  {/* Image */}
                  <div style={{
                    position: 'relative',
                    aspectRatio: '4/3',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    marginBottom: '12px'
                  }}>
                    <img
                      src={spot.main_image || 'https://images.unsplash.com/photo-1509914398892-963f53e6e2f1?w=800&h=600&fit=crop'}
                      alt={spot.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                      }}
                    />
                    <div style={{
                      position: 'absolute',
                      top: '12px',
                      left: '12px',
                      padding: '6px 12px',
                      backgroundColor: 'white',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#ea580c'
                    }}>
                      {getWaveLabel(spot.wave_type)}
                    </div>
                  </div>

                  {/* Content */}
                  <div>
                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '4px'
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        color: '#64748b',
                        fontSize: '14px'
                      }}>
                        <MapPin style={{ width: '14px', height: '14px' }} />
                        <span>{spot.region_name}, {spot.country_name}</span>
                      </div>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <Star style={{ width: '14px', height: '14px', fill: '#0f172a', color: '#0f172a' }} />
                        <span style={{ fontSize: '14px', fontWeight: 500 }}>
                          {Number(spot.rating).toFixed(1)}
                        </span>
                      </div>
                    </div>

                    <h3 style={{
                      fontSize: '16px',
                      fontWeight: 600,
                      color: '#0f172a',
                      margin: '0 0 6px'
                    }}>
                      {spot.name}
                    </h3>

                    <p style={{
                      fontSize: '14px',
                      color: '#64748b',
                      margin: '0 0 8px',
                      display: '-webkit-box',
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden'
                    }}>
                      {spot.short_description}
                    </p>

                    <div style={{
                      display: 'flex',
                      gap: '8px'
                    }}>
                      {spot.skill_levels.map(level => (
                        <span
                          key={level}
                          style={{
                            padding: '4px 10px',
                            backgroundColor: level === 'beginner' ? '#dcfce7' : level === 'intermediate' ? '#fef3c7' : '#fce7f3',
                            color: level === 'beginner' ? '#166534' : level === 'intermediate' ? '#92400e' : '#9d174d',
                            borderRadius: '6px',
                            fontSize: '12px',
                            fontWeight: 500,
                            textTransform: 'capitalize'
                          }}
                        >
                          {level}
                        </span>
                      ))}
                    </div>
                  </div>
                </article>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
