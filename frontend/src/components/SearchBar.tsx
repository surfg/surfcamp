import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Building2, Waves, Calendar, Users, X } from 'lucide-react';
import { searchAutocomplete } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SearchResult } from '../types';

interface SearchBarProps {
  variant?: 'hero' | 'header' | 'page';
  onSearch?: (params: { destination?: string; checkIn?: string; checkOut?: string; guests?: number }) => void;
}

export function SearchBar({ variant = 'hero', onSearch }: SearchBarProps) {
  const navigate = useNavigate();
  const { language, t } = useLanguage();
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [checkIn, setCheckIn] = useState('');
  const [checkOut, setCheckOut] = useState('');
  const [guests, setGuests] = useState(2);
  const [showGuestPicker, setShowGuestPicker] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState<SearchResult | null>(null);

  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowGuestPicker(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  const handleSearch = useCallback((value: string) => {
    setQuery(value);
    if (debounceRef.current) clearTimeout(debounceRef.current as ReturnType<typeof setTimeout>);

    if (value.length < 2) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setLoading(true);
      try {
        const data = await searchAutocomplete(value, language);
        setResults(data.results);
        setIsOpen(true);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setLoading(false);
      }
    }, 300);
  }, [language]);

  const handleSelectResult = (result: SearchResult) => {
    setSelectedDestination(result);
    setQuery(result.name);
    setIsOpen(false);

    // If it's a camp, navigate directly
    if (result.type === 'camp') {
      navigate(`/camps/${result.slug}`);
    }
  };

  const handleSubmit = () => {
    const params: Record<string, string> = {};

    if (selectedDestination) {
      if (selectedDestination.type === 'country') {
        params.country = selectedDestination.code;
      } else if (selectedDestination.type === 'region') {
        params.region = String(selectedDestination.id);
      }
    } else if (query) {
      params.search = query;
    }

    if (checkIn) params.check_in = checkIn;
    if (checkOut) params.check_out = checkOut;
    if (guests) params.guests = String(guests);

    if (onSearch) {
      onSearch({ destination: query, checkIn, checkOut, guests });
    } else {
      const searchParams = new URLSearchParams(params);
      navigate(`/camps?${searchParams.toString()}`);
    }
  };

  const clearDestination = () => {
    setQuery('');
    setSelectedDestination(null);
    setResults([]);
  };

  const getMinCheckOut = () => {
    if (!checkIn) return '';
    const date = new Date(checkIn);
    date.setDate(date.getDate() + 1);
    return date.toISOString().split('T')[0];
  };

  const isCompact = variant === 'header';

  const containerStyle: React.CSSProperties = isCompact
    ? {
        display: 'flex',
        alignItems: 'center',
        backgroundColor: '#f8fafc',
        borderRadius: '40px',
        padding: '6px 6px 6px 20px',
        border: '1px solid #e2e8f0',
        maxWidth: '500px',
      }
    : {
        backgroundColor: 'white',
        borderRadius: '16px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.12)',
        padding: '8px',
      };

  return (
    <div ref={searchRef} style={{ position: 'relative', width: '100%' }}>
      <div style={containerStyle}>
        {isCompact ? (
          // Compact header version
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
            <Search style={{ width: '18px', height: '18px', color: '#64748b' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => handleSearch(e.target.value)}
              onFocus={() => results.length > 0 && setIsOpen(true)}
              placeholder={t('search.searchDest')}
              style={{
                border: 'none',
                background: 'transparent',
                fontSize: '14px',
                outline: 'none',
                flex: 1,
                minWidth: '150px',
              }}
            />
            <button
              onClick={handleSubmit}
              style={{
                backgroundColor: '#0ea5e9',
                color: 'white',
                border: 'none',
                borderRadius: '50%',
                width: '36px',
                height: '36px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
              }}
            >
              <Search style={{ width: '16px', height: '16px' }} />
            </button>
          </div>
        ) : (
          // Full search bar
          <div style={{
            display: 'grid',
            gridTemplateColumns: variant === 'hero' ? '2fr 1fr 1fr 1fr auto' : '1fr',
            gap: '4px',
            alignItems: 'center',
          }}>
            {/* Destination */}
            <div style={{
              position: 'relative',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: isOpen ? '#f8fafc' : 'transparent',
              transition: 'background-color 0.2s',
            }}>
              <label style={{
                display: 'block',
                fontSize: '12px',
                fontWeight: 600,
                color: '#64748b',
                marginBottom: '4px',
              }}>
                {t('search.destination')}
              </label>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <MapPin style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => handleSearch(e.target.value)}
                  onFocus={() => results.length > 0 && setIsOpen(true)}
                  placeholder={t('search.whereTo')}
                  style={{
                    border: 'none',
                    background: 'transparent',
                    fontSize: '15px',
                    fontWeight: 500,
                    color: '#0f172a',
                    outline: 'none',
                    flex: 1,
                    width: '100%',
                  }}
                />
                {query && (
                  <button
                    onClick={clearDestination}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '4px',
                      display: 'flex',
                    }}
                  >
                    <X style={{ width: '16px', height: '16px', color: '#94a3b8' }} />
                  </button>
                )}
              </div>
            </div>

            {variant === 'hero' && (
              <>
                {/* Divider */}
                <div style={{ width: '1px', height: '40px', backgroundColor: '#e2e8f0' }} />

                {/* Check-in */}
                <div style={{ padding: '12px 16px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '4px',
                  }}>
                    {t('search.checkIn')}
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Calendar style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                    <input
                      type="date"
                      value={checkIn}
                      onChange={(e) => setCheckIn(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      style={{
                        border: 'none',
                        background: 'transparent',
                        fontSize: '15px',
                        fontWeight: 500,
                        color: checkIn ? '#0f172a' : '#94a3b8',
                        outline: 'none',
                        cursor: 'pointer',
                      }}
                    />
                  </div>
                </div>

                {/* Check-out */}
                <div style={{ padding: '12px 16px' }}>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '4px',
                  }}>
                    {t('search.checkOut')}
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Calendar style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                    <input
                      type="date"
                      value={checkOut}
                      onChange={(e) => setCheckOut(e.target.value)}
                      min={getMinCheckOut()}
                      disabled={!checkIn}
                      style={{
                        border: 'none',
                        background: 'transparent',
                        fontSize: '15px',
                        fontWeight: 500,
                        color: checkOut ? '#0f172a' : '#94a3b8',
                        outline: 'none',
                        cursor: checkIn ? 'pointer' : 'not-allowed',
                        opacity: checkIn ? 1 : 0.5,
                      }}
                    />
                  </div>
                </div>

                {/* Guests */}
                <div
                  style={{
                    padding: '12px 16px',
                    borderRadius: '12px',
                    backgroundColor: showGuestPicker ? '#f8fafc' : 'transparent',
                    cursor: 'pointer',
                    position: 'relative',
                  }}
                  onClick={() => setShowGuestPicker(!showGuestPicker)}
                >
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '4px',
                  }}>
                    {t('search.guests')}
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Users style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                    <span style={{ fontSize: '15px', fontWeight: 500, color: '#0f172a' }}>
                      {guests} {language === 'ru' ? (guests === 1 ? 'гость' : guests < 5 ? 'гостя' : 'гостей') : (guests === 1 ? 'guest' : 'guests')}
                    </span>
                  </div>

                  {/* Guest picker dropdown */}
                  {showGuestPicker && (
                    <div
                      onClick={(e) => e.stopPropagation()}
                      style={{
                        position: 'absolute',
                        top: '100%',
                        right: 0,
                        marginTop: '8px',
                        backgroundColor: 'white',
                        borderRadius: '12px',
                        boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
                        padding: '16px',
                        minWidth: '200px',
                        zIndex: 50,
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <span style={{ fontSize: '14px', fontWeight: 500 }}>Guests</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <button
                            onClick={() => setGuests(Math.max(1, guests - 1))}
                            disabled={guests <= 1}
                            style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '50%',
                              border: '1px solid #e2e8f0',
                              backgroundColor: 'white',
                              cursor: guests <= 1 ? 'not-allowed' : 'pointer',
                              opacity: guests <= 1 ? 0.5 : 1,
                              fontSize: '18px',
                            }}
                          >
                            -
                          </button>
                          <span style={{ fontSize: '16px', fontWeight: 600, minWidth: '24px', textAlign: 'center' }}>
                            {guests}
                          </span>
                          <button
                            onClick={() => setGuests(Math.min(10, guests + 1))}
                            disabled={guests >= 10}
                            style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '50%',
                              border: '1px solid #e2e8f0',
                              backgroundColor: 'white',
                              cursor: guests >= 10 ? 'not-allowed' : 'pointer',
                              opacity: guests >= 10 ? 0.5 : 1,
                              fontSize: '18px',
                            }}
                          >
                            +
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Search button */}
                <button
                  onClick={handleSubmit}
                  style={{
                    backgroundColor: '#0ea5e9',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '16px 24px',
                    fontSize: '15px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    transition: 'background-color 0.2s',
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#0284c7'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#0ea5e9'}
                >
                  <Search style={{ width: '18px', height: '18px' }} />
                  {t('hero.search')}
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Autocomplete dropdown */}
      {isOpen && results.length > 0 && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '8px',
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          overflow: 'hidden',
          zIndex: 100,
          maxHeight: '400px',
          overflowY: 'auto',
        }}>
          {results.map((result, index) => (
            <div
              key={`${result.type}-${result.id}`}
              onClick={() => handleSelectResult(result)}
              style={{
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                cursor: 'pointer',
                backgroundColor: 'white',
                borderBottom: index < results.length - 1 ? '1px solid #f1f5f9' : 'none',
                transition: 'background-color 0.15s',
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
            >
              {/* Icon */}
              <div style={{
                width: '40px',
                height: '40px',
                borderRadius: '10px',
                backgroundColor: result.type === 'country' ? '#dbeafe' : result.type === 'region' ? '#dcfce7' : '#fef3c7',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}>
                {result.type === 'country' && <MapPin style={{ width: '20px', height: '20px', color: '#2563eb' }} />}
                {result.type === 'region' && <Building2 style={{ width: '20px', height: '20px', color: '#16a34a' }} />}
                {result.type === 'camp' && <Waves style={{ width: '20px', height: '20px', color: '#d97706' }} />}
              </div>

              {/* Content */}
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '15px', fontWeight: 500, color: '#0f172a' }}>
                  {result.name}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>
                  {result.type === 'country' && `${result.camps_count} ${t('search.camps')}`}
                  {result.type === 'region' && `${result.country_name} · ${result.camps_count} ${t('search.camps')}`}
                  {result.type === 'camp' && `${result.region_name}, ${result.country_name}`}
                </div>
              </div>

              {/* Price for camps */}
              {result.type === 'camp' && (
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>
                    ${result.price_per_night}
                  </div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>{t('search.perNight')}</div>
                </div>
              )}

              {/* Type badge */}
              <div style={{
                padding: '4px 8px',
                borderRadius: '6px',
                backgroundColor: result.type === 'country' ? '#dbeafe' : result.type === 'region' ? '#dcfce7' : '#fef3c7',
                fontSize: '11px',
                fontWeight: 600,
                color: result.type === 'country' ? '#2563eb' : result.type === 'region' ? '#16a34a' : '#d97706',
                textTransform: 'uppercase',
              }}>
                {result.type === 'country' ? t('search.country') : result.type === 'region' ? t('search.region') : t('search.camp')}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Loading indicator */}
      {loading && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: 0,
          right: 0,
          marginTop: '8px',
          backgroundColor: 'white',
          borderRadius: '16px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.15)',
          padding: '24px',
          textAlign: 'center',
          zIndex: 100,
        }}>
          <div style={{
            width: '24px',
            height: '24px',
            border: '2px solid #e2e8f0',
            borderTopColor: '#0ea5e9',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto',
          }} />
        </div>
      )}
    </div>
  );
}
