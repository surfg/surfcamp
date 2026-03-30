import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, Calendar, MapPin, Users, Mail, Phone, Download, Share2 } from 'lucide-react';
import { getBooking } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { Booking } from '../types';

export function ConfirmationPage() {
  const { bookingNumber } = useParams<{ bookingNumber: string }>();
  const { t, language } = useLanguage();
  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    if (!bookingNumber) return;
    getBooking(bookingNumber)
      .then(setBooking)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [bookingNumber]);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
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

  if (!booking) {
    return (
      <div style={{ minHeight: '100vh', padding: '100px 24px', textAlign: 'center' }}>
        <h2>{language === 'ru' ? 'Бронирование не найдено' : 'Booking not found'}</h2>
      </div>
    );
  }

  const primaryGuest = booking.guests.find(g => g.is_primary) || booking.guests[0];

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8fafc' }}>
      {/* Success header */}
      <div style={{
        backgroundColor: '#10b981',
        color: 'white',
        padding: '48px 24px',
        textAlign: 'center',
      }}>
        <div style={{
          width: '80px',
          height: '80px',
          backgroundColor: 'white',
          borderRadius: '50%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 20px',
        }}>
          <CheckCircle size={48} color="#10b981" />
        </div>
        <h1 style={{ fontSize: '28px', fontWeight: 700, margin: '0 0 8px' }}>
          {t('confirmation.title')}
        </h1>
        <p style={{ fontSize: '16px', opacity: 0.9, margin: 0, maxWidth: '500px', marginLeft: 'auto', marginRight: 'auto' }}>
          {t('confirmation.managerContact')}
        </p>
      </div>

      <div style={{
        maxWidth: '900px',
        margin: '-32px auto 0',
        padding: '0 24px 48px',
      }}>
        {/* Booking card */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '20px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          marginBottom: '24px',
        }}>
          {/* Booking number banner */}
          <div style={{
            backgroundColor: '#0f172a',
            color: 'white',
            padding: '20px 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '12px',
          }}>
            <div>
              <div style={{ fontSize: '12px', opacity: 0.7, marginBottom: '4px' }}>{t('confirmation.number')}</div>
              <div style={{ fontSize: '24px', fontWeight: 700, fontFamily: 'monospace' }}>
                {booking.booking_number}
              </div>
            </div>
            <div style={{
              padding: '8px 16px',
              backgroundColor: '#f59e0b',
              borderRadius: '20px',
              fontSize: '13px',
              fontWeight: 600,
              textTransform: 'uppercase',
            }}>
              {language === 'ru' ? 'Ожидает подтверждения' : 'Pending confirmation'}
            </div>
          </div>

          {/* Camp details */}
          <div style={{ padding: '24px' }}>
            <div style={{
              display: 'flex',
              gap: '20px',
              paddingBottom: '24px',
              borderBottom: '1px solid #e2e8f0',
              marginBottom: '24px',
            }}>
              <img
                src={booking.camp_image || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=200'}
                alt={booking.camp_name}
                style={{
                  width: '140px',
                  height: '100px',
                  borderRadius: '12px',
                  objectFit: 'cover',
                }}
              />
              <div>
                <h2 style={{ fontSize: '20px', fontWeight: 600, margin: '0 0 8px' }}>
                  {booking.camp_name}
                </h2>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#64748b', marginBottom: '12px' }}>
                  <MapPin size={16} />
                  <span style={{ fontSize: '14px' }}>{booking.camp_address}</span>
                </div>
                <Link
                  to={`/camps/${booking.camp_slug}`}
                  style={{
                    fontSize: '14px',
                    color: '#0ea5e9',
                    textDecoration: 'none',
                    fontWeight: 500,
                  }}
                >
                  {language === 'ru' ? 'Посмотреть кемп' : 'View camp details'}
                </Link>
              </div>
            </div>

            {/* Dates and guests */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: '24px',
              marginBottom: '24px',
            }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Calendar size={18} color="#0ea5e9" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#64748b' }}>{language === 'ru' ? 'ЗАЕЗД' : 'CHECK-IN'}</span>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 600 }}>
                  {new Date(booking.check_in).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>{language === 'ru' ? 'С 14:00' : 'From 2:00 PM'}</div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Calendar size={18} color="#0ea5e9" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#64748b' }}>{language === 'ru' ? 'ВЫЕЗД' : 'CHECK-OUT'}</span>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 600 }}>
                  {new Date(booking.check_out).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US', {
                    weekday: 'short',
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric',
                  })}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>{language === 'ru' ? 'До 11:00' : 'Until 11:00 AM'}</div>
              </div>

              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                  <Users size={18} color="#0ea5e9" />
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#64748b' }}>{language === 'ru' ? 'ГОСТИ' : 'GUESTS'}</span>
                </div>
                <div style={{ fontSize: '16px', fontWeight: 600 }}>
                  {booking.adults} {language === 'ru' ? (booking.adults === 1 ? 'взрослый' : 'взрослых') : (booking.adults === 1 ? 'adult' : 'adults')}
                  {booking.children > 0 && `, ${booking.children} ${language === 'ru' ? (booking.children === 1 ? 'ребёнок' : 'детей') : (booking.children === 1 ? 'child' : 'children')}`}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>
                  {booking.nights} {language === 'ru' ? (booking.nights === 1 ? 'ночь' : booking.nights < 5 ? 'ночи' : 'ночей') : 'nights'} {language === 'ru' ? 'всего' : 'total'}
                </div>
              </div>
            </div>

            {/* Add-ons */}
            {(booking.include_breakfast || booking.include_lessons || booking.include_board_rental) && (
              <div style={{
                backgroundColor: '#f8fafc',
                borderRadius: '12px',
                padding: '16px',
                marginBottom: '24px',
              }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: '#64748b', marginBottom: '12px' }}>
                  {language === 'ru' ? 'ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ' : 'INCLUDED EXTRAS'}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {booking.include_breakfast && (
                    <span style={{
                      padding: '6px 12px',
                      backgroundColor: 'white',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: 500,
                    }}>
                      {language === 'ru' ? 'Завтрак включён' : 'Breakfast included'}
                    </span>
                  )}
                  {booking.include_lessons && (
                    <span style={{
                      padding: '6px 12px',
                      backgroundColor: 'white',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: 500,
                    }}>
                      {booking.lessons_count} {language === 'ru' ? 'уроков серфинга' : 'Surf lessons'}
                    </span>
                  )}
                  {booking.include_board_rental && (
                    <span style={{
                      padding: '6px 12px',
                      backgroundColor: 'white',
                      borderRadius: '20px',
                      fontSize: '13px',
                      fontWeight: 500,
                    }}>
                      {language === 'ru' ? 'Аренда доски' : 'Board rental'}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Price summary */}
            <div style={{
              backgroundColor: '#f8fafc',
              borderRadius: '12px',
              padding: '20px',
            }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: '#64748b', marginBottom: '16px' }}>
                {language === 'ru' ? 'ПРЕДВАРИТЕЛЬНАЯ СТОИМОСТЬ' : 'ESTIMATED PRICE'}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Проживание' : 'Accommodation'} ({booking.nights} {language === 'ru' ? (booking.nights === 1 ? 'ночь' : booking.nights < 5 ? 'ночи' : 'ночей') : 'nights'})</span>
                  <span>${(booking.price_per_night * booking.nights).toFixed(2)}</span>
                </div>
                {Number(booking.breakfast_total) > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                    <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Завтрак' : 'Breakfast'}</span>
                    <span>${Number(booking.breakfast_total).toFixed(2)}</span>
                  </div>
                )}
                {Number(booking.lessons_total) > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                    <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Уроки серфинга' : 'Surf lessons'}</span>
                    <span>${Number(booking.lessons_total).toFixed(2)}</span>
                  </div>
                )}
                {Number(booking.board_rental_total) > 0 && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                    <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Аренда доски' : 'Board rental'}</span>
                    <span>${Number(booking.board_rental_total).toFixed(2)}</span>
                  </div>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#64748b' }}>{t('booking.serviceFee')}</span>
                  <span>${Number(booking.service_fee).toFixed(2)}</span>
                </div>
                <div style={{
                  borderTop: '1px solid #e2e8f0',
                  marginTop: '8px',
                  paddingTop: '12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                }}>
                  <span style={{ fontSize: '16px', fontWeight: 600 }}>{language === 'ru' ? 'Итого' : 'Total'}</span>
                  <span style={{ fontSize: '16px', fontWeight: 700, color: '#0ea5e9' }}>
                    ${Number(booking.total_price).toFixed(2)}
                  </span>
                </div>
              </div>
              <p style={{ fontSize: '13px', color: '#64748b', marginTop: '12px', marginBottom: 0 }}>
                {language === 'ru'
                  ? '* Окончательная стоимость будет согласована с менеджером'
                  : '* Final price will be confirmed by our manager'}
              </p>
            </div>
          </div>
        </div>

        {/* Guest information */}
        {primaryGuest && (
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 16px' }}>
              {language === 'ru' ? 'Контактная информация' : 'Contact Information'}
            </h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#f1f5f9',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Mail size={18} color="#64748b" />
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>Email</div>
                  <div style={{ fontSize: '14px', fontWeight: 500 }}>{primaryGuest.email}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: '#f1f5f9',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Phone size={18} color="#64748b" />
                </div>
                <div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>{t('guest.phone')}</div>
                  <div style={{ fontSize: '14px', fontWeight: 500 }}>{primaryGuest.phone}</div>
                </div>
              </div>
            </div>
            <p style={{ fontSize: '13px', color: '#64748b', marginTop: '16px', marginBottom: 0 }}>
              {language === 'ru'
                ? `Подтверждение отправлено на ${primaryGuest.email}`
                : `A confirmation email has been sent to ${primaryGuest.email}`}
            </p>
          </div>
        )}

        {/* Actions */}
        <div style={{
          display: 'flex',
          gap: '12px',
          justifyContent: 'center',
          flexWrap: 'wrap',
        }}>
          <button
            onClick={() => window.print()}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '14px 24px',
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <Download size={18} />
            {t('confirmation.download')}
          </button>
          <button
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '14px 24px',
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <Share2 size={18} />
            {language === 'ru' ? 'Поделиться' : 'Share'}
          </button>
          <Link
            to="/camps"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '14px 24px',
              backgroundColor: '#0ea5e9',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '14px',
              fontWeight: 600,
              textDecoration: 'none',
            }}
          >
            {language === 'ru' ? 'Смотреть другие кемпы' : 'Browse more camps'}
          </Link>
        </div>
      </div>
    </div>
  );
}
