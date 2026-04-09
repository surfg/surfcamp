import { Link } from 'react-router-dom';
import { MapPin, Star, Clock, Percent } from 'lucide-react';
import { OptimizedImage } from './OptimizedImage';
import type { SurfCamp } from '../types';

interface CampCardProps {
  camp: SurfCamp;
}

// Calculate time remaining for discount
function getTimeRemaining(endTime: string | null): { hours: number; minutes: number } | null {
  if (!endTime) return null;
  const end = new Date(endTime).getTime();
  const now = Date.now();
  const diff = end - now;

  if (diff <= 0) return null;

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

  return { hours, minutes };
}

export function CampCard({ camp }: CampCardProps) {
  const imageUrl = camp.main_image || 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&h=600&fit=crop';

  // Check for active discount
  const hasDiscount = camp.discount_percent && camp.discount_percent > 0;
  const timeRemaining = camp.discount_ends_at ? getTimeRemaining(camp.discount_ends_at) : null;
  const isDiscountActive = hasDiscount && timeRemaining;

  // Calculate discounted price
  const originalPrice = Number(camp.price_per_night);
  const discountedPrice = isDiscountActive
    ? originalPrice * (1 - (camp.discount_percent || 0) / 100)
    : originalPrice;

  return (
    <Link
      to={`/camps/${camp.slug}`}
      style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}
    >
      <article>
        {/* Image */}
        <div style={{
          position: 'relative',
          borderRadius: '16px',
          overflow: 'hidden',
          marginBottom: '12px'
        }}>
          <OptimizedImage
            src={imageUrl}
            alt={camp.name}
            aspectRatio="4/3"
            sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            style={{
              transition: 'transform 0.3s'
            }}
          />

          {/* Discount Badge with Timer */}
          {isDiscountActive && (
            <div style={{
              position: 'absolute',
              top: '12px',
              right: '12px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-end',
              gap: '6px'
            }}>
              <div style={{
                padding: '6px 12px',
                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                borderRadius: '20px',
                fontSize: '13px',
                fontWeight: 700,
                color: 'white',
                boxShadow: '0 2px 8px rgba(239,68,68,0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <Percent style={{ width: '14px', height: '14px' }} />
                -{camp.discount_percent}%
              </div>
              <div style={{
                padding: '4px 10px',
                backgroundColor: 'rgba(0,0,0,0.75)',
                borderRadius: '12px',
                fontSize: '11px',
                fontWeight: 600,
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <Clock style={{ width: '12px', height: '12px' }} />
                {timeRemaining.hours}h {timeRemaining.minutes}m left
              </div>
              <div style={{
                padding: '3px 8px',
                backgroundColor: 'white',
                borderRadius: '10px',
                fontSize: '10px',
                fontWeight: 600,
                color: '#dc2626',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}>
                Register to claim
              </div>
            </div>
          )}

          {/* Featured Badge */}
          {camp.is_featured && !isDiscountActive && (
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              padding: '6px 12px',
              backgroundColor: 'white',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              color: '#0f172a',
              boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
            }}>
              Guest favourite
            </div>
          )}

          {/* Featured Badge (when discount is active) */}
          {camp.is_featured && isDiscountActive && (
            <div style={{
              position: 'absolute',
              top: '12px',
              left: '12px',
              padding: '6px 12px',
              background: 'linear-gradient(135deg, #fbbf24, #f97316)',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600,
              color: 'white',
              boxShadow: '0 2px 8px rgba(251,191,36,0.4)'
            }}>
              Guest favourite
            </div>
          )}

          {/* Amenities */}
          {(camp.has_pool || camp.has_yoga) && (
            <div style={{
              position: 'absolute',
              bottom: '12px',
              left: '12px',
              display: 'flex',
              gap: '6px'
            }}>
              {camp.has_pool && (
                <span style={{
                  padding: '5px 10px',
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  borderRadius: '8px',
                  fontSize: '11px',
                  fontWeight: 500,
                  color: '#0284c7'
                }}>Pool</span>
              )}
              {camp.has_yoga && (
                <span style={{
                  padding: '5px 10px',
                  backgroundColor: 'rgba(255,255,255,0.95)',
                  borderRadius: '8px',
                  fontSize: '11px',
                  fontWeight: 500,
                  color: '#7c3aed'
                }}>Yoga</span>
              )}
            </div>
          )}
        </div>

        {/* Content */}
        <div>
          {/* Location & Rating Row */}
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
              <span>{camp.region_name}, {camp.country_name}</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <Star style={{ width: '14px', height: '14px', fill: '#0f172a', color: '#0f172a' }} />
              <span style={{ fontSize: '14px', fontWeight: 500, color: '#0f172a' }}>
                {Number(camp.rating).toFixed(1)}
              </span>
              <span style={{ fontSize: '13px', color: '#94a3b8' }}>
                ({camp.reviews_count})
              </span>
            </div>
          </div>

          {/* Name */}
          <h3 style={{
            fontSize: '16px',
            fontWeight: 600,
            color: '#0f172a',
            margin: '0 0 6px 0',
            lineHeight: 1.4
          }}>
            {camp.name}
          </h3>

          {/* Skill Levels + Languages */}
          <p style={{
            fontSize: '14px',
            color: '#64748b',
            margin: '0 0 8px 0',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            flexWrap: 'wrap',
          }}>
            <span>
              {camp.skill_levels.map(level =>
                level.charAt(0).toUpperCase() + level.slice(1)
              ).join(' · ')} levels
            </span>
            {camp.teaching_languages && camp.teaching_languages.length > 0 && (
              <span style={{ display: 'flex', gap: '4px' }}>
                {camp.teaching_languages.slice(0, 3).map(lang => (
                  <span
                    key={lang}
                    style={{
                      padding: '2px 6px',
                      backgroundColor: '#f1f5f9',
                      color: '#475569',
                      borderRadius: '4px',
                      fontSize: '10px',
                      fontWeight: 600,
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}
                  >
                    {lang}
                  </span>
                ))}
              </span>
            )}
          </p>

          {/* Price */}
          <p style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            {isDiscountActive ? (
              <>
                <span style={{
                  fontSize: '14px',
                  color: '#94a3b8',
                  textDecoration: 'line-through'
                }}>
                  ${originalPrice.toFixed(0)}
                </span>
                <span style={{
                  fontSize: '16px',
                  fontWeight: 600,
                  color: '#dc2626'
                }}>
                  ${discountedPrice.toFixed(0)}
                </span>
                <span style={{ fontSize: '14px', color: '#64748b' }}> / night</span>
              </>
            ) : (
              <>
                <span style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>
                  ${originalPrice.toFixed(0)}
                </span>
                <span style={{ fontSize: '14px', color: '#64748b' }}> / night</span>
              </>
            )}
          </p>
        </div>
      </article>
    </Link>
  );
}
