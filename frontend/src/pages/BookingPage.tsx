import { useState, useEffect, useMemo } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Calendar, Users, Coffee, Waves, ArrowLeft, ChevronRight, Check, Minus, Plus, Clock } from 'lucide-react';
import { getCamp, calculatePricePreview, createBooking } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { SurfCampDetail, BookingCreateData } from '../types';

export function BookingPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { t, language } = useLanguage();

  const [camp, setCamp] = useState<SurfCampDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Booking state
  const [checkIn, setCheckIn] = useState(searchParams.get('check_in') || '');
  const [checkOut, setCheckOut] = useState(searchParams.get('check_out') || '');
  const [adults, setAdults] = useState(Number(searchParams.get('guests')) || 2);
  const [children, setChildren] = useState(0);
  const packageType: 'full' | 'bnb' = searchParams.get('package') === 'bnb' ? 'bnb' : 'full';
  const [includeBreakfast, setIncludeBreakfast] = useState(false);
  const [includeLessons, setIncludeLessons] = useState(false);
  const [lessonsCount, setLessonsCount] = useState(0);
  const [includeBoardRental, setIncludeBoardRental] = useState(false);
  const [specialRequests, setSpecialRequests] = useState('');
  const [arrivalTime, setArrivalTime] = useState('14:00');

  useEffect(() => {
    // Scroll to top when page loads
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    if (!slug) return;
    getCamp(slug)
      .then(setCamp)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [slug]);

  const nights = useMemo(() => {
    if (!checkIn || !checkOut) return 0;
    const start = new Date(checkIn);
    const end = new Date(checkOut);
    return Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));
  }, [checkIn, checkOut]);

  const priceBreakdown = useMemo(() => {
    if (!camp || nights <= 0) return null;
    return calculatePricePreview(camp, nights, adults, children, {
      includeBreakfast,
      includeLessons,
      lessonsCount,
      includeBoardRental,
    });
  }, [camp, nights, adults, children, includeBreakfast, includeLessons, lessonsCount, includeBoardRental]);

  const getMinCheckOut = () => {
    if (!checkIn) return '';
    const date = new Date(checkIn);
    date.setDate(date.getDate() + 1);
    return date.toISOString().split('T')[0];
  };

  const handleSubmit = async () => {
    if (!camp || !priceBreakdown || nights <= 0) return;

    setSubmitting(true);
    setError(null);

    try {
      const bookingData: BookingCreateData = {
        camp: camp.id,
        check_in: checkIn,
        check_out: checkOut,
        adults,
        children,
        package_type: packageType,
        include_breakfast: packageType === 'bnb' ? false : includeBreakfast,
        include_lessons: packageType === 'bnb' ? false : includeLessons,
        lessons_count: packageType === 'bnb' ? 0 : lessonsCount,
        include_board_rental: includeBoardRental,
        special_requests: specialRequests,
        arrival_time: arrivalTime,
      };

      const booking = await createBooking(bookingData);
      navigate(`/booking/${booking.booking_number}/guests`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create booking');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '3px solid #e2e8f0',
          borderTopColor: '#0ea5e9',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
        }} />
      </div>
    );
  }

  if (!camp) {
    return (
      <div style={{ minHeight: '100vh', padding: '100px 24px', textAlign: 'center' }}>
        <h2>{language === 'ru' ? 'Кемп не найден' : 'Camp not found'}</h2>
        <button onClick={() => navigate('/camps')}>{language === 'ru' ? 'Смотреть кемпы' : 'Browse camps'}</button>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Header */}
      <div style={{
        backgroundColor: 'white',
        borderBottom: '1px solid #e2e8f0',
        position: 'sticky',
        top: '72px',
        zIndex: 40,
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
        }}>
          <button
            onClick={() => navigate(`/camps/${slug}`)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              color: '#64748b',
              fontSize: '14px',
            }}
          >
            <ArrowLeft size={20} />
            {t('booking.backToCamp')}
          </button>
          <div style={{ flex: 1 }}>
            <h1 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>
              {t('booking.title')} {camp.name}
            </h1>
          </div>
        </div>

        {/* Progress steps */}
        <div style={{
          maxWidth: '600px',
          margin: '0 auto',
          padding: '0 24px 16px',
          display: 'flex',
          justifyContent: 'center',
          gap: '8px',
        }}>
          {[t('booking.step1'), t('booking.step2'), t('booking.step3')].map((step, index) => (
            <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '20px',
                backgroundColor: index === 0 ? '#0ea5e9' : '#f1f5f9',
                color: index === 0 ? 'white' : '#64748b',
              }}>
                <span style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: index === 0 ? 'white' : '#e2e8f0',
                  color: index === 0 ? '#0ea5e9' : '#64748b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 600,
                }}>
                  {index + 1}
                </span>
                <span style={{ fontSize: '13px', fontWeight: 500 }}>
                  {step}
                </span>
              </div>
              {index < 2 && (
                <ChevronRight size={16} style={{ color: '#cbd5e1', margin: '0 4px' }} />
              )}
            </div>
          ))}
        </div>
      </div>

      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '32px 24px',
        display: 'grid',
        gridTemplateColumns: '1fr 400px',
        gap: '32px',
      }}>
        {/* Main form */}
        <div>
          {/* Camp summary */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '24px',
            display: 'flex',
            gap: '16px',
          }}>
            <img
              src={camp.main_image || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200&h=150&fit=crop'}
              alt={camp.name}
              style={{
                width: '120px',
                height: '90px',
                objectFit: 'cover',
                borderRadius: '12px',
              }}
            />
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 4px' }}>{camp.name}</h2>
              <p style={{ fontSize: '14px', color: '#64748b', margin: '0 0 8px' }}>
                {camp.region_name}, {camp.country_name}
              </p>
              <div style={{ display: 'flex', gap: '8px' }}>
                {camp.skill_levels.map(level => (
                  <span key={level} style={{
                    padding: '4px 10px',
                    backgroundColor: '#f1f5f9',
                    borderRadius: '6px',
                    fontSize: '12px',
                    fontWeight: 500,
                  }}>
                    {language === 'ru'
                      ? (level === 'beginner' ? 'Начинающий' : level === 'intermediate' ? 'Средний' : 'Продвинутый')
                      : level.charAt(0).toUpperCase() + level.slice(1)}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Dates section */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Calendar size={20} color="#0ea5e9" />
              {t('booking.selectDates')}
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  {t('booking.checkIn')}
                </label>
                <input
                  type="date"
                  value={checkIn}
                  onChange={(e) => setCheckIn(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    fontSize: '15px',
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  {t('booking.checkOut')}
                </label>
                <input
                  type="date"
                  value={checkOut}
                  onChange={(e) => setCheckOut(e.target.value)}
                  min={getMinCheckOut()}
                  disabled={!checkIn}
                  style={{
                    width: '100%',
                    padding: '14px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '12px',
                    fontSize: '15px',
                    opacity: checkIn ? 1 : 0.5,
                  }}
                />
              </div>
            </div>
            {nights > 0 && (
              <p style={{ fontSize: '14px', color: '#0ea5e9', marginTop: '12px', fontWeight: 500 }}>
                {nights} {language === 'ru' ? (nights === 1 ? 'ночь' : nights < 5 ? 'ночи' : 'ночей') : (nights === 1 ? 'night' : 'nights')}
              </p>
            )}
          </div>

          {/* Guests section */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Users size={20} color="#0ea5e9" />
              {t('booking.guests')}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Adults */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: 500 }}>{t('booking.adults')}</div>
                  <div style={{ fontSize: '13px', color: '#64748b' }}>{t('booking.age18')}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button
                    onClick={() => setAdults(Math.max(1, adults - 1))}
                    disabled={adults <= 1}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1px solid #e2e8f0',
                      backgroundColor: 'white',
                      cursor: adults <= 1 ? 'not-allowed' : 'pointer',
                      opacity: adults <= 1 ? 0.5 : 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Minus size={16} />
                  </button>
                  <span style={{ fontSize: '16px', fontWeight: 600, width: '24px', textAlign: 'center' }}>
                    {adults}
                  </span>
                  <button
                    onClick={() => setAdults(Math.min(10, adults + 1))}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1px solid #e2e8f0',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
              {/* Children */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: 500 }}>{t('booking.children')}</div>
                  <div style={{ fontSize: '13px', color: '#64748b' }}>{t('booking.age017')}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button
                    onClick={() => setChildren(Math.max(0, children - 1))}
                    disabled={children <= 0}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1px solid #e2e8f0',
                      backgroundColor: 'white',
                      cursor: children <= 0 ? 'not-allowed' : 'pointer',
                      opacity: children <= 0 ? 0.5 : 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Minus size={16} />
                  </button>
                  <span style={{ fontSize: '16px', fontWeight: 600, width: '24px', textAlign: 'center' }}>
                    {children}
                  </span>
                  <button
                    onClick={() => setChildren(Math.min(10, children + 1))}
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '50%',
                      border: '1px solid #e2e8f0',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Plus size={16} />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Add-ons section */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px' }}>
              {t('booking.enhance')}
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Breakfast */}
              {camp.has_bed_breakfast && camp.bed_breakfast_price && (
                <label style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                  padding: '16px',
                  borderRadius: '12px',
                  border: includeBreakfast ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                  backgroundColor: includeBreakfast ? '#f0f9ff' : 'white',
                  cursor: 'pointer',
                }}>
                  <input
                    type="checkbox"
                    checked={includeBreakfast}
                    onChange={(e) => setIncludeBreakfast(e.target.checked)}
                    style={{ width: '20px', height: '20px', accentColor: '#0ea5e9', marginTop: '2px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <Coffee size={18} color="#f97316" />
                      <span style={{ fontSize: '15px', fontWeight: 600 }}>{t('booking.breakfast')}</span>
                    </div>
                    <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
                      {t('booking.breakfastDesc')}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '15px', fontWeight: 600 }}>${camp.bed_breakfast_price}</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>{t('booking.perPersonNight')}</div>
                  </div>
                </label>
              )}

              {/* Surf lessons */}
              {camp.price_per_lesson && (
                <label style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                  padding: '16px',
                  borderRadius: '12px',
                  border: includeLessons ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                  backgroundColor: includeLessons ? '#f0f9ff' : 'white',
                  cursor: 'pointer',
                }}>
                  <input
                    type="checkbox"
                    checked={includeLessons}
                    onChange={(e) => {
                      setIncludeLessons(e.target.checked);
                      if (e.target.checked && lessonsCount === 0) setLessonsCount(1);
                    }}
                    style={{ width: '20px', height: '20px', accentColor: '#0ea5e9', marginTop: '2px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <Waves size={18} color="#0ea5e9" />
                      <span style={{ fontSize: '15px', fontWeight: 600 }}>{t('booking.surfLessons')}</span>
                    </div>
                    <p style={{ fontSize: '13px', color: '#64748b', margin: '0 0 12px' }}>
                      {t('booking.lessonsDesc')}
                    </p>
                    {includeLessons && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '13px', color: '#64748b' }}>{t('booking.numLessons')}:</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); setLessonsCount(Math.max(1, lessonsCount - 1)); }}
                            style={{
                              width: '28px',
                              height: '28px',
                              borderRadius: '50%',
                              border: '1px solid #e2e8f0',
                              backgroundColor: 'white',
                              cursor: 'pointer',
                              fontSize: '14px',
                            }}
                          >
                            -
                          </button>
                          <span style={{ fontWeight: 600, width: '20px', textAlign: 'center' }}>{lessonsCount}</span>
                          <button
                            type="button"
                            onClick={(e) => { e.preventDefault(); setLessonsCount(lessonsCount + 1); }}
                            style={{
                              width: '28px',
                              height: '28px',
                              borderRadius: '50%',
                              border: '1px solid #e2e8f0',
                              backgroundColor: 'white',
                              cursor: 'pointer',
                              fontSize: '14px',
                            }}
                          >
                            +
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '15px', fontWeight: 600 }}>${camp.price_per_lesson}</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>{t('booking.perLesson')}</div>
                  </div>
                </label>
              )}

              {/* Board rental */}
              {camp.board_rental_available && camp.board_rental_price && (
                <label style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '16px',
                  padding: '16px',
                  borderRadius: '12px',
                  border: includeBoardRental ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                  backgroundColor: includeBoardRental ? '#f0f9ff' : 'white',
                  cursor: 'pointer',
                }}>
                  <input
                    type="checkbox"
                    checked={includeBoardRental}
                    onChange={(e) => setIncludeBoardRental(e.target.checked)}
                    style={{ width: '20px', height: '20px', accentColor: '#0ea5e9', marginTop: '2px' }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                      <Waves size={18} color="#10b981" />
                      <span style={{ fontSize: '15px', fontWeight: 600 }}>{t('booking.boardRental')}</span>
                    </div>
                    <p style={{ fontSize: '13px', color: '#64748b', margin: 0 }}>
                      {t('booking.boardDesc')}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '15px', fontWeight: 600 }}>${camp.board_rental_price}</div>
                    <div style={{ fontSize: '12px', color: '#64748b' }}>{t('booking.perDay')}</div>
                  </div>
                </label>
              )}
            </div>
          </div>

          {/* Special requests */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px' }}>
              {t('booking.additionalInfo')}
            </h3>
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                <Clock size={14} style={{ display: 'inline', marginRight: '6px' }} />
                {t('booking.arrivalTime')}
              </label>
              <select
                value={arrivalTime}
                onChange={(e) => setArrivalTime(e.target.value)}
                style={{
                  width: '200px',
                  padding: '12px 16px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  fontSize: '14px',
                }}
              >
                {Array.from({ length: 24 }, (_, i) => {
                  const hour = i.toString().padStart(2, '0');
                  return <option key={hour} value={`${hour}:00`}>{hour}:00</option>;
                })}
              </select>
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                {t('booking.specialRequests')}
              </label>
              <textarea
                value={specialRequests}
                onChange={(e) => setSpecialRequests(e.target.value)}
                placeholder={t('booking.requestsPlaceholder')}
                rows={3}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid #e2e8f0',
                  borderRadius: '12px',
                  fontSize: '14px',
                  resize: 'vertical',
                }}
              />
            </div>
          </div>
        </div>

        {/* Price summary sidebar */}
        <div>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            position: 'sticky',
            top: '180px',
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 20px' }}>
              {t('booking.priceSummary')}
            </h3>

            {!checkIn || !checkOut || nights <= 0 ? (
              <div style={{ textAlign: 'center', padding: '32px 0', color: '#64748b' }}>
                <Calendar size={32} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
                <p style={{ fontSize: '14px', margin: 0 }}>{t('booking.selectDatesToSee')}</p>
              </div>
            ) : priceBreakdown ? (
              <>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '20px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#64748b' }}>
                      ${camp.price_per_night} x {nights} {language === 'ru' ? (nights === 1 ? 'ночь' : nights < 5 ? 'ночи' : 'ночей') : (nights === 1 ? 'night' : 'nights')}
                    </span>
                    <span style={{ fontWeight: 500 }}>${priceBreakdown.accommodationTotal.toFixed(2)}</span>
                  </div>

                  {priceBreakdown.breakfastTotal > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Завтрак' : 'Breakfast'}</span>
                      <span style={{ fontWeight: 500 }}>${priceBreakdown.breakfastTotal.toFixed(2)}</span>
                    </div>
                  )}

                  {priceBreakdown.lessonsTotal > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Уроки серфинга' : 'Surf lessons'} ({lessonsCount}x)</span>
                      <span style={{ fontWeight: 500 }}>${priceBreakdown.lessonsTotal.toFixed(2)}</span>
                    </div>
                  )}

                  {priceBreakdown.boardRentalTotal > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Аренда доски' : 'Board rental'}</span>
                      <span style={{ fontWeight: 500 }}>${priceBreakdown.boardRentalTotal.toFixed(2)}</span>
                    </div>
                  )}

                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#64748b' }}>{t('booking.serviceFee')} (10%)</span>
                    <span style={{ fontWeight: 500 }}>${priceBreakdown.serviceFee.toFixed(2)}</span>
                  </div>
                </div>

                <div style={{
                  borderTop: '1px solid #e2e8f0',
                  paddingTop: '16px',
                  marginBottom: '24px',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: '18px', fontWeight: 600 }}>{t('booking.total')}</span>
                    <span style={{ fontSize: '18px', fontWeight: 700 }}>${priceBreakdown.total.toFixed(2)}</span>
                  </div>
                </div>

                {error && (
                  <div style={{
                    padding: '12px 16px',
                    backgroundColor: '#fef2f2',
                    borderRadius: '8px',
                    color: '#dc2626',
                    fontSize: '14px',
                    marginBottom: '16px',
                  }}>
                    {error}
                  </div>
                )}

                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  style={{
                    width: '100%',
                    padding: '16px',
                    backgroundColor: submitting ? '#94a3b8' : '#0ea5e9',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: 600,
                    cursor: submitting ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                  }}
                >
                  {submitting ? t('booking.processing') : (
                    <>
                      {t('booking.continue')}
                      <ChevronRight size={20} />
                    </>
                  )}
                </button>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                  marginTop: '16px',
                  color: '#64748b',
                  fontSize: '13px',
                }}>
                  <Check size={16} color="#10b981" />
                  {t('booking.freeCancellation')}
                </div>
              </>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}
