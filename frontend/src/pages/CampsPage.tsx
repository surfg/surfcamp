import { useState, useEffect, useCallback } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { SlidersHorizontal, X, ChevronDown, Map } from 'lucide-react';
import { CampCard } from '../components/CampCard';
import { Pagination } from '../components/Pagination';
import { getCamps, getFilterOptions } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfCamp, FilterParams, FilterOptions } from '../types';

const PAGE_SIZE = 12;

export function CampsPage() {
  const { t, language } = useLanguage();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [camps, setCamps] = useState<SurfCamp[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [filters, setFilters] = useState<FilterParams>(() => {
    const params: FilterParams = {};
    const search = searchParams.get('search');
    const country = searchParams.get('country');
    const region = searchParams.get('region');
    if (search) params.search = search;
    if (country) params.country = country;
    if (region) params.region = Number(region);
    return params;
  });
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 500]);
  const [selectedBoardTypes, setSelectedBoardTypes] = useState<number[]>([]);

  // Load filter options
  useEffect(() => {
    getFilterOptions()
      .then((options) => {
        setFilterOptions(options);
        setPriceRange([options.price_range.min, options.price_range.max]);
      })
      .catch(console.error);
  }, []);

  const fetchCamps = useCallback(() => {
    setLoading(true);
    setError(null);

    const apiFilters: FilterParams = { ...filters, page: currentPage };
    if (priceRange[0] > 0) apiFilters.min_price = priceRange[0];
    if (priceRange[1] < (filterOptions?.price_range.max || 500)) apiFilters.max_price = priceRange[1];
    if (selectedBoardTypes.length > 0) {
      (apiFilters as Record<string, unknown>).board_types = selectedBoardTypes.join(',');
    }

    getCamps(apiFilters)
      .then((data) => {
        setCamps(data.results);
        setTotalCount(data.count);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filters, currentPage, priceRange, filterOptions?.price_range.max, selectedBoardTypes]);

  useEffect(() => {
    fetchCamps();
  }, [fetchCamps]);

  const skillLevels = [
    { value: 'beginner', label: t('filters.beginner') },
    { value: 'intermediate', label: t('filters.intermediate') },
    { value: 'advanced', label: t('filters.advanced') },
  ];

  const boardTypes = [
    { id: 1, name: 'Soft tops', name_en: 'Soft tops', name_ru: 'Софттопы' },
    { id: 2, name: 'Longboards', name_en: 'Longboards', name_ru: 'Лонгборды' },
    { id: 3, name: 'Mid lengths', name_en: 'Mid lengths', name_ru: 'Миды' },
    { id: 4, name: 'Shortboards', name_en: 'Shortboards', name_ru: 'Шортборды' },
  ];

  const activeFiltersCount = Object.values(filters).filter(Boolean).length +
    (priceRange[0] > 0 || priceRange[1] < (filterOptions?.price_range.max || 500) ? 1 : 0);

  const clearAllFilters = () => {
    setFilters({});
    setPriceRange([0, filterOptions?.price_range.max || 500]);
    setSelectedBoardTypes([]);
    setCurrentPage(1);
  };

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters, priceRange, selectedBoardTypes]);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handleShowOnMap = () => {
    const params = new URLSearchParams();
    if (filters.country) params.set('country', filters.country);
    if (filters.region) params.set('region', String(filters.region));
    navigate(`/map${params.toString() ? '?' + params.toString() : ''}`);
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Header */}
      <div style={{
        borderBottom: '1px solid #e2e8f0',
        backgroundColor: 'white',
        position: 'sticky',
        top: '72px',
        zIndex: 40
      }}>
        <div style={{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '16px',
          flexWrap: 'wrap'
        }}>
          <div>
            <h1 style={{
              fontSize: '24px',
              fontWeight: 700,
              color: '#0f172a',
              margin: 0
            }}>
              {t('camps.title')}
            </h1>
            <p style={{
              fontSize: '14px',
              color: '#64748b',
              margin: '4px 0 0'
            }}>
              {totalCount} {t('camps.places')}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={handleShowOnMap}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                backgroundColor: 'white',
                fontSize: '14px',
                fontWeight: 500,
                color: '#0ea5e9',
                cursor: 'pointer'
              }}
            >
              <Map style={{ width: '18px', height: '18px' }} />
              {t('nav.map')}
            </button>

            <button
              onClick={() => setShowFilters(!showFilters)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                border: '1px solid #e2e8f0',
                borderRadius: '12px',
                backgroundColor: showFilters ? '#f1f5f9' : 'white',
                fontSize: '14px',
                fontWeight: 500,
                color: '#0f172a',
                cursor: 'pointer'
              }}
            >
              <SlidersHorizontal style={{ width: '18px', height: '18px' }} />
              {t('filters.title')}
              {activeFiltersCount > 0 && (
                <span style={{
                  backgroundColor: '#0f172a',
                  color: 'white',
                  fontSize: '11px',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: '10px'
                }}>
                  {activeFiltersCount}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div style={{
            borderTop: '1px solid #e2e8f0',
            padding: '24px',
            backgroundColor: '#fafafa'
          }}>
            <div style={{
              maxWidth: '1400px',
              margin: '0 auto',
            }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '24px',
              }}>
                {/* Country */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.country')}
                  </label>
                  <div style={{ position: 'relative' }}>
                    <select
                      value={filters.country || ''}
                      onChange={(e) => setFilters(prev => ({
                        ...prev,
                        country: e.target.value || undefined,
                        region: undefined
                      }))}
                      style={{
                        width: '100%',
                        padding: '12px 40px 12px 16px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        backgroundColor: 'white',
                        fontSize: '14px',
                        color: '#0f172a',
                        cursor: 'pointer',
                        appearance: 'none',
                      }}
                    >
                      <option value="">{t('filters.allCountries')}</option>
                      {filterOptions?.countries.map(country => (
                        <option key={country.code} value={country.code}>
                          {language === 'ru' ? country.name : country.name_en} ({country.camps_count})
                        </option>
                      ))}
                    </select>
                    <ChevronDown style={{
                      position: 'absolute',
                      right: '16px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      width: '16px',
                      height: '16px',
                      color: '#64748b',
                      pointerEvents: 'none'
                    }} />
                  </div>
                </div>

                {/* Price Range */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.priceRange')} (${priceRange[0]} - ${priceRange[1]})
                  </label>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <input
                      type="number"
                      value={priceRange[0]}
                      onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                      min={0}
                      max={priceRange[1]}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        fontSize: '14px',
                      }}
                      placeholder="Min"
                    />
                    <span style={{ color: '#94a3b8' }}>-</span>
                    <input
                      type="number"
                      value={priceRange[1]}
                      onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
                      min={priceRange[0]}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        fontSize: '14px',
                      }}
                      placeholder="Max"
                    />
                  </div>
                </div>

                {/* Skill Level */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.skillLevel')}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {skillLevels.map(level => (
                      <button
                        key={level.value}
                        onClick={() => setFilters(prev => ({
                          ...prev,
                          skill_level: prev.skill_level === level.value ? undefined : level.value
                        }))}
                        style={{
                          padding: '10px 16px',
                          borderRadius: '20px',
                          border: filters.skill_level === level.value ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: filters.skill_level === level.value ? '#f0f9ff' : 'white',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: filters.skill_level === level.value ? '#0284c7' : '#0f172a',
                          cursor: 'pointer',
                        }}
                      >
                        {level.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Teaching Language */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {language === 'ru' ? 'Язык обучения' : 'Teaching language'}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {(filterOptions?.languages || []).map(lang => {
                      const active = filters.language === lang.value;
                      const label = language === 'ru' ? lang.label_ru : lang.label;
                      return (
                        <button
                          key={lang.value}
                          onClick={() => setFilters(prev => ({
                            ...prev,
                            language: prev.language === lang.value ? undefined : lang.value
                          }))}
                          style={{
                            padding: '10px 16px',
                            borderRadius: '20px',
                            border: active ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                            backgroundColor: active ? '#f0f9ff' : 'white',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: active ? '#0284c7' : '#0f172a',
                            cursor: 'pointer',
                          }}
                        >
                          {label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Board Types */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.boardTypes')}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {boardTypes.map(type => (
                      <button
                        key={type.id}
                        onClick={() => {
                          setSelectedBoardTypes(prev =>
                            prev.includes(type.id)
                              ? prev.filter(id => id !== type.id)
                              : [...prev, type.id]
                          );
                        }}
                        style={{
                          padding: '10px 16px',
                          borderRadius: '20px',
                          border: selectedBoardTypes.includes(type.id) ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: selectedBoardTypes.includes(type.id) ? '#f0f9ff' : 'white',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: selectedBoardTypes.includes(type.id) ? '#0284c7' : '#0f172a',
                          cursor: 'pointer',
                        }}
                      >
                        {language === 'ru' ? type.name_ru : type.name_en}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Second Row - Features */}
              <div style={{
                display: 'flex',
                flexWrap: 'wrap',
                gap: '24px',
                marginTop: '24px',
                paddingTop: '24px',
                borderTop: '1px solid #e2e8f0'
              }}>
                {/* Amenities */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.amenities')}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {[
                      { key: 'has_pool', label: t('filters.pool') },
                      { key: 'has_yoga', label: t('filters.yoga') },
                      { key: 'has_parties', label: t('filters.parties') },
                      { key: 'has_bed_breakfast', label: t('filters.bedBreakfast') || 'Только проживание' },
                    ].map(amenity => (
                      <button
                        key={amenity.key}
                        onClick={() => setFilters(prev => ({
                          ...prev,
                          [amenity.key]: prev[amenity.key as keyof FilterParams] ? undefined : true
                        }))}
                        style={{
                          padding: '10px 16px',
                          borderRadius: '20px',
                          border: filters[amenity.key as keyof FilterParams] ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: filters[amenity.key as keyof FilterParams] ? '#f0f9ff' : 'white',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: filters[amenity.key as keyof FilterParams] ? '#0284c7' : '#0f172a',
                          cursor: 'pointer',
                        }}
                      >
                        {amenity.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Board Rental */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {t('filters.boardRental')}
                  </label>
                  <button
                    onClick={() => setFilters(prev => ({
                      ...prev,
                      board_rental: prev.board_rental ? undefined : true
                    }))}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '20px',
                      border: filters.board_rental ? '2px solid #10b981' : '1px solid #e2e8f0',
                      backgroundColor: filters.board_rental ? '#dcfce7' : 'white',
                      fontSize: '14px',
                      fontWeight: 500,
                      color: filters.board_rental ? '#166534' : '#0f172a',
                      cursor: 'pointer',
                    }}
                  >
                    {t('filters.boardRental')}
                  </button>
                </div>

                {/* Bed & Breakfast */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    B&B
                  </label>
                  <button
                    onClick={() => setFilters(prev => ({
                      ...prev,
                      has_bed_breakfast: prev.has_bed_breakfast ? undefined : true
                    }))}
                    style={{
                      padding: '10px 16px',
                      borderRadius: '20px',
                      border: filters.has_bed_breakfast ? '2px solid #f59e0b' : '1px solid #e2e8f0',
                      backgroundColor: filters.has_bed_breakfast ? '#fef3c7' : 'white',
                      fontSize: '14px',
                      fontWeight: 500,
                      color: filters.has_bed_breakfast ? '#92400e' : '#0f172a',
                      cursor: 'pointer',
                    }}
                  >
                    {t('filters.bedBreakfast')}
                  </button>
                </div>

                {/* Clear Filters */}
                {activeFiltersCount > 0 && (
                  <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                    <button
                      onClick={clearAllFilters}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '10px 16px',
                        border: 'none',
                        backgroundColor: 'transparent',
                        fontSize: '14px',
                        fontWeight: 500,
                        color: '#dc2626',
                        cursor: 'pointer'
                      }}
                    >
                      <X style={{ width: '16px', height: '16px' }} />
                      {t('filters.clearAll')}
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
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
              :(
            </div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 600,
              color: '#0f172a',
              margin: '0 0 8px'
            }}>
              {t('camps.error')}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#64748b',
              margin: '0 0 24px'
            }}>
              {error}
            </p>
            <button
              onClick={fetchCamps}
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
              {t('camps.tryAgain')}
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
                <div style={{ height: '18px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '80%', marginBottom: '8px' }} />
                <div style={{ height: '14px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '40%' }} />
              </div>
            ))}
          </div>
        ) : camps.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '80px 24px'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              backgroundColor: '#f1f5f9',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
              fontSize: '28px'
            }}>
              :(
            </div>
            <h3 style={{
              fontSize: '18px',
              fontWeight: 600,
              color: '#0f172a',
              margin: '0 0 8px'
            }}>
              {t('camps.noResults')}
            </h3>
            <p style={{
              fontSize: '14px',
              color: '#64748b',
              margin: 0
            }}>
              {t('camps.adjustFilters')}
            </p>
          </div>
        ) : (
          <>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '24px'
            }}>
              {camps.map((camp) => (
                <CampCard key={camp.id} camp={camp} />
              ))}
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              totalCount={totalCount}
              pageSize={PAGE_SIZE}
            />
          </>
        )}
      </div>
    </div>
  );
}
