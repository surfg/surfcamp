import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  MapPin, Star, ArrowLeft, Globe, Mail, Phone, Clock,
  ChevronLeft, ChevronRight, Check, Users, Calendar,
  Award, Camera, Video, Shield, BookOpen
} from 'lucide-react';
import { getLesson } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfLessonDetail } from '../types';

export function LessonDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { t, language } = useLanguage();
  const [lesson, setLesson] = useState<SurfLessonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeImage, setActiveImage] = useState(0);

  useEffect(() => {
    if (slug) {
      setLoading(true);
      getLesson(slug)
        .then(setLesson)
        .catch(console.error)
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
          borderTopColor: '#0ea5e9',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
      </div>
    );
  }

  if (!lesson) {
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
          <Link to="/lessons" style={{ color: '#0ea5e9', textDecoration: 'none' }}>
            {t('lesson.backToLessons')}
          </Link>
        </div>
      </div>
    );
  }

  const images = lesson.images.length > 0
    ? lesson.images.map(img => img.image)
    : ['https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=1200&h=800&fit=crop'];

  const lessonTypeLabels: Record<string, { en: string; ru: string }> = {
    private: { en: 'Private Lesson', ru: 'Индивидуальный урок' },
    group: { en: 'Group Lesson', ru: 'Групповой урок' },
    semi_private: { en: 'Semi-Private', ru: 'Полу-индивидуальный' },
  };

  const skillLevelLabels: Record<string, { en: string; ru: string }> = {
    beginner: { en: 'Beginner', ru: 'Начинающий' },
    intermediate: { en: 'Intermediate', ru: 'Средний' },
    advanced: { en: 'Advanced', ru: 'Продвинутый' },
    all: { en: 'All Levels', ru: 'Все уровни' },
  };

  const formatDuration = (minutes: number): string => {
    if (minutes < 60) return `${minutes} ${language === 'ru' ? 'мин' : 'min'}`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (mins === 0) return `${hours} ${language === 'ru' ? (hours === 1 ? 'час' : 'часа') : (hours === 1 ? 'hour' : 'hours')}`;
    return `${hours}${language === 'ru' ? 'ч' : 'h'} ${mins}${language === 'ru' ? 'м' : 'm'}`;
  };

  const includes = [
    { included: lesson.includes_equipment, label: { en: 'Equipment (board & wetsuit)', ru: 'Оборудование (доска и гидрокостюм)' }, icon: Award },
    { included: lesson.includes_wetsuit, label: { en: 'Wetsuit', ru: 'Гидрокостюм' }, icon: Award },
    { included: lesson.includes_photos, label: { en: 'Photos', ru: 'Фото' }, icon: Camera },
    { included: lesson.includes_video, label: { en: 'Video', ru: 'Видео' }, icon: Video },
    { included: lesson.includes_theory, label: { en: 'Theory session', ru: 'Теоретическая часть' }, icon: BookOpen },
    { included: lesson.includes_insurance, label: { en: 'Insurance', ru: 'Страховка' }, icon: Shield },
    { included: lesson.includes_transport, label: { en: 'Transport to spot', ru: 'Трансфер до спота' }, icon: MapPin },
  ].filter(item => item.included);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#ffffff' }}>
      {/* Back Button */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '16px 24px'
      }}>
        <Link
          to="/lessons"
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
          {t('lesson.backToLessons')}
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
            alt={language === 'ru' ? lesson.name_ru : lesson.name}
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

          {/* Lesson Type Badge */}
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            backgroundColor: lesson.lesson_type === 'private' ? '#7c3aed' : lesson.lesson_type === 'group' ? '#0ea5e9' : '#f59e0b',
            color: 'white',
            padding: '8px 16px',
            borderRadius: '24px',
            fontSize: '14px',
            fontWeight: 600
          }}>
            {lessonTypeLabels[lesson.lesson_type]?.[language] || lesson.lesson_type}
          </div>
        </div>
      </div>

      {/* Content */}
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 24px 48px',
        display: 'grid',
        gridTemplateColumns: '1fr',
        gap: '32px'
      }} className="lg:grid-cols-[1fr_380px]">
        {/* Main Content */}
        <div>
          {/* Title & Info */}
          <div style={{ marginBottom: '32px' }}>
            <h1 style={{
              fontSize: '32px',
              fontWeight: 700,
              color: '#0f172a',
              marginBottom: '12px'
            }}>
              {language === 'ru' ? lesson.name_ru : lesson.name}
            </h1>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '16px',
              color: '#64748b',
              fontSize: '15px'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin style={{ width: '18px', height: '18px' }} />
                {lesson.region_name}, {lesson.country_name}
              </span>
              {lesson.rating > 0 && (
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Star style={{ width: '18px', height: '18px', fill: '#fbbf24', color: '#fbbf24' }} />
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>{lesson.rating.toFixed(1)}</span>
                  <span>({lesson.reviews_count} {t('camp.reviews')})</span>
                </span>
              )}
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Clock style={{ width: '18px', height: '18px' }} />
                {formatDuration(lesson.duration_minutes)}
              </span>
            </div>
          </div>

          {/* Quick Info Cards */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '16px',
            marginBottom: '32px'
          }}>
            <div style={{
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '16px',
              textAlign: 'center'
            }}>
              <Users style={{ width: '24px', height: '24px', color: '#0ea5e9', margin: '0 auto 8px' }} />
              <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>
                {language === 'ru' ? 'Макс. участников' : 'Max participants'}
              </div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>
                {lesson.max_participants}
              </div>
            </div>
            <div style={{
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '16px',
              textAlign: 'center'
            }}>
              <Award style={{ width: '24px', height: '24px', color: '#0ea5e9', margin: '0 auto 8px' }} />
              <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>
                {language === 'ru' ? 'Уровень' : 'Skill level'}
              </div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>
                {skillLevelLabels[lesson.skill_level]?.[language] || lesson.skill_level}
              </div>
            </div>
            <div style={{
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '16px',
              textAlign: 'center'
            }}>
              <Calendar style={{ width: '24px', height: '24px', color: '#0ea5e9', margin: '0 auto 8px' }} />
              <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>
                {language === 'ru' ? 'Мин. возраст' : 'Min age'}
              </div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#0f172a' }}>
                {lesson.min_age}+
              </div>
            </div>
            {lesson.is_package && (
              <div style={{
                padding: '16px',
                backgroundColor: '#f0fdf4',
                borderRadius: '16px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '4px' }}>
                  {language === 'ru' ? 'Пакет уроков' : 'Package'}
                </div>
                <div style={{ fontSize: '18px', fontWeight: 600, color: '#16a34a' }}>
                  {lesson.lessons_in_package} {language === 'ru' ? 'уроков' : 'lessons'}
                </div>
              </div>
            )}
          </div>

          {/* Description */}
          <div style={{ marginBottom: '32px' }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 600,
              color: '#0f172a',
              marginBottom: '16px'
            }}>
              {language === 'ru' ? 'Описание' : 'Description'}
            </h2>
            <p style={{
              color: '#475569',
              lineHeight: 1.7,
              fontSize: '15px'
            }}>
              {language === 'ru' ? lesson.description_ru : lesson.description}
            </p>
          </div>

          {/* What's Included */}
          {includes.length > 0 && (
            <div style={{ marginBottom: '32px' }}>
              <h2 style={{
                fontSize: '20px',
                fontWeight: 600,
                color: '#0f172a',
                marginBottom: '16px'
              }}>
                {language === 'ru' ? 'Что включено' : "What's included"}
              </h2>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px'
              }}>
                {includes.map((item, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      padding: '12px 16px',
                      backgroundColor: '#f0fdf4',
                      borderRadius: '12px'
                    }}
                  >
                    <Check style={{ width: '20px', height: '20px', color: '#16a34a' }} />
                    <span style={{ color: '#0f172a', fontSize: '14px' }}>
                      {item.label[language]}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Provider Info */}
          <div style={{
            padding: '24px',
            backgroundColor: '#f8fafc',
            borderRadius: '20px',
            marginBottom: '32px'
          }}>
            <h2 style={{
              fontSize: '20px',
              fontWeight: 600,
              color: '#0f172a',
              marginBottom: '16px'
            }}>
              {language === 'ru' ? 'Школа серфинга' : 'Surf School'}
            </h2>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
              {lesson.provider.logo && (
                <img
                  src={lesson.provider.logo}
                  alt={lesson.provider.name}
                  style={{
                    width: '64px',
                    height: '64px',
                    borderRadius: '12px',
                    objectFit: 'cover'
                  }}
                />
              )}
              <div style={{ flex: 1 }}>
                <h3 style={{
                  fontSize: '18px',
                  fontWeight: 600,
                  color: '#0f172a',
                  marginBottom: '8px'
                }}>
                  {lesson.provider.name}
                </h3>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  color: '#64748b',
                  fontSize: '14px',
                  marginBottom: '12px'
                }}>
                  <MapPin style={{ width: '16px', height: '16px' }} />
                  {lesson.provider.address}
                </div>
                <p style={{
                  color: '#475569',
                  fontSize: '14px',
                  lineHeight: 1.6,
                  marginBottom: '16px'
                }}>
                  {language === 'ru' ? lesson.provider.description_ru : lesson.provider.description}
                </p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px' }}>
                  {lesson.provider.phone && (
                    <a
                      href={`tel:${lesson.provider.phone}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        color: '#0ea5e9',
                        textDecoration: 'none',
                        fontSize: '14px'
                      }}
                    >
                      <Phone style={{ width: '16px', height: '16px' }} />
                      {lesson.provider.phone}
                    </a>
                  )}
                  {lesson.provider.email && (
                    <a
                      href={`mailto:${lesson.provider.email}`}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        color: '#0ea5e9',
                        textDecoration: 'none',
                        fontSize: '14px'
                      }}
                    >
                      <Mail style={{ width: '16px', height: '16px' }} />
                      {lesson.provider.email}
                    </a>
                  )}
                  {lesson.provider.website && (
                    <a
                      href={lesson.provider.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        color: '#0ea5e9',
                        textDecoration: 'none',
                        fontSize: '14px'
                      }}
                    >
                      <Globe style={{ width: '16px', height: '16px' }} />
                      Website
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Reviews */}
          {lesson.reviews.length > 0 && (
            <div>
              <h2 style={{
                fontSize: '20px',
                fontWeight: 600,
                color: '#0f172a',
                marginBottom: '16px'
              }}>
                {t('camp.reviewsTab')} ({lesson.reviews.length})
              </h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {lesson.reviews.slice(0, 5).map(review => (
                  <div
                    key={review.id}
                    style={{
                      padding: '20px',
                      backgroundColor: '#f8fafc',
                      borderRadius: '16px'
                    }}
                  >
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                      marginBottom: '12px'
                    }}>
                      <div style={{
                        width: '40px',
                        height: '40px',
                        borderRadius: '50%',
                        backgroundColor: '#0ea5e9',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: 'white',
                        fontWeight: 600
                      }}>
                        {review.author_name.charAt(0).toUpperCase()}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, color: '#0f172a' }}>
                          {review.author_name}
                        </div>
                        <div style={{ fontSize: '13px', color: '#64748b' }}>
                          {review.author_country}
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Star style={{ width: '16px', height: '16px', fill: '#fbbf24', color: '#fbbf24' }} />
                        <span style={{ fontWeight: 600, color: '#0f172a' }}>{review.rating}</span>
                      </div>
                    </div>
                    {review.title && (
                      <h4 style={{
                        fontWeight: 600,
                        color: '#0f172a',
                        marginBottom: '8px'
                      }}>
                        {review.title}
                      </h4>
                    )}
                    <p style={{ color: '#475569', fontSize: '14px', lineHeight: 1.6 }}>
                      {review.text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Sidebar - Booking Card */}
        <div className="hidden lg:block">
          <div style={{
            position: 'sticky',
            top: '96px',
            padding: '24px',
            backgroundColor: 'white',
            borderRadius: '20px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
            border: '1px solid #e2e8f0'
          }}>
            <div style={{ marginBottom: '20px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'baseline',
                gap: '8px',
                marginBottom: '8px'
              }}>
                <span style={{ fontSize: '28px', fontWeight: 700, color: '#0f172a' }}>
                  {lesson.currency === 'EUR' ? '€' : lesson.currency === 'USD' ? '$' : lesson.currency}
                  {lesson.price}
                </span>
                {lesson.price_per_person && (
                  <span style={{ color: '#64748b', fontSize: '14px' }}>
                    / {language === 'ru' ? 'человек' : 'person'}
                  </span>
                )}
              </div>
              {lesson.is_package && lesson.package_discount_percent > 0 && (
                <div style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  backgroundColor: '#dcfce7',
                  color: '#16a34a',
                  borderRadius: '20px',
                  fontSize: '13px',
                  fontWeight: 600
                }}>
                  {language === 'ru' ? `Скидка ${lesson.package_discount_percent}%` : `${lesson.package_discount_percent}% off package`}
                </div>
              )}
            </div>

            <div style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '12px',
              marginBottom: '20px',
              padding: '16px',
              backgroundColor: '#f8fafc',
              borderRadius: '12px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Тип урока' : 'Lesson type'}</span>
                <span style={{ fontWeight: 500, color: '#0f172a' }}>
                  {lessonTypeLabels[lesson.lesson_type]?.[language]}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Длительность' : 'Duration'}</span>
                <span style={{ fontWeight: 500, color: '#0f172a' }}>
                  {formatDuration(lesson.duration_minutes)}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Уровень' : 'Level'}</span>
                <span style={{ fontWeight: 500, color: '#0f172a' }}>
                  {skillLevelLabels[lesson.skill_level]?.[language]}
                </span>
              </div>
            </div>

            <button
              style={{
                width: '100%',
                padding: '16px',
                backgroundColor: '#0ea5e9',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
                marginBottom: '12px'
              }}
            >
              {language === 'ru' ? 'Забронировать урок' : 'Book this lesson'}
            </button>

            {lesson.provider.whatsapp && (
              <a
                href={`https://wa.me/${lesson.provider.whatsapp.replace(/[^0-9]/g, '')}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  width: '100%',
                  padding: '14px',
                  backgroundColor: '#25d366',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '15px',
                  fontWeight: 600,
                  textDecoration: 'none'
                }}
              >
                WhatsApp
              </a>
            )}
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
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        zIndex: 40
      }}>
        <div>
          <div style={{
            display: 'flex',
            alignItems: 'baseline',
            gap: '4px'
          }}>
            <span style={{ fontSize: '22px', fontWeight: 700, color: '#0f172a' }}>
              {lesson.currency === 'EUR' ? '€' : lesson.currency === 'USD' ? '$' : lesson.currency}
              {lesson.price}
            </span>
            {lesson.price_per_person && (
              <span style={{ color: '#64748b', fontSize: '13px' }}>
                / {language === 'ru' ? 'чел.' : 'person'}
              </span>
            )}
          </div>
          <div style={{ fontSize: '13px', color: '#64748b' }}>
            {formatDuration(lesson.duration_minutes)}
          </div>
        </div>
        <button
          style={{
            padding: '14px 32px',
            backgroundColor: '#0ea5e9',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            fontSize: '15px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          {language === 'ru' ? 'Забронировать' : 'Book now'}
        </button>
      </div>
    </div>
  );
}
