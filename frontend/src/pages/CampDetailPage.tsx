import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  MapPin, Star, ArrowLeft,
  ChevronLeft, ChevronRight, Check, Waves, Users,
  Map as MapIcon, MessageCircle, Clock, Percent
} from 'lucide-react';
import { getCamp } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import { OptimizedImage, useImagePreload } from '../components/OptimizedImage';
import { InlineSignupCard } from '../components/RegistrationMotivation';
import type { SurfCampDetail } from '../types';

export function CampDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { t, language, getLocalized } = useLanguage();
  const [camp, setCamp] = useState<SurfCampDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeImage, setActiveImage] = useState(0);
  const [activeTab, setActiveTab] = useState<'overview' | 'instructors' | 'spots' | 'reviews'>('overview');
  const [packageType, setPackageType] = useState<'full' | 'bnb'>('full');

  useEffect(() => {
    if (slug) {
      setLoading(true);
      getCamp(slug)
        .then(setCamp)
        .catch(console.error)
        .finally(() => setLoading(false));
    }
  }, [slug]);

  // Preload first 3 images (must run before early returns to satisfy hook rules)
  const preloadImages = camp && camp.images.length > 0
    ? camp.images.map(img => img.image)
    : [];
  useImagePreload(preloadImages, 3);

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

  if (!camp) {
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
            {t('common.notFound')}
          </h1>
          <Link to="/camps" style={{ color: '#0ea5e9', textDecoration: 'none' }}>
            {t('camp.backToCamps')}
          </Link>
        </div>
      </div>
    );
  }

  const images = camp.images.length > 0
    ? camp.images.map(img => img.image)
    : ['https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=1200&h=800&fit=crop'];

  // Discount calculations
  const hasDiscount = (camp as any).discount_percent && (camp as any).discount_percent > 0;
  const discountEndsAt = (camp as any).discount_ends_at;
  const isDiscountActive = hasDiscount && discountEndsAt && new Date(discountEndsAt) > new Date();
  const originalPrice = Number(camp.price_per_night);
  const discountedPrice = isDiscountActive
    ? originalPrice * (1 - ((camp as any).discount_percent || 0) / 100)
    : originalPrice;

  const skillLevelLabels: Record<string, { en: string; ru: string }> = {
    beginner: { en: 'Beginner', ru: 'Начинающий' },
    intermediate: { en: 'Intermediate', ru: 'Средний' },
    advanced: { en: 'Advanced', ru: 'Продвинутый' },
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Back Button */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '16px 24px'
      }}>
        <Link
          to="/camps"
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
          {t('camp.backToCamps')}
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
          <OptimizedImage
            src={images[activeImage]}
            alt={camp.name}
            priority={activeImage === 0}
            sizes="(max-width: 768px) 100vw, 1400px"
            style={{
              width: '100%',
              height: '100%'
            }}
          />

          {/* Discount Badge */}
          {isDiscountActive && (
            <div style={{
              position: 'absolute',
              top: '20px',
              right: '20px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'flex-end',
              gap: '8px'
            }}>
              <div style={{
                padding: '10px 18px',
                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                borderRadius: '24px',
                fontSize: '16px',
                fontWeight: 700,
                color: 'white',
                boxShadow: '0 4px 15px rgba(239,68,68,0.4)',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <Percent style={{ width: '18px', height: '18px' }} />
                -{(camp as any).discount_percent}% OFF
              </div>
              <div style={{
                padding: '6px 14px',
                backgroundColor: 'rgba(0,0,0,0.8)',
                borderRadius: '14px',
                fontSize: '13px',
                fontWeight: 600,
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                gap: '6px'
              }}>
                <Clock style={{ width: '14px', height: '14px' }} />
                Limited time offer!
              </div>
            </div>
          )}

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
              <div style={{
                position: 'absolute',
                bottom: '16px',
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                gap: '8px'
              }}>
                {images.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveImage(i)}
                    style={{
                      width: i === activeImage ? '24px' : '8px',
                      height: '8px',
                      backgroundColor: i === activeImage ? 'white' : 'rgba(255,255,255,0.5)',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      transition: 'all 0.2s'
                    }}
                  />
                ))}
              </div>
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
        gridTemplateColumns: '1fr 380px',
        gap: '48px'
      }}>
        {/* Main Content */}
        <div>
          {/* Header */}
          <div style={{ marginBottom: '32px' }}>
            {camp.is_featured && (
              <span style={{
                display: 'inline-block',
                padding: '6px 14px',
                background: 'linear-gradient(135deg, #fbbf24, #f97316)',
                color: 'white',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: 600,
                marginBottom: '12px'
              }}>
                {t('camp.guestFavourite')}
              </span>
            )}
            <h1 style={{
              fontSize: '32px',
              fontWeight: 700,
              color: '#0f172a',
              margin: '0 0 12px'
            }}>
              {camp.name}
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
                {getLocalized(camp.region.name, camp.region.name_en)}, {getLocalized(camp.country.name, camp.country.name_en)}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Star style={{ width: '18px', height: '18px', fill: '#0f172a', color: '#0f172a' }} />
                <span style={{ fontWeight: 600, color: '#0f172a' }}>{Number(camp.rating).toFixed(1)}</span>
                <span>({camp.reviews_count} {t('camp.reviews')})</span>
              </div>
            </div>

            {/* Skill Levels */}
            <div style={{ display: 'flex', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
              {camp.skill_levels.map(level => (
                <span
                  key={level}
                  style={{
                    padding: '6px 14px',
                    backgroundColor: level === 'beginner' ? '#dcfce7' : level === 'intermediate' ? '#fef3c7' : '#fce7f3',
                    color: level === 'beginner' ? '#166534' : level === 'intermediate' ? '#92400e' : '#9d174d',
                    borderRadius: '20px',
                    fontSize: '13px',
                    fontWeight: 500,
                  }}
                >
                  {language === 'ru' ? skillLevelLabels[level]?.ru : skillLevelLabels[level]?.en}
                </span>
              ))}
            </div>

            {/* Teaching languages */}
            {camp.teaching_languages && camp.teaching_languages.length > 0 && (
              <div style={{ marginTop: '16px' }}>
                <div style={{
                  fontSize: '12px',
                  fontWeight: 600,
                  color: '#64748b',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                  marginBottom: '8px'
                }}>
                  {language === 'ru' ? 'Языки обучения' : 'Teaching languages'}
                </div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {camp.teaching_languages.map(lang => {
                    const labels: Record<string, { en: string; ru: string }> = {
                      en: { en: 'English', ru: 'Английский' },
                      ru: { en: 'Russian', ru: 'Русский' },
                      es: { en: 'Spanish', ru: 'Испанский' },
                      pt: { en: 'Portuguese', ru: 'Португальский' },
                      fr: { en: 'French', ru: 'Французский' },
                      de: { en: 'German', ru: 'Немецкий' },
                    };
                    return (
                      <span
                        key={lang}
                        style={{
                          padding: '6px 14px',
                          backgroundColor: '#eff6ff',
                          color: '#1e40af',
                          borderRadius: '20px',
                          fontSize: '13px',
                          fontWeight: 500,
                          border: '1px solid #bfdbfe',
                        }}
                      >
                        {language === 'ru' ? (labels[lang]?.ru || lang) : (labels[lang]?.en || lang)}
                      </span>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Quick Features */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '12px',
            marginBottom: '32px'
          }}>
            {camp.has_pool && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px',
                backgroundColor: '#f8fafc',
                borderRadius: '12px'
              }}>
                <Waves style={{ width: '24px', height: '24px', color: '#0ea5e9' }} />
                <span style={{ fontWeight: 500, color: '#0f172a' }}>{t('filters.pool')}</span>
              </div>
            )}
            {camp.has_yoga && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px',
                backgroundColor: '#f8fafc',
                borderRadius: '12px'
              }}>
                <Users style={{ width: '24px', height: '24px', color: '#7c3aed' }} />
                <span style={{ fontWeight: 500, color: '#0f172a' }}>{t('filters.yoga')}</span>
              </div>
            )}
            {camp.board_rental_available && (
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px',
                backgroundColor: '#f8fafc',
                borderRadius: '12px'
              }}>
                <Waves style={{ width: '24px', height: '24px', color: '#10b981' }} />
                <span style={{ fontWeight: 500, color: '#0f172a' }}>{t('filters.boardRental')}</span>
              </div>
            )}
          </div>

          {/* Tabs */}
          <div style={{
            display: 'flex',
            gap: '8px',
            borderBottom: '1px solid #e2e8f0',
            marginBottom: '32px',
            overflowX: 'auto'
          }}>
            {([
              { key: 'overview', label: t('camp.overview') },
              { key: 'instructors', label: t('camp.instructors') },
              { key: 'spots', label: t('camp.surfSpots') },
              { key: 'reviews', label: t('camp.reviewsTab') },
            ] as const).map(tab => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                style={{
                  padding: '12px 20px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  color: activeTab === tab.key ? '#0f172a' : '#64748b',
                  fontSize: '15px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  borderBottom: activeTab === tab.key ? '2px solid #0f172a' : '2px solid transparent',
                  marginBottom: '-1px',
                  whiteSpace: 'nowrap'
                }}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          {activeTab === 'overview' && (
            <div>
              <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
                {t('camp.about')}
              </h3>
              <p style={{ fontSize: '15px', lineHeight: 1.7, color: '#475569', whiteSpace: 'pre-line', marginBottom: '32px' }}>
                {camp.description}
              </p>

              {/* History Section */}
              {camp.history && (
                <>
                  <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
                    {t('camp.history')}
                  </h3>
                  <p style={{ fontSize: '15px', lineHeight: 1.7, color: '#475569', whiteSpace: 'pre-line', marginBottom: '32px' }}>
                    {camp.history}
                  </p>
                </>
              )}

              {/* Activities */}
              {camp.activities.length > 0 && (
                <>
                  <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
                    {t('camp.activities')}
                  </h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '12px',
                    marginBottom: '32px'
                  }}>
                    {camp.activities.map(activity => (
                      <div
                        key={activity.id}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                          padding: '14px 16px',
                          backgroundColor: '#f8fafc',
                          borderRadius: '12px'
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                          <Check style={{ width: '18px', height: '18px', color: '#10b981' }} />
                          <span style={{ fontSize: '14px', color: '#0f172a' }}>
                            {getLocalized(activity.name, activity.name_en)}
                          </span>
                        </div>
                        {activity.is_included ? (
                          <span style={{ fontSize: '12px', color: '#10b981', fontWeight: 500 }}>{t('camp.included')}</span>
                        ) : activity.price ? (
                          <span style={{ fontSize: '13px', color: '#64748b' }}>${activity.price}</span>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </>
              )}

              {/* Lessons Without Accommodation */}
              {camp.price_per_lesson && (
                <div style={{
                  backgroundColor: '#f0f9ff',
                  borderRadius: '16px',
                  padding: '24px',
                  marginBottom: '32px',
                  border: '1px solid #bae6fd'
                }}>
                  <h3 style={{
                    fontSize: '18px',
                    fontWeight: 600,
                    color: '#0284c7',
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px'
                  }}>
                    <Waves style={{ width: '22px', height: '22px' }} />
                    {t('camp.lessonsWithoutStay')}
                  </h3>
                  <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px' }}>
                    <span style={{ fontSize: '28px', fontWeight: 700, color: '#0f172a' }}>
                      ${Number(camp.price_per_lesson).toFixed(0)}
                    </span>
                    <span style={{ fontSize: '15px', color: '#64748b' }}>
                      {t('camp.pricePerLesson')}
                    </span>
                  </div>
                  <p style={{ fontSize: '14px', color: '#64748b', marginTop: '12px', marginBottom: 0 }}>
                    {language === 'ru'
                      ? 'Возможность брать уроки без проживания в кемпе. Включает оборудование и профессионального инструктора.'
                      : 'Take lessons without staying at the camp. Includes equipment and professional instructor.'}
                  </p>
                </div>
              )}

              {/* Board Types */}
              {camp.board_types.length > 0 && (
                <>
                  <h3 style={{ fontSize: '20px', fontWeight: 600, color: '#0f172a', marginBottom: '16px' }}>
                    {t('filters.boardTypes')}
                  </h3>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '32px' }}>
                    {camp.board_types.map(board => (
                      <span
                        key={board.id}
                        style={{
                          padding: '10px 18px',
                          backgroundColor: '#f1f5f9',
                          borderRadius: '20px',
                          fontSize: '14px',
                          fontWeight: 500,
                          color: '#334155'
                        }}
                      >
                        {getLocalized(board.name, board.name_en)}
                      </span>
                    ))}
                  </div>
                </>
              )}
            </div>
          )}

          {activeTab === 'instructors' && (
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
              gap: '20px'
            }}>
              {camp.instructors.length === 0 ? (
                <p style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>{t('camp.noInstructors')}</p>
              ) : (
                camp.instructors.map(instructor => (
                  <div
                    key={instructor.id}
                    style={{
                      padding: '24px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '16px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '12px' }}>
                      <div style={{
                        width: '56px',
                        height: '56px',
                        background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                        borderRadius: '50%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontSize: '20px',
                        fontWeight: 700,
                        overflow: 'hidden'
                      }}>
                        {instructor.photo ? (
                          <img src={instructor.photo} alt={instructor.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        ) : (
                          instructor.name.charAt(0)
                        )}
                      </div>
                      <div>
                        <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: 0 }}>
                          {instructor.name}
                        </h4>
                        {instructor.is_head_coach && (
                          <span style={{ fontSize: '13px', color: '#f59e0b', fontWeight: 500 }}>{t('camp.headCoach')}</span>
                        )}
                      </div>
                    </div>
                    <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 8px' }}>
                      {instructor.experience_years} {t('camp.yearsExp')}
                    </p>
                    {instructor.certifications && (
                      <p style={{ fontSize: '13px', color: '#94a3b8', margin: '0 0 8px' }}>
                        {instructor.certifications}
                      </p>
                    )}
                    {instructor.languages && (
                      <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0 }}>
                        {t('camp.languages')}: {instructor.languages}
                      </p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {activeTab === 'spots' && (
            <div>
              {camp.spots && camp.spots.length > 0 ? (
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: '20px'
                }}>
                  {camp.spots.map(spot => (
                    <Link
                      key={spot.id}
                      to={`/spots/${spot.slug}`}
                      style={{
                        textDecoration: 'none',
                        padding: '20px',
                        backgroundColor: '#f8fafc',
                        borderRadius: '16px',
                        display: 'block',
                        transition: 'transform 0.2s, box-shadow 0.2s'
                      }}
                      onMouseOver={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                      }}
                      onMouseOut={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = 'none';
                      }}
                    >
                      {spot.main_image && (
                        <img
                          src={spot.main_image}
                          alt={spot.name}
                          style={{
                            width: '100%',
                            height: '120px',
                            objectFit: 'cover',
                            borderRadius: '12px',
                            marginBottom: '12px'
                          }}
                        />
                      )}
                      <h4 style={{ fontSize: '16px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
                        {spot.name}
                      </h4>
                      <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 12px' }}>
                        {spot.short_description}
                      </p>
                      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        <span style={{
                          padding: '4px 10px',
                          backgroundColor: '#e0f2fe',
                          borderRadius: '6px',
                          fontSize: '12px',
                          color: '#0284c7',
                          fontWeight: 500
                        }}>
                          {spot.wave_type}
                        </span>
                        <span style={{
                          padding: '4px 10px',
                          backgroundColor: '#dcfce7',
                          borderRadius: '6px',
                          fontSize: '12px',
                          color: '#166534',
                          fontWeight: 500
                        }}>
                          {spot.wave_direction === 'both' ? 'A-Frame' : spot.wave_direction}
                        </span>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '60px 24px' }}>
                  <MapIcon style={{ width: '48px', height: '48px', color: '#cbd5e1', margin: '0 auto 16px' }} />
                  <p style={{ color: '#64748b', fontSize: '15px' }}>
                    {language === 'ru'
                      ? 'Информация о серф-спотах скоро появится'
                      : 'Surf spots information coming soon'}
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'reviews' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {camp.reviews.length === 0 ? (
                <p style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>{t('camp.noReviews')}</p>
              ) : (
                camp.reviews.map(review => (
                  <div
                    key={review.id}
                    style={{
                      padding: '24px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '16px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                          width: '44px',
                          height: '44px',
                          backgroundColor: '#e2e8f0',
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          color: '#64748b',
                          fontSize: '16px',
                          fontWeight: 600
                        }}>
                          {review.author_name.charAt(0)}
                        </div>
                        <div>
                          <h4 style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', margin: 0 }}>
                            {review.author_name}
                          </h4>
                          <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0 }}>
                            {review.author_country}
                          </p>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Star style={{ width: '16px', height: '16px', fill: '#fbbf24', color: '#fbbf24' }} />
                        <span style={{ fontWeight: 600, color: '#0f172a' }}>{review.rating}</span>
                      </div>
                    </div>
                    {review.title && (
                      <h5 style={{ fontSize: '15px', fontWeight: 600, color: '#0f172a', margin: '0 0 8px' }}>
                        {review.title}
                      </h5>
                    )}
                    <p style={{ fontSize: '14px', lineHeight: 1.6, color: '#475569', margin: 0 }}>
                      {review.text}
                    </p>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Sidebar - Booking Card */}
        <div>
          {/* Inline signup card for non-logged users */}
          <InlineSignupCard
            isLoggedIn={false}
            onRegister={() => window.location.href = '/register'}
          />

          <div style={{
            position: 'sticky',
            top: '100px',
            padding: '28px',
            backgroundColor: 'white',
            borderRadius: '20px',
            border: isDiscountActive ? '2px solid #dc2626' : '1px solid #e2e8f0',
            boxShadow: isDiscountActive ? '0 4px 20px rgba(220,38,38,0.15)' : '0 4px 20px rgba(0,0,0,0.08)'
          }}>
            {/* Discount header */}
            {isDiscountActive && (
              <div style={{
                background: 'linear-gradient(135deg, #dc2626, #b91c1c)',
                margin: '-28px -28px 20px -28px',
                padding: '14px 28px',
                borderRadius: '18px 18px 0 0',
                textAlign: 'center'
              }}>
                <span style={{ color: 'white', fontWeight: 700, fontSize: '15px' }}>
                  🔥 FLASH SALE - {(camp as any).discount_percent}% OFF
                </span>
              </div>
            )}

            <div style={{ marginBottom: '24px' }}>
              {isDiscountActive ? (
                <div>
                  <span style={{
                    fontSize: '18px',
                    color: '#94a3b8',
                    textDecoration: 'line-through',
                    marginRight: '10px'
                  }}>
                    ${originalPrice.toFixed(0)}
                  </span>
                  <span style={{ fontSize: '28px', fontWeight: 700, color: '#dc2626' }}>
                    ${discountedPrice.toFixed(0)}
                  </span>
                  <span style={{ fontSize: '16px', color: '#64748b' }}> / {t('camp.perNight')}</span>
                </div>
              ) : (
                <div>
                  <span style={{ fontSize: '28px', fontWeight: 700, color: '#0f172a' }}>
                    ${originalPrice.toFixed(0)}
                  </span>
                  <span style={{ fontSize: '16px', color: '#64748b' }}> / {t('camp.perNight')}</span>
                </div>
              )}
            </div>

            {camp.has_bed_breakfast && camp.bed_breakfast_price && (
              <div style={{
                display: 'flex',
                gap: '8px',
                marginBottom: '16px',
                padding: '4px',
                backgroundColor: '#f1f5f9',
                borderRadius: '12px',
              }}>
                {[
                  { value: 'full' as const, label: language === 'ru' ? 'С уроками' : 'With lessons', price: originalPrice },
                  { value: 'bnb' as const, label: language === 'ru' ? 'Только проживание' : 'B&B only', price: Number(camp.bed_breakfast_price) },
                ].map(opt => (
                  <button
                    key={opt.value}
                    onClick={() => setPackageType(opt.value)}
                    style={{
                      flex: 1,
                      padding: '10px 12px',
                      background: packageType === opt.value ? 'white' : 'transparent',
                      border: 'none',
                      borderRadius: '10px',
                      fontSize: '13px',
                      fontWeight: 600,
                      color: packageType === opt.value ? '#0f172a' : '#64748b',
                      cursor: 'pointer',
                      boxShadow: packageType === opt.value ? '0 1px 2px rgba(0,0,0,0.08)' : 'none',
                    }}
                  >
                    <div>{opt.label}</div>
                    <div style={{ fontSize: '12px', fontWeight: 500, color: '#0ea5e9' }}>${opt.price.toFixed(0)} / {t('camp.perNight')}</div>
                  </button>
                ))}
              </div>
            )}

            <button
              onClick={() => navigate(`/camps/${slug}/book${packageType === 'bnb' ? '?package=bnb' : ''}`)}
              style={{
                width: '100%',
                padding: '16px',
                background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
                marginBottom: '12px'
              }}
            >
              {t('camp.bookNow')}
            </button>

            <p style={{ textAlign: 'center', fontSize: '13px', color: '#94a3b8', marginBottom: '24px' }}>
              {t('camp.noCharge')}
            </p>

            {/* Contacts hidden — sent after registration */}
            <div style={{
              borderTop: '1px solid #e2e8f0',
              paddingTop: '24px',
            }}>
              <div style={{
                padding: '16px',
                background: 'linear-gradient(135deg, #f0f9ff, #e0f2fe)',
                borderRadius: '12px',
                border: '1px solid #bae6fd',
              }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '6px',
                }}>
                  <MessageCircle style={{ width: '18px', height: '18px', color: '#0284c7' }} />
                  <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#0c4a6e', margin: 0 }}>
                    {language === 'ru' ? 'Контакты камп-школы' : 'Camp contacts'}
                  </h4>
                </div>
                <p style={{ fontSize: '13px', color: '#0369a1', margin: 0, lineHeight: 1.5 }}>
                  {language === 'ru'
                    ? 'Контакты школы (телефон, email, WhatsApp, Instagram) отправим вам на почту после регистрации заявки.'
                    : "We'll email you the camp's contact details (phone, email, WhatsApp, Instagram) after you submit a booking request."}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Booking Bar */}
      <div className="lg:hidden" style={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        padding: '16px 24px',
        backgroundColor: 'white',
        borderTop: '1px solid #e2e8f0',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        zIndex: 50
      }}>
        <div>
          <span style={{ fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
            ${Number(camp.price_per_night).toFixed(0)}
          </span>
          <span style={{ fontSize: '14px', color: '#64748b' }}> / {t('camp.perNight')}</span>
        </div>
        <button
          onClick={() => navigate(`/camps/${slug}/book`)}
          style={{
            padding: '14px 32px',
            background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: '16px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          {t('camp.bookNow')}
        </button>
      </div>
    </div>
  );
}
