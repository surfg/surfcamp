import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, ChevronRight, CreditCard, Lock, Shield } from 'lucide-react';
import { getBooking, processPayment } from '../lib/api';
import { useLanguage } from '../contexts/LanguageContext';
import type { Booking, PaymentData } from '../types';

export function PaymentPage() {
  const { bookingNumber } = useParams<{ bookingNumber: string }>();
  const navigate = useNavigate();
  const { t, language } = useLanguage();

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [paymentMethod, setPaymentMethod] = useState<'card' | 'paypal'>('card');
  const [cardNumber, setCardNumber] = useState('');
  const [cardExpiry, setCardExpiry] = useState('');
  const [cardCvc, setCardCvc] = useState('');
  const [cardHolder, setCardHolder] = useState('');
  const [agreeTerms, setAgreeTerms] = useState(false);

  useEffect(() => {
    if (!bookingNumber) return;
    getBooking(bookingNumber)
      .then(setBooking)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [bookingNumber]);

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    return parts.length ? parts.join(' ') : value;
  };

  const formatExpiry = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  const detectCardType = (number: string): string => {
    const n = number.replace(/\s/g, '');
    if (n.startsWith('4')) return 'visa';
    if (/^5[1-5]/.test(n)) return 'mastercard';
    if (/^3[47]/.test(n)) return 'amex';
    return 'card';
  };

  const handleSubmit = async () => {
    if (!bookingNumber || !agreeTerms) return;

    if (paymentMethod === 'card') {
      if (!cardNumber || !cardExpiry || !cardCvc || !cardHolder) {
        setError(language === 'ru' ? 'Заполните все данные карты' : 'Please fill in all card details');
        return;
      }
      if (cardNumber.replace(/\s/g, '').length < 16) {
        setError(language === 'ru' ? 'Некорректный номер карты' : 'Invalid card number');
        return;
      }
    }

    setProcessing(true);
    setError(null);

    try {
      const paymentData: PaymentData = {
        method: paymentMethod,
        ...(paymentMethod === 'card' && {
          card_number: cardNumber.replace(/\s/g, ''),
          card_expiry: cardExpiry,
          card_cvc: cardCvc,
          card_holder: cardHolder,
        }),
      };

      await processPayment(bookingNumber, paymentData);
      navigate(`/booking/${bookingNumber}/confirmation`);
    } catch (err) {
      setError(err instanceof Error ? err.message : (language === 'ru' ? 'Ошибка оплаты' : 'Payment failed'));
    } finally {
      setProcessing(false);
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

  const primaryGuest = booking.guests.find(g => g.is_primary) || booking.guests[0];

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
            }}
          >
            <ArrowLeft size={20} />
          </button>
          <h1 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>
            {language === 'ru' ? 'Завершите бронирование' : 'Complete your booking'}
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
          {[t('booking.step1'), t('booking.step2'), t('booking.step3'), t('booking.step4')].map((step, index) => (
            <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '20px',
                backgroundColor: index <= 2 ? (index === 2 ? '#0ea5e9' : '#10b981') : '#f1f5f9',
                color: index <= 2 ? 'white' : '#64748b',
              }}>
                <span style={{
                  width: '20px',
                  height: '20px',
                  borderRadius: '50%',
                  backgroundColor: index <= 2 ? 'white' : '#e2e8f0',
                  color: index === 2 ? '#0ea5e9' : index < 2 ? '#10b981' : '#64748b',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '12px',
                  fontWeight: 600,
                }}>
                  {index < 2 ? '✓' : index + 1}
                </span>
                <span style={{ fontSize: '13px', fontWeight: 500, display: index > 2 ? 'none' : undefined }}>
                  {step}
                </span>
              </div>
              {index < 3 && <ChevronRight size={16} style={{ color: '#cbd5e1', margin: '0 4px' }} />}
            </div>
          ))}
        </div>
      </div>

      <div style={{
        maxWidth: '1100px',
        margin: '0 auto',
        padding: '32px 24px',
        display: 'grid',
        gridTemplateColumns: '1fr 380px',
        gap: '32px',
      }}>
        {/* Payment form */}
        <div>
          {/* Payment method selection */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px' }}>
              {t('payment.method')}
            </h3>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setPaymentMethod('card')}
                style={{
                  flex: 1,
                  padding: '16px',
                  borderRadius: '12px',
                  border: paymentMethod === 'card' ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                  backgroundColor: paymentMethod === 'card' ? '#f0f9ff' : 'white',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <CreditCard size={24} color={paymentMethod === 'card' ? '#0ea5e9' : '#64748b'} />
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontWeight: 600, color: paymentMethod === 'card' ? '#0ea5e9' : '#0f172a' }}>{t('payment.card')}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>Visa, Mastercard, Amex</div>
                </div>
              </button>
              <button
                onClick={() => setPaymentMethod('paypal')}
                style={{
                  flex: 1,
                  padding: '16px',
                  borderRadius: '12px',
                  border: paymentMethod === 'paypal' ? '2px solid #0ea5e9' : '1px solid #e2e8f0',
                  backgroundColor: paymentMethod === 'paypal' ? '#f0f9ff' : 'white',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                }}
              >
                <div style={{
                  width: '24px',
                  height: '24px',
                  backgroundColor: '#003087',
                  borderRadius: '4px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '12px',
                  fontWeight: 700,
                }}>P</div>
                <div style={{ textAlign: 'left' }}>
                  <div style={{ fontWeight: 600, color: paymentMethod === 'paypal' ? '#0ea5e9' : '#0f172a' }}>{t('payment.paypal')}</div>
                  <div style={{ fontSize: '12px', color: '#64748b' }}>{language === 'ru' ? 'Оплата через PayPal' : 'Pay with PayPal'}</div>
                </div>
              </button>
            </div>
          </div>

          {/* Card details */}
          {paymentMethod === 'card' && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '24px',
              marginBottom: '24px',
            }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <CreditCard size={20} color="#0ea5e9" />
                {language === 'ru' ? 'Данные карты' : 'Card details'}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {/* Card number */}
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                    {t('payment.cardNumber')}
                  </label>
                  <div style={{ position: 'relative' }}>
                    <input
                      type="text"
                      value={cardNumber}
                      onChange={(e) => setCardNumber(formatCardNumber(e.target.value))}
                      placeholder="1234 5678 9012 3456"
                      maxLength={19}
                      style={{
                        width: '100%',
                        padding: '14px 50px 14px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        fontSize: '16px',
                        fontFamily: 'monospace',
                      }}
                    />
                    <div style={{
                      position: 'absolute',
                      right: '16px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      fontSize: '12px',
                      fontWeight: 600,
                      color: '#64748b',
                      textTransform: 'uppercase',
                    }}>
                      {detectCardType(cardNumber)}
                    </div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  {/* Expiry */}
                  <div>
                    <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                      {t('payment.expiry')}
                    </label>
                    <input
                      type="text"
                      value={cardExpiry}
                      onChange={(e) => setCardExpiry(formatExpiry(e.target.value))}
                      placeholder="MM/YY"
                      maxLength={5}
                      style={{
                        width: '100%',
                        padding: '14px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        fontSize: '16px',
                        fontFamily: 'monospace',
                      }}
                    />
                  </div>

                  {/* CVC */}
                  <div>
                    <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                      {t('payment.cvv')}
                    </label>
                    <input
                      type="text"
                      value={cardCvc}
                      onChange={(e) => setCardCvc(e.target.value.replace(/\D/g, '').slice(0, 4))}
                      placeholder="123"
                      maxLength={4}
                      style={{
                        width: '100%',
                        padding: '14px 16px',
                        border: '1px solid #e2e8f0',
                        borderRadius: '12px',
                        fontSize: '16px',
                        fontFamily: 'monospace',
                      }}
                    />
                  </div>
                </div>

                {/* Card holder */}
                <div>
                  <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#64748b', marginBottom: '8px' }}>
                    {t('payment.cardHolder')}
                  </label>
                  <input
                    type="text"
                    value={cardHolder}
                    onChange={(e) => setCardHolder(e.target.value.toUpperCase())}
                    placeholder={language === 'ru' ? 'ИВАН ИВАНОВ' : 'JOHN DOE'}
                    style={{
                      width: '100%',
                      padding: '14px 16px',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      fontSize: '16px',
                      textTransform: 'uppercase',
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* PayPal */}
          {paymentMethod === 'paypal' && (
            <div style={{
              backgroundColor: 'white',
              borderRadius: '16px',
              padding: '40px',
              marginBottom: '24px',
              textAlign: 'center',
            }}>
              <div style={{
                width: '64px',
                height: '64px',
                backgroundColor: '#003087',
                borderRadius: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
                color: 'white',
                fontSize: '24px',
                fontWeight: 700,
              }}>P</div>
              <h3 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 8px' }}>PayPal</h3>
              <p style={{ color: '#64748b', margin: 0 }}>
                {language === 'ru' ? 'Вы будете перенаправлены в PayPal для завершения оплаты' : 'You will be redirected to PayPal to complete your payment'}
              </p>
            </div>
          )}

          {/* Billing address */}
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            marginBottom: '24px',
          }}>
            <h3 style={{ fontSize: '16px', fontWeight: 600, margin: '0 0 16px' }}>
              {language === 'ru' ? 'Платёжные данные' : 'Billing details'}
            </h3>
            {primaryGuest && (
              <div style={{
                padding: '16px',
                backgroundColor: '#f8fafc',
                borderRadius: '12px',
              }}>
                <div style={{ fontWeight: 500 }}>{primaryGuest.first_name} {primaryGuest.last_name}</div>
                <div style={{ fontSize: '14px', color: '#64748b' }}>{primaryGuest.email}</div>
                {primaryGuest.city && primaryGuest.country && (
                  <div style={{ fontSize: '14px', color: '#64748b' }}>{primaryGuest.city}, {primaryGuest.country}</div>
                )}
              </div>
            )}
          </div>

          {/* Terms */}
          <label style={{
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px',
            padding: '16px',
            backgroundColor: 'white',
            borderRadius: '12px',
            cursor: 'pointer',
            marginBottom: '24px',
          }}>
            <input
              type="checkbox"
              checked={agreeTerms}
              onChange={(e) => setAgreeTerms(e.target.checked)}
              style={{ width: '20px', height: '20px', accentColor: '#0ea5e9', marginTop: '2px' }}
            />
            <span style={{ fontSize: '14px', color: '#64748b' }}>
              {language === 'ru'
                ? <>Я согласен с <a href="#" style={{ color: '#0ea5e9' }}>Условиями использования</a> и <a href="#" style={{ color: '#0ea5e9' }}>Политикой отмены</a>. Я понимаю, что это бронирование является окончательным и не подлежит возврату в течение 48 часов до заезда.</>
                : <>I agree to the <a href="#" style={{ color: '#0ea5e9' }}>Terms & Conditions</a> and <a href="#" style={{ color: '#0ea5e9' }}>Cancellation Policy</a>. I understand that this booking is final and non-refundable within 48 hours of check-in.</>}
            </span>
          </label>

          {error && (
            <div style={{
              padding: '16px',
              backgroundColor: '#fef2f2',
              borderRadius: '12px',
              color: '#dc2626',
              marginBottom: '24px',
            }}>
              {error}
            </div>
          )}
        </div>

        {/* Order summary */}
        <div>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '16px',
            padding: '24px',
            position: 'sticky',
            top: '180px',
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: 600, margin: '0 0 20px' }}>
              {language === 'ru' ? 'Детали заказа' : 'Order summary'}
            </h3>

            {/* Camp info */}
            <div style={{
              display: 'flex',
              gap: '12px',
              paddingBottom: '16px',
              borderBottom: '1px solid #e2e8f0',
              marginBottom: '16px',
            }}>
              <img
                src={booking.camp_image || 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=100'}
                alt=""
                style={{ width: '80px', height: '60px', borderRadius: '8px', objectFit: 'cover' }}
              />
              <div>
                <div style={{ fontWeight: 600, fontSize: '14px' }}>{booking.camp_name}</div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>
                  {new Date(booking.check_in).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')} - {new Date(booking.check_out).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')}
                </div>
                <div style={{ fontSize: '13px', color: '#64748b' }}>
                  {booking.nights} {language === 'ru' ? (booking.nights === 1 ? 'ночь' : booking.nights < 5 ? 'ночи' : 'ночей') : 'nights'} · {booking.adults + booking.children} {language === 'ru' ? 'гостей' : 'guests'}
                </div>
              </div>
            </div>

            {/* Price breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Проживание' : 'Accommodation'}</span>
                <span>${(booking.price_per_night * booking.nights).toFixed(2)}</span>
              </div>
              {booking.breakfast_total > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Завтрак' : 'Breakfast'}</span>
                  <span>${Number(booking.breakfast_total).toFixed(2)}</span>
                </div>
              )}
              {booking.lessons_total > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Уроки серфинга' : 'Surf lessons'}</span>
                  <span>${Number(booking.lessons_total).toFixed(2)}</span>
                </div>
              )}
              {booking.board_rental_total > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                  <span style={{ color: '#64748b' }}>{language === 'ru' ? 'Аренда доски' : 'Board rental'}</span>
                  <span>${Number(booking.board_rental_total).toFixed(2)}</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px' }}>
                <span style={{ color: '#64748b' }}>{t('booking.serviceFee')}</span>
                <span>${Number(booking.service_fee).toFixed(2)}</span>
              </div>
            </div>

            <div style={{
              borderTop: '1px solid #e2e8f0',
              paddingTop: '16px',
              marginBottom: '24px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '18px', fontWeight: 600 }}>{t('booking.total')}</span>
                <span style={{ fontSize: '18px', fontWeight: 700 }}>${Number(booking.total_price).toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={handleSubmit}
              disabled={processing || !agreeTerms}
              style={{
                width: '100%',
                padding: '16px',
                backgroundColor: processing || !agreeTerms ? '#94a3b8' : '#0ea5e9',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: processing || !agreeTerms ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
              }}
            >
              {processing ? (
                language === 'ru' ? 'Обработка...' : 'Processing...'
              ) : (
                <>
                  <Lock size={18} />
                  {t('payment.payNow')} ${Number(booking.total_price).toFixed(2)}
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
              fontSize: '12px',
            }}>
              <Shield size={14} />
              {t('payment.secure')}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
