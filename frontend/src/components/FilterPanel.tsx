import { useState, useEffect } from 'react';
import { X, ChevronDown, ChevronUp, Star } from 'lucide-react';
import { getFilterOptions } from '../lib/api';
import type { FilterParams, FilterOptions } from '../types';

interface FilterPanelProps {
  filters: FilterParams;
  onFilterChange: (filters: FilterParams) => void;
  onClose?: () => void;
  isModal?: boolean;
}

export function FilterPanel({ filters, onFilterChange, onClose, isModal = false }: FilterPanelProps) {
  const [options, setOptions] = useState<FilterOptions | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    price: true,
    skill: true,
    amenities: true,
    rating: false,
  });

  useEffect(() => {
    getFilterOptions()
      .then(setOptions)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

  const updateFilter = <K extends keyof FilterParams>(key: K, value: FilterParams[K]) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const clearFilters = () => {
    onFilterChange({});
  };

  const activeFiltersCount = Object.entries(filters).filter(([_, v]) => v !== undefined && v !== '').length;

  const containerStyle: React.CSSProperties = isModal
    ? {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.5)',
        zIndex: 100,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '24px',
      }
    : {};

  const panelStyle: React.CSSProperties = isModal
    ? {
        backgroundColor: 'white',
        borderRadius: '24px',
        width: '100%',
        maxWidth: '600px',
        maxHeight: '90vh',
        overflow: 'auto',
      }
    : {
        backgroundColor: 'white',
        borderRadius: '16px',
        border: '1px solid #e2e8f0',
      };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={{ ...panelStyle, padding: '40px', textAlign: 'center' }}>
          <div style={{
            width: '32px',
            height: '32px',
            border: '3px solid #e2e8f0',
            borderTopColor: '#0ea5e9',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto',
          }} />
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle} onClick={isModal ? onClose : undefined}>
      <div style={panelStyle} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          backgroundColor: 'white',
          zIndex: 10,
          borderRadius: isModal ? '24px 24px 0 0' : undefined,
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>Filters</h3>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {activeFiltersCount > 0 && (
              <button
                onClick={clearFilters}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '14px',
                  color: '#dc2626',
                  cursor: 'pointer',
                  fontWeight: 500,
                }}
              >
                Clear all ({activeFiltersCount})
              </button>
            )}
            {isModal && onClose && (
              <button
                onClick={onClose}
                style={{
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '8px',
                  display: 'flex',
                }}
              >
                <X style={{ width: '24px', height: '24px' }} />
              </button>
            )}
          </div>
        </div>

        <div style={{ padding: '8px 0' }}>
          {/* Price Range */}
          <div style={{ borderBottom: '1px solid #f1f5f9' }}>
            <button
              onClick={() => toggleSection('price')}
              style={{
                width: '100%',
                padding: '16px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>Price range</span>
              {expandedSections.price ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {expandedSections.price && (
              <div style={{ padding: '0 24px 20px' }}>
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '6px' }}>
                      Min price
                    </label>
                    <div style={{ position: 'relative' }}>
                      <span style={{
                        position: 'absolute',
                        left: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: '#64748b',
                      }}>$</span>
                      <input
                        type="number"
                        value={filters.min_price || ''}
                        onChange={(e) => updateFilter('min_price', e.target.value ? Number(e.target.value) : undefined)}
                        placeholder={String(options?.price_range.min || 0)}
                        style={{
                          width: '100%',
                          padding: '10px 12px 10px 28px',
                          border: '1px solid #e2e8f0',
                          borderRadius: '10px',
                          fontSize: '14px',
                        }}
                      />
                    </div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <label style={{ fontSize: '12px', color: '#64748b', display: 'block', marginBottom: '6px' }}>
                      Max price
                    </label>
                    <div style={{ position: 'relative' }}>
                      <span style={{
                        position: 'absolute',
                        left: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: '#64748b',
                      }}>$</span>
                      <input
                        type="number"
                        value={filters.max_price || ''}
                        onChange={(e) => updateFilter('max_price', e.target.value ? Number(e.target.value) : undefined)}
                        placeholder={String(options?.price_range.max || 500)}
                        style={{
                          width: '100%',
                          padding: '10px 12px 10px 28px',
                          border: '1px solid #e2e8f0',
                          borderRadius: '10px',
                          fontSize: '14px',
                        }}
                      />
                    </div>
                  </div>
                </div>
                {/* Quick price buttons */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {[50, 100, 150, 200, 300].map(price => (
                    <button
                      key={price}
                      onClick={() => updateFilter('max_price', filters.max_price === price ? undefined : price)}
                      style={{
                        padding: '8px 16px',
                        borderRadius: '20px',
                        border: filters.max_price === price ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                        backgroundColor: filters.max_price === price ? '#f0f9ff' : 'white',
                        fontSize: '13px',
                        fontWeight: 500,
                        color: filters.max_price === price ? '#0ea5e9' : '#0f172a',
                        cursor: 'pointer',
                      }}
                    >
                      Under ${price}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Skill Level */}
          <div style={{ borderBottom: '1px solid #f1f5f9' }}>
            <button
              onClick={() => toggleSection('skill')}
              style={{
                width: '100%',
                padding: '16px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>Skill level</span>
              {expandedSections.skill ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {expandedSections.skill && (
              <div style={{ padding: '0 24px 20px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {(options?.skill_levels || []).map(level => (
                    <button
                      key={level.value}
                      onClick={() => updateFilter('skill_level', filters.skill_level === level.value ? undefined : level.value)}
                      style={{
                        padding: '10px 20px',
                        borderRadius: '20px',
                        border: filters.skill_level === level.value ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                        backgroundColor: filters.skill_level === level.value ? '#f0f9ff' : 'white',
                        fontSize: '14px',
                        fontWeight: 500,
                        color: filters.skill_level === level.value ? '#0ea5e9' : '#0f172a',
                        cursor: 'pointer',
                      }}
                    >
                      {level.label}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Amenities & Features */}
          <div style={{ borderBottom: '1px solid #f1f5f9' }}>
            <button
              onClick={() => toggleSection('amenities')}
              style={{
                width: '100%',
                padding: '16px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>Amenities</span>
              {expandedSections.amenities ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {expandedSections.amenities && (
              <div style={{ padding: '0 24px 20px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                  {(options?.features || []).map(feature => {
                    const isActive = filters[feature.key as keyof FilterParams];
                    return (
                      <label
                        key={feature.key}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          border: isActive ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: isActive ? '#f0f9ff' : 'white',
                          cursor: 'pointer',
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={!!isActive}
                          onChange={(e) => updateFilter(feature.key as keyof FilterParams, e.target.checked ? true : undefined)}
                          style={{
                            width: '20px',
                            height: '20px',
                            accentColor: '#0ea5e9',
                          }}
                        />
                        <span style={{ fontSize: '14px', fontWeight: 500 }}>{feature.label}</span>
                      </label>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Rating */}
          <div style={{ borderBottom: '1px solid #f1f5f9' }}>
            <button
              onClick={() => toggleSection('rating')}
              style={{
                width: '100%',
                padding: '16px 24px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
              }}
            >
              <span style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>Rating</span>
              {expandedSections.rating ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </button>
            {expandedSections.rating && (
              <div style={{ padding: '0 24px 20px' }}>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {[4.5, 4, 3.5, 3].map(rating => (
                    <button
                      key={rating}
                      onClick={() => updateFilter('min_rating', filters.min_rating === rating ? undefined : rating)}
                      style={{
                        padding: '10px 16px',
                        borderRadius: '20px',
                        border: filters.min_rating === rating ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                        backgroundColor: filters.min_rating === rating ? '#f0f9ff' : 'white',
                        fontSize: '14px',
                        fontWeight: 500,
                        color: filters.min_rating === rating ? '#0ea5e9' : '#0f172a',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                      }}
                    >
                      <Star style={{ width: '14px', height: '14px', fill: '#fbbf24', color: '#fbbf24' }} />
                      {rating}+
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Country */}
          {options?.countries && options.countries.length > 0 && (
            <div style={{ borderBottom: '1px solid #f1f5f9' }}>
              <div style={{ padding: '16px 24px' }}>
                <label style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', display: 'block', marginBottom: '12px' }}>
                  Country
                </label>
                <select
                  value={filters.country || ''}
                  onChange={(e) => updateFilter('country', e.target.value || undefined)}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    fontSize: '14px',
                    backgroundColor: 'white',
                    cursor: 'pointer',
                  }}
                >
                  <option value="">All countries</option>
                  {options.countries.map(country => (
                    <option key={country.code} value={country.code}>
                      {country.name_en || country.name} ({country.camps_count})
                    </option>
                  ))}
                </select>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {isModal && (
          <div style={{
            padding: '16px 24px',
            borderTop: '1px solid #e2e8f0',
            display: 'flex',
            justifyContent: 'space-between',
            position: 'sticky',
            bottom: 0,
            backgroundColor: 'white',
            borderRadius: isModal ? '0 0 24px 24px' : undefined,
          }}>
            <button
              onClick={clearFilters}
              style={{
                padding: '14px 24px',
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Clear all
            </button>
            <button
              onClick={onClose}
              style={{
                padding: '14px 32px',
                backgroundColor: '#0f172a',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              Show results
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
