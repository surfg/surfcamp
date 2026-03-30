import { Link } from 'react-router-dom';
import { MapPin, Star } from 'lucide-react';
import type { SurfCamp } from '../types';

interface CampCardProps {
  camp: SurfCamp;
}

export function CampCard({ camp }: CampCardProps) {
  const imageUrl = camp.main_image || 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&h=600&fit=crop';

  return (
    <Link
      to={`/camps/${camp.slug}`}
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
            src={imageUrl}
            alt={camp.name}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transition: 'transform 0.3s'
            }}
            className="hover:scale-105"
          />

          {/* Featured Badge */}
          {camp.is_featured && (
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

          {/* Skill Levels */}
          <p style={{
            fontSize: '14px',
            color: '#64748b',
            margin: '0 0 8px 0'
          }}>
            {camp.skill_levels.map(level =>
              level.charAt(0).toUpperCase() + level.slice(1)
            ).join(' · ')} levels
          </p>

          {/* Price */}
          <p style={{ margin: 0 }}>
            <span style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a' }}>
              ${Number(camp.price_per_night).toFixed(0)}
            </span>
            <span style={{ fontSize: '14px', color: '#64748b' }}> / night</span>
          </p>
        </div>
      </article>
    </Link>
  );
}
