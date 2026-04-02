import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { SlidersHorizontal, X, ChevronDown, MapPin, Star, Clock, Users } from 'lucide-react';
import { getLessons, getLessonFilters } from '../lib/api';
import { Pagination } from '../components/Pagination';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfLesson, LessonFilterOptions, FilterParams } from '../types';

const PAGE_SIZE = 12;

export function LessonsPage() {
  const { t, language } = useLanguage();
  const [lessons, setLessons] = useState<SurfLesson[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [filterOptions, setFilterOptions] = useState<LessonFilterOptions | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // Filter state
  const [filters, setFilters] = useState<FilterParams>({});
  const [lessonType, setLessonType] = useState<string>('');
  const [skillLevel, setSkillLevel] = useState<string>('');
  const [priceRange, setPriceRange] = useState<[number, number]>([0, 500]);

  // Load filter options
  useEffect(() => {
    getLessonFilters()
      .then((options) => {
        setFilterOptions(options);
        setPriceRange([options.price_range.min, options.price_range.max]);
      })
      .catch(console.error);
  }, []);

  const fetchLessons = useCallback(() => {
    setLoading(true);
    setError(null);

    const apiFilters: FilterParams = { ...filters, page: currentPage };
    if (lessonType) (apiFilters as Record<string, unknown>).lesson_type = lessonType;
    if (skillLevel) apiFilters.skill_level = skillLevel;
    if (priceRange[0] > 0) apiFilters.min_price = priceRange[0];
    if (priceRange[1] < (filterOptions?.price_range.max || 500)) apiFilters.max_price = priceRange[1];

    getLessons(apiFilters)
      .then((data) => {
        setLessons(data.results);
        setTotalCount(data.count);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [filters, currentPage, lessonType, skillLevel, priceRange, filterOptions?.price_range.max]);

  useEffect(() => {
    fetchLessons();
  }, [fetchLessons]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filters, lessonType, skillLevel, priceRange]);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  const clearAllFilters = () => {
    setFilters({});
    setLessonType('');
    setSkillLevel('');
    setPriceRange([0, filterOptions?.price_range.max || 500]);
    setCurrentPage(1);
  };

  const activeFiltersCount =
    (filters.country ? 1 : 0) +
    (lessonType ? 1 : 0) +
    (skillLevel ? 1 : 0) +
    (priceRange[0] > 0 || priceRange[1] < (filterOptions?.price_range.max || 500) ? 1 : 0);

  const getLessonTypeLabel = (type: string) => {
    const option = filterOptions?.lesson_types.find(t => t.value === type);
    if (!option) return type;
    return language === 'ru' ? option.label_ru : option.label;
  };

  const getSkillLevelLabel = (level: string) => {
    const option = filterOptions?.skill_levels.find(l => l.value === level);
    if (!option) return level;
    return language === 'ru' ? option.label_ru : option.label;
  };

  const formatDuration = (minutes: number) => {
    if (minutes >= 60) {
      const hours = minutes / 60;
      return `${hours} ${language === 'ru' ? 'ч' : 'h'}`;
    }
    return `${minutes} ${language === 'ru' ? 'мин' : 'min'}`;
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
            <h1 style={{ fontSize: '24px', fontWeight: 700, color: '#0f172a', margin: 0 }}>
              {t('lessons.title')}
            </h1>
            <p style={{ fontSize: '14px', color: '#64748b', margin: '4px 0 0' }}>
              {totalCount} {t('lessons.places')}
            </p>
          </div>

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

        {/* Filters Panel */}
        {showFilters && (
          <div style={{
            borderTop: '1px solid #e2e8f0',
            padding: '24px',
            backgroundColor: '#fafafa'
          }}>
            <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '24px'
              }}>
                {/* Country */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase'
                  }}>
                    {t('filters.country')}
                  </label>
                  <div style={{ position: 'relative' }}>
                    <select
                      value={filters.country || ''}
                      onChange={(e) => setFilters(prev => ({ ...prev, country: e.target.value || undefined }))}
                      style={{
                        width: '100%',
                        padding: '12px 40px 12px 16px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        backgroundColor: 'white',
                        fontSize: '14px',
                        appearance: 'none',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="">{t('filters.allCountries')}</option>
                      {filterOptions?.countries.map(country => (
                        <option key={country.code} value={country.code}>
                          {language === 'ru' ? country.name : country.name_en} ({country.lessons_count})
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

                {/* Lesson Type */}
                <div>
                  <label style={{
                    display: 'block',
                    fontSize: '12px',
                    fontWeight: 600,
                    color: '#64748b',
                    marginBottom: '8px',
                    textTransform: 'uppercase'
                  }}>
                    {t('lessons.private')} / {t('lessons.group')}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {filterOptions?.lesson_types.map(type => (
                      <button
                        key={type.value}
                        onClick={() => setLessonType(lessonType === type.value ? '' : type.value)}
                        style={{
                          padding: '10px 16px',
                          borderRadius: '20px',
                          border: lessonType === type.value ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: lessonType === type.value ? '#f0f9ff' : 'white',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: lessonType === type.value ? '#0284c7' : '#0f172a',
                          cursor: 'pointer'
                        }}
                      >
                        {language === 'ru' ? type.label_ru : type.label}
                      </button>
                    ))}
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
                    textTransform: 'uppercase'
                  }}>
                    {t('filters.skillLevel')}
                  </label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {filterOptions?.skill_levels.map(level => (
                      <button
                        key={level.value}
                        onClick={() => setSkillLevel(skillLevel === level.value ? '' : level.value)}
                        style={{
                          padding: '10px 16px',
                          borderRadius: '20px',
                          border: skillLevel === level.value ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                          backgroundColor: skillLevel === level.value ? '#f0f9ff' : 'white',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: skillLevel === level.value ? '#0284c7' : '#0f172a',
                          cursor: 'pointer'
                        }}
                      >
                        {language === 'ru' ? level.label_ru : level.label}
                      </button>
                    ))}
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
                    textTransform: 'uppercase'
                  }}>
                    {t('filters.priceRange')} (${priceRange[0]} - ${priceRange[1]})
                  </label>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <input
                      type="number"
                      value={priceRange[0]}
                      onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
                      min={0}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0',
                        fontSize: '14px'
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
                        fontSize: '14px'
                      }}
                      placeholder="Max"
                    />
                  </div>
                </div>
              </div>

              {/* Clear filters */}
              {activeFiltersCount > 0 && (
                <div style={{ marginTop: '24px', paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
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
        )}
      </div>

      {/* Content */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '32px 24px' }}>
        {error ? (
          <div style={{ textAlign: 'center', padding: '80px 24px' }}>
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
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
              {t('camps.error')}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 24px' }}>{error}</p>
            <button
              onClick={fetchLessons}
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
                <div style={{ height: '18px', backgroundColor: '#f1f5f9', borderRadius: '4px', width: '80%' }} />
              </div>
            ))}
          </div>
        ) : lessons.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 24px' }}>
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
            <h3 style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
              {t('lessons.noResults')}
            </h3>
            <p style={{ fontSize: '14px', color: '#64748b', margin: 0 }}>
              {t('lessons.adjustFilters')}
            </p>
          </div>
        ) : (
          <>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '24px'
            }}>
              {lessons.map((lesson) => (
                <Link
                  key={lesson.id}
                  to={`/lessons/${lesson.slug}`}
                  style={{ display: 'block', textDecoration: 'none', color: 'inherit' }}
                >
                  <article style={{
                    border: '1px solid #e2e8f0',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    transition: 'box-shadow 0.2s',
                  }}
                  onMouseOver={(e) => e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)'}
                  onMouseOut={(e) => e.currentTarget.style.boxShadow = 'none'}
                  >
                    {/* Image */}
                    <div style={{
                      position: 'relative',
                      aspectRatio: '16/10',
                      overflow: 'hidden'
                    }}>
                      <img
                        src={lesson.main_image || 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&h=500&fit=crop'}
                        alt={lesson.name}
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                      />
                      {/* Type badge */}
                      <div style={{
                        position: 'absolute',
                        top: '12px',
                        left: '12px',
                        padding: '6px 12px',
                        backgroundColor: lesson.lesson_type === 'private' ? '#0ea5e9' : '#10b981',
                        borderRadius: '20px',
                        fontSize: '12px',
                        fontWeight: 600,
                        color: 'white'
                      }}>
                        {getLessonTypeLabel(lesson.lesson_type)}
                      </div>
                      {/* Featured badge */}
                      {lesson.is_featured && (
                        <div style={{
                          position: 'absolute',
                          top: '12px',
                          right: '12px',
                          padding: '6px 12px',
                          backgroundColor: '#f59e0b',
                          borderRadius: '20px',
                          fontSize: '12px',
                          fontWeight: 600,
                          color: 'white'
                        }}>
                          Featured
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div style={{ padding: '16px' }}>
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '8px'
                      }}>
                        <div style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          color: '#64748b',
                          fontSize: '13px'
                        }}>
                          <MapPin style={{ width: '14px', height: '14px' }} />
                          <span>{lesson.region_name}, {lesson.country_name}</span>
                        </div>
                        {lesson.rating > 0 && (
                          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <Star style={{ width: '14px', height: '14px', fill: '#0f172a', color: '#0f172a' }} />
                            <span style={{ fontSize: '14px', fontWeight: 500 }}>
                              {Number(lesson.rating).toFixed(1)}
                            </span>
                          </div>
                        )}
                      </div>

                      <h3 style={{
                        fontSize: '16px',
                        fontWeight: 600,
                        color: '#0f172a',
                        margin: '0 0 6px'
                      }}>
                        {language === 'ru' && lesson.name_ru ? lesson.name_ru : lesson.name}
                      </h3>

                      <p style={{
                        fontSize: '13px',
                        color: '#64748b',
                        margin: '0 0 12px',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}>
                        {language === 'ru' && lesson.short_description_ru ? lesson.short_description_ru : lesson.short_description}
                      </p>

                      {/* Info row */}
                      <div style={{
                        display: 'flex',
                        gap: '16px',
                        marginBottom: '12px',
                        fontSize: '13px',
                        color: '#64748b'
                      }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock style={{ width: '14px', height: '14px' }} />
                          {formatDuration(lesson.duration_minutes)}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Users style={{ width: '14px', height: '14px' }} />
                          {lesson.lesson_type === 'private' ? '1:1' : `max ${lesson.max_participants}`}
                        </div>
                        <span style={{
                          padding: '2px 8px',
                          backgroundColor: lesson.skill_level === 'beginner' ? '#dcfce7' : lesson.skill_level === 'intermediate' ? '#fef3c7' : '#fce7f3',
                          color: lesson.skill_level === 'beginner' ? '#166534' : lesson.skill_level === 'intermediate' ? '#92400e' : '#9d174d',
                          borderRadius: '4px',
                          fontSize: '11px',
                          fontWeight: 500
                        }}>
                          {getSkillLevelLabel(lesson.skill_level)}
                        </span>
                      </div>

                      {/* Tags */}
                      <div style={{ display: 'flex', gap: '6px', marginBottom: '12px', flexWrap: 'wrap' }}>
                        {lesson.includes_equipment && (
                          <span style={{
                            padding: '4px 8px',
                            backgroundColor: '#f1f5f9',
                            borderRadius: '6px',
                            fontSize: '11px',
                            color: '#475569'
                          }}>
                            {t('lessons.includesEquipment')}
                          </span>
                        )}
                        {lesson.includes_transport && (
                          <span style={{
                            padding: '4px 8px',
                            backgroundColor: '#f1f5f9',
                            borderRadius: '6px',
                            fontSize: '11px',
                            color: '#475569'
                          }}>
                            {t('lessons.includesTransport')}
                          </span>
                        )}
                      </div>

                      {/* Price */}
                      <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        paddingTop: '12px',
                        borderTop: '1px solid #e2e8f0'
                      }}>
                        <div>
                          <span style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>
                            ${lesson.price}
                          </span>
                          <span style={{ fontSize: '13px', color: '#64748b', marginLeft: '4px' }}>
                            {lesson.is_package ? t('lessons.perPackage') : t('lessons.perLesson')}
                          </span>
                        </div>
                        <span style={{ fontSize: '12px', color: '#64748b' }}>
                          {lesson.provider_name}
                        </span>
                      </div>
                    </div>
                  </article>
                </Link>
              ))}
            </div>
            <Pagination
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={setCurrentPage}
              totalCount={totalCount}
              pageSize={PAGE_SIZE}
            />
          </>
        )}
      </div>
    </div>
  );
}
