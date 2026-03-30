import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronRight, User, Phone, Mail, MapPin, AlertCircle, Waves } from 'lucide-react';
import { getBooking, updateBookingGuests } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { Booking, Guest } from '../types';

const emptyGuest = (): Omit<Guest, 'id'> => ({
  is_primary: false,
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  country: '',
  city: '',
  surf_level: 'beginner',
  emergency_name: '',
  emergency_phone: '',
});

export function GuestInfoPage() {
  const { bookingNumber } = useParams<{ bookingNumber: string }>();
  const navigate = useNavigate();
  const { t, language } = useLanguage();

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [guests, setGuests] = useState<Omit<Guest, 'id'>[]>([]);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, []);

  useEffect(() => {
    if (!bookingNumber) return;
    getBooking(bookingNumber)
      .then((data) => {
        setBooking(data);
        const totalGuests = data.adults + data.children;
        const existingGuests = data.guests.length > 0
          ? data.guests.map(g => ({ ...g }))
          : Array.from({ length: totalGuests }, (_, i) => ({ ...emptyGuest(), is_primary: i === 0 }));
        setGuests(existingGuests);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [bookingNumber]);

  const updateGuest = (index: number, field: keyof Omit<Guest, 'id'>, value: string | boolean) => {
    setGuests(prev => prev.map((g, i) => i === index ? { ...g, [field]: value } : g));
  };

  const validateForm = (): boolean => {
    for (let i = 0; i < guests.length; i++) {
      const g = guests[i];
      if (!g.first_name || !g.last_name || !g.email || !g.phone) {
        setError(language === 'ru'
          ? `Заполните все обязательные поля для Гостя ${i + 1}`
          : `Please fill in all required fields for Guest ${i + 1}`);
        return false;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(g.email)) {
        setError(language === 'ru'
          ? `Некорректный email для Гостя ${i + 1}`
          : `Invalid email for Guest ${i + 1}`);
        return false;
      }
    }
    // Primary guest needs emergency contact
    const primary = guests[0];
    if (!primary.emergency_name || !primary.emergency_phone) {
      setError(language === 'ru'
        ? 'Укажите контакт для экстренной связи'
        : 'Please provide emergency contact information');
      return false;
    }
    return true;
  };

  const handleSubmit = async () => {
    if (!bookingNumber || !validateForm()) return;

    setSubmitting(true);
    setError(null);

    try {
      await updateBookingGuests(bookingNumber, guests);
      navigate(`/booking/${bookingNumber}/confirmation`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save guest information');
    } finally {
      setSubmitting(false);
    }
  };

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
            onClick={() => navigate(-1)}
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
            {language === 'ru' ? 'Назад' : 'Back'}
          </button>
          <h1 style={{ fontSize: '18px', fontWeight: 600, margin: 0, flex: 1 }}>
            {t('guest.title')}
          </h1>
        </div>

        {/* Progress */}
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
                backgroundColor: index <= 1 ? (index === 1 ? '#0ea5e9' : '#10b981') : '#f1f5f9',
                color: index <= 1 ? 'white' : '#64748b',
              }}>
                <span style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: index <= 1 ? 'white' : '#e2e8f0',
                  color: index === 1 ? '#0ea5e9' : index === 0 ? '#10b981' : '#64748b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 600,
                }}>
                  {index === 0 ? '✓' : index + 1}
                </span>
                <span style={{ fontSize: '13px', fontWeight: 500 }}>
                  {step}
                </span>
              </div>
              {index < 2 && <ChevronRight size={16} style={{ color: '#cbd5e1', margin: '0 4px' }} />}
            </div>
          ))}
        </div>
      </div>

      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '32px 24px',
      }}>
        {/* Booking summary */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '16px',
          padding: '20px',
          marginBottom: '24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}>
          <div>
            <div style={{ fontSize: '14px', color: '#64748b' }}>{language === 'ru' ? 'Бронирование' : 'Booking'} #{booking.booking_number}</div>
            <div style={{ fontSize: '16px', fontWeight: 600 }}>{booking.camp_name}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', color: '#64748b' }}>
              {new Date(booking.check_in).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')} - {new Date(booking.check_out).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')}
            </div>
            <div style={{ fontSize: '16px', fontWeight: 600 }}>
              {booking.nights} {language === 'ru' ? (booking.nights === 1 ? 'ночь' : booking.nights < 5 ? 'ночи' : 'ночей') : (booking.nights === 1 ? 'night' : 'nights')} · {booking.adults + booking.children} {language === 'ru' ? 'гостей' : 'guests'}
            </div>
          </div>
        </div>

        {error && (
          <div style={{
            padding: '16px',
            backgroundColor: '#fef2f2',
            borderRadius: '12px',
            color: '#dc2626',
            marginBottom: '24px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
          }}>
            <AlertCircle size={20} />
            {error}
          </div>
        )}

        {/* Guest forms */}
        {guests.map((guest, index) => (
          <div key={index} style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{
              fontSize: '16px',
              fontWeight: 600,
              margin: '0 0 20px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <User size={20} color="#0ea5e9" />
              {index === 0
                ? (language === 'ru' ? 'Основной гость (ответственный)' : 'Primary Guest (Lead Booker)')
                : (language === 'ru' ? `Гость ${index + 1}` : `Guest ${index + 1}`)}
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
              {/* First Name */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  {t('guest.firstName')} *
                </label>
                <input
                  type="text"
                  value={guest.first_name}
                  onChange={(e) => updateGuest(index, 'first_name', e.target.value)}
                  placeholder={language === 'ru' ? 'Иван' : 'John'}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* Last Name */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  {t('guest.lastName')} *
                </label>
                <input
                  type="text"
                  value={guest.last_name}
                  onChange={(e) => updateGuest(index, 'last_name', e.target.value)}
                  placeholder={language === 'ru' ? 'Иванов' : 'Doe'}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* Email */}
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  <Mail size={14} />
                  {t('guest.email')} *
                </label>
                <input
                  type="email"
                  value={guest.email}
                  onChange={(e) => updateGuest(index, 'email', e.target.value)}
                  placeholder={language === 'ru' ? 'ivan@example.com' : 'john@example.com'}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* Phone */}
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  <Phone size={14} />
                  {t('guest.phone')} *
                </label>
                <input
                  type="tel"
                  value={guest.phone}
                  onChange={(e) => updateGuest(index, 'phone', e.target.value)}
                  placeholder="+7 999 123 4567"
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* Country */}
              <div>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  <MapPin size={14} />
                  {t('guest.country')}
                </label>
                <input
                  type="text"
                  value={guest.country}
                  onChange={(e) => updateGuest(index, 'country', e.target.value)}
                  placeholder={language === 'ru' ? 'Россия' : 'United States'}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* City */}
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  {t('guest.city')}
                </label>
                <input
                  type="text"
                  value={guest.city}
                  onChange={(e) => updateGuest(index, 'city', e.target.value)}
                  placeholder={language === 'ru' ? 'Москва' : 'Los Angeles'}
                  style={{
                    width: '100%',
                    padding: '12px 16px',
                    border: '1px solid #e2e8f0',
                    borderRadius: '10px',
                    fontSize: '14px',
                  }}
                />
              </div>

              {/* Surf Level */}
              <div style={{ gridColumn: '1 / -1' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                  <Waves size={14} />
                  {t('guest.surfLevel')}
                </label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  {(['beginner', 'intermediate', 'advanced'] as const).map(level => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => updateGuest(index, 'surf_level', level)}
                      style={{
                        padding: '10px 20px',
                        borderRadius: '20px',
                        border: guest.surf_level === level ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                        backgroundColor: guest.surf_level === level ? '#f0f9ff' : 'white',
                        color: guest.surf_level === level ? '#0ea5e9' : '#0f172a',
                        fontSize: '14px',
                        fontWeight: 500,
                        cursor: 'pointer',
                      }}
                    >
                      {language === 'ru'
                        ? (level === 'beginner' ? 'Начинающий' : level === 'intermediate' ? 'Средний' : 'Продвинутый')
                        : level.charAt(0).toUpperCase() + level.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Emergency contact for primary guest */}
            {index === 0 && (
              <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid #e2e8f0' }}>
                <h4 style={{ fontSize: '14px', fontWeight: 600, margin: '0 0 16px', color: '#64748b' }}>
                  {t('guest.emergency')} *
                </h4>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                      {t('guest.emergencyName')}
                    </label>
                    <input
                      type="text"
                      value={guest.emergency_name}
                      onChange={(e) => updateGuest(index, 'emergency_name', e.target.value)}
                      placeholder={language === 'ru' ? 'Анна Иванова' : 'Jane Doe'}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '10px',
                        fontSize: '14px',
                      }}
                    />
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                      {t('guest.emergencyPhone')}
                    </label>
                    <input
                      type="tel"
                      value={guest.emergency_phone}
                      onChange={(e) => updateGuest(index, 'emergency_phone', e.target.value)}
                      placeholder="+7 999 123 4567"
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '10px',
                        fontSize: '14px',
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}

        {/* Submit */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '24px 0',
        }}>
          <button
            onClick={() => navigate(-1)}
            style={{
              padding: '14px 24px',
              backgroundColor: 'white',
              border: '1px solid #e2e8f0',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            {language === 'ru' ? 'Назад' : 'Back'}
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            style={{
              padding: '14px 32px',
              backgroundColor: submitting ? '#94a3b8' : '#0ea5e9',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '15px',
              fontWeight: 600,
              cursor: submitting ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            {submitting
              ? (language === 'ru' ? 'Оформление...' : 'Submitting...')
              : t('guest.continueCheckout')}
            <ChevronRight size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}
