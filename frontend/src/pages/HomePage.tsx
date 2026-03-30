import { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Star, ArrowRight, Waves, Map, Building2, X } from 'lucide-react';
import { CampCard } from '../components/CampCard';
import { getFeaturedCamps, searchAutocomplete, getCountries } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfCamp, SearchResult, Country } from '../types';

export function HomePage() {
  const { t } = useLanguage();
  const [featuredCamps, setFeaturedCamps] = useState<SurfCamp[]>([]);
  const [countries, setCountries] = useState<Country[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedDestination, setSelectedDestination] = useState<SearchResult | null>(null);
  const navigate = useNavigate();
  const searchRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    Promise.all([getFeaturedCamps(), getCountries()])
      .then(([camps, countriesData]) => {
        setFeaturedCamps(camps);
        setCountries(countriesData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchInput = useCallback((value: string) => {
    setSearchQuery(value);
    setSelectedDestination(null);

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (value.length < 2) {
      setSearchResults([]);
      setIsSearchOpen(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setSearchLoading(true);
      try {
        const data = await searchAutocomplete(value);
        setSearchResults(data.results);
        setIsSearchOpen(true);
      } catch (err) {
        console.error('Search error:', err);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
  }, []);

  const handleSelectResult = (result: SearchResult) => {
    setSelectedDestination(result);
    setSearchQuery(result.name);
    setIsSearchOpen(false);

    if (result.type === 'camp') {
      navigate(`/camps/${result.slug}`);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedDestination) {
      if (selectedDestination.type === 'country') {
        navigate(`/camps?country=${selectedDestination.code}`);
      } else if (selectedDestination.type === 'region') {
        navigate(`/camps?region=${selectedDestination.id}`);
      } else if (selectedDestination.type === 'camp') {
        navigate(`/camps/${selectedDestination.slug}`);
      }
    } else if (searchQuery.trim()) {
      navigate(`/camps?search=${encodeURIComponent(searchQuery.trim())}`);
    } else {
      navigate('/camps');
    }
  };

  const handleShowOnMap = () => {
    if (selectedDestination) {
      if (selectedDestination.type === 'country') {
        navigate(`/map?country=${selectedDestination.code}`);
      } else if (selectedDestination.type === 'region') {
        navigate(`/map?region=${selectedDestination.id}`);
      }
    } else {
      navigate('/map');
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSelectedDestination(null);
    setSearchResults([]);
    setIsSearchOpen(false);
  };

  const totalCamps = countries.reduce((acc, c) => acc + (c.camps_count || 0), 0);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Hero Section */}
      <section style={{
        position: 'relative',
        minHeight: '85vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #0c4a6e 0%, #0369a1 50%, #0ea5e9 100%)',
        overflow: 'hidden'
      }}>
        {/* Background Pattern */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          opacity: 0.5
        }} />

        {/* Hero Content */}
        <div style={{
          position: 'relative',
          zIndex: 10,
          width: '100%',
          maxWidth: '800px',
          margin: '0 auto',
          padding: '40px 24px',
          textAlign: 'center'
        }}>
          <h1 style={{
            fontSize: 'clamp(36px, 8vw, 64px)',
            fontWeight: 800,
            color: 'white',
            lineHeight: 1.1,
            marginBottom: '24px',
            letterSpacing: '-0.02em'
          }}>
            {t('hero.title1')}<br />
            <span style={{ color: '#7dd3fc' }}>{t('hero.title2')}</span>
          </h1>

          <p style={{
            fontSize: 'clamp(16px, 3vw, 20px)',
            color: 'rgba(255,255,255,0.9)',
            marginBottom: '40px',
            maxWidth: '600px',
            margin: '0 auto 40px'
          }}>
            {t('hero.subtitle')}
          </p>

          {/* Enhanced Search Bar with Autocomplete */}
          <div ref={searchRef} style={{ position: 'relative', maxWidth: '600px', margin: '0 auto 48px' }}>
            <form onSubmit={handleSearch} style={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: 'white',
              borderRadius: '60px',
              padding: '6px 6px 6px 24px',
              boxShadow: '0 8px 32px rgba(0,0,0,0.2)'
            }}>
              <MapPin style={{ width: '20px', height: '20px', color: '#94a3b8', flexShrink: 0 }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => handleSearchInput(e.target.value)}
                onFocus={() => searchResults.length > 0 && setIsSearchOpen(true)}
                placeholder={t('hero.searchPlaceholder')}
                style={{
                  flex: 1,
                  padding: '14px 16px',
                  border: 'none',
                  outline: 'none',
                  fontSize: '16px',
                  color: '#0f172a',
                  backgroundColor: 'transparent'
                }}
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: '8px',
                    marginRight: '8px',
                  }}
                >
                  <X style={{ width: '18px', height: '18px', color: '#94a3b8' }} />
                </button>
              )}
              <button
                type="button"
                onClick={handleShowOnMap}
                title={t('search.showOnMap')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: '12px',
                  backgroundColor: '#f8fafc',
                  border: 'none',
                  borderRadius: '50%',
                  cursor: 'pointer',
                  marginRight: '8px',
                }}
              >
                <Map style={{ width: '20px', height: '20px', color: '#0ea5e9' }} />
              </button>
              <button
                type="submit"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '14px 28px',
                  backgroundColor: '#0ea5e9',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50px',
                  fontSize: '16px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'background 0.2s'
                }}
              >
                <Search style={{ width: '18px', height: '18px' }} />
                <span className="hidden sm:inline">{t('hero.search')}</span>
              </button>
            </form>

            {/* Search Autocomplete Dropdown */}
            {isSearchOpen && searchResults.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                marginTop: '8px',
                backgroundColor: 'white',
                borderRadius: '16px',
                boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
                overflow: 'hidden',
                zIndex: 100,
                maxHeight: '400px',
                overflowY: 'auto',
              }}>
                {searchResults.map((result, index) => (
                  <div
                    key={`${result.type}-${result.id}`}
                    onClick={() => handleSelectResult(result)}
                    style={{
                      padding: '14px 20px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '14px',
                      cursor: 'pointer',
                      backgroundColor: 'white',
                      borderBottom: index < searchResults.length - 1 ? '1px solid #f1f5f9' : 'none',
                      transition: 'background-color 0.15s',
                    }}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = 'white'}
                  >
                    {/* Icon */}
                    <div style={{
                      width: '44px',
                      height: '44px',
                      borderRadius: '12px',
                      backgroundColor: result.type === 'country' ? '#dbeafe' : result.type === 'region' ? '#dcfce7' : '#fef3c7',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      {result.type === 'country' && <MapPin style={{ width: '22px', height: '22px', color: '#2563eb' }} />}
                      {result.type === 'region' && <Building2 style={{ width: '22px', height: '22px', color: '#16a34a' }} />}
                      {result.type === 'camp' && <Waves style={{ width: '22px', height: '22px', color: '#d97706' }} />}
                    </div>

                    {/* Content */}
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a' }}>
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
                        <div style={{ fontSize: '16px', fontWeight: 700, color: '#0f172a' }}>
                          ${result.price_per_night}
                        </div>
                        <div style={{ fontSize: '12px', color: '#64748b' }}>{t('search.perNight')}</div>
                      </div>
                    )}

                    {/* Type badge */}
                    <div style={{
                      padding: '4px 10px',
                      borderRadius: '8px',
                      backgroundColor: result.type === 'country' ? '#dbeafe' : result.type === 'region' ? '#dcfce7' : '#fef3c7',
                      fontSize: '11px',
                      fontWeight: 600,
                      color: result.type === 'country' ? '#2563eb' : result.type === 'region' ? '#16a34a' : '#d97706',
                      textTransform: 'uppercase',
                    }}>
                      {t(`search.${result.type}`)}
                    </div>
                  </div>
                ))}

                {/* Show on Map Option */}
                <div
                  onClick={handleShowOnMap}
                  style={{
                    padding: '14px 20px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '14px',
                    cursor: 'pointer',
                    backgroundColor: '#f8fafc',
                    borderTop: '1px solid #e2e8f0',
                  }}
                  onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f1f5f9'}
                  onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#f8fafc'}
                >
                  <div style={{
                    width: '44px',
                    height: '44px',
                    borderRadius: '12px',
                    backgroundColor: '#e0f2fe',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <Map style={{ width: '22px', height: '22px', color: '#0284c7' }} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '15px', fontWeight: 600, color: '#0284c7' }}>
                      {t('search.showOnMap')}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Loading indicator */}
            {searchLoading && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                marginTop: '8px',
                backgroundColor: 'white',
                borderRadius: '16px',
                boxShadow: '0 4px 24px rgba(0,0,0,0.15)',
                padding: '24px',
                textAlign: 'center',
                zIndex: 100,
              }}>
                <div style={{
                  width: '28px',
                  height: '28px',
                  border: '3px solid #e2e8f0',
                  borderTopColor: '#0ea5e9',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite',
                  margin: '0 auto',
                }} />
              </div>
            )}
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '48px',
            flexWrap: 'wrap'
          }}>
            {[
              { value: `${totalCamps || '50'}+`, label: t('stats.surfCamps') },
              { value: String(countries.length || 15), label: t('stats.countries') },
              { value: '4.8', label: t('stats.avgRating'), icon: true }
            ].map(stat => (
              <div key={stat.label} style={{ textAlign: 'center' }}>
                <div style={{
                  fontSize: '32px',
                  fontWeight: 700,
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}>
                  {stat.icon && <Star style={{ width: '24px', height: '24px', fill: '#fbbf24', color: '#fbbf24' }} />}
                  {stat.value}
                </div>
                <div style={{ fontSize: '14px', color: 'rgba(255,255,255,0.8)' }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Wave Bottom */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0
        }}>
          <svg viewBox="0 0 1440 120" fill="none" style={{ display: 'block', width: '100%' }}>
            <path
              d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H0V120Z"
              fill="white"
            />
          </svg>
        </div>
      </section>

      {/* Featured Camps Section */}
      <section style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '80px 24px'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '32px',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div>
            <h2 style={{
              fontSize: '28px',
              fontWeight: 700,
              color: '#0f172a',
              margin: 0
            }}>
              {t('featured.title')}
            </h2>
            <p style={{
              fontSize: '16px',
              color: '#64748b',
              margin: '8px 0 0'
            }}>
              {t('featured.subtitle')}
            </p>
          </div>
          <Link
            to="/camps"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#0f172a',
              textDecoration: 'none',
              fontSize: '15px',
              fontWeight: 600
            }}
          >
            {t('featured.viewAll')}
            <ArrowRight style={{ width: '18px', height: '18px' }} />
          </Link>
        </div>

        {loading ? (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {[1, 2, 3].map((i) => (
              <div key={i} style={{
                borderRadius: '16px',
                overflow: 'hidden'
              }}>
                <div style={{
                  aspectRatio: '4/3',
                  backgroundColor: '#f1f5f9',
                  animation: 'pulse 2s infinite'
                }} />
                <div style={{ padding: '16px 0' }}>
                  <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '60%', marginBottom: '12px' }} />
                  <div style={{ height: '18px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '80%', marginBottom: '8px' }} />
                  <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '40%' }} />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {featuredCamps.map((camp) => (
              <CampCard key={camp.id} camp={camp} />
            ))}
          </div>
        )}
      </section>

      {/* CTA Section */}
      <section style={{
        backgroundColor: '#f8fafc',
        padding: '80px 24px'
      }}>
        <div style={{
          maxWidth: '800px',
          margin: '0 auto',
          textAlign: 'center'
        }}>
          <h2 style={{
            fontSize: 'clamp(24px, 5vw, 36px)',
            fontWeight: 700,
            color: '#0f172a',
            marginBottom: '16px'
          }}>
            {t('cta.title')}
          </h2>
          <p style={{
            fontSize: '18px',
            color: '#64748b',
            marginBottom: '32px'
          }}>
            {t('cta.subtitle')}
          </p>
          <Link
            to="/camps"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '10px',
              padding: '16px 32px',
              backgroundColor: '#0f172a',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '12px',
              fontSize: '16px',
              fontWeight: 600,
              transition: 'background 0.2s'
            }}
          >
            {t('cta.button')}
            <ArrowRight style={{ width: '20px', height: '20px' }} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{
        backgroundColor: '#0f172a',
        padding: '48px 24px'
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px'
          }}>
            <div style={{
              width: '36px',
              height: '36px',
              background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Waves style={{ width: '20px', height: '20px', color: 'white' }} />
            </div>
            <span style={{ fontSize: '18px', fontWeight: 700, color: 'white' }}>
              SurfSelect
            </span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '14px', margin: 0 }}>
            © 2024 SurfSelect. {t('footer.rights')}
          </p>
        </div>
      </footer>
    </div>
  );
}
