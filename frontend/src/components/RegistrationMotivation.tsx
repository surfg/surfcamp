import { useState, useEffect } from 'react';
import { X, Gift, Percent, Bell, Heart, ChevronRight } from 'lucide-react';

interface RegistrationMotivationProps {
  isLoggedIn: boolean;
  onRegister?: () => void;
  onClose?: () => void;
}

// Check if popup was shown recently
function shouldShowPopup(): boolean {
  const lastShown = localStorage.getItem('reg_popup_shown');
  if (!lastShown) return true;

  const lastShownDate = new Date(lastShown);
  const daysSinceShown = (Date.now() - lastShownDate.getTime()) / (1000 * 60 * 60 * 24);

  return daysSinceShown > 3; // Show again after 3 days
}

function markPopupShown(): void {
  localStorage.setItem('reg_popup_shown', new Date().toISOString());
}

// Popup that appears after user spends time on site
export function RegistrationPopup({ isLoggedIn, onRegister, onClose }: RegistrationMotivationProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isLoggedIn) return;
    if (!shouldShowPopup()) return;

    // Show popup after 30 seconds on site
    const timer = setTimeout(() => {
      setIsVisible(true);
      markPopupShown();
    }, 30000);

    return () => clearTimeout(timer);
  }, [isLoggedIn]);

  if (!isVisible || isLoggedIn) return null;

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0,0,0,0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '24px',
        maxWidth: '440px',
        width: '100%',
        overflow: 'hidden',
        boxShadow: '0 25px 50px rgba(0,0,0,0.25)'
      }}>
        {/* Header with gradient */}
        <div style={{
          background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
          padding: '32px 24px',
          textAlign: 'center',
          position: 'relative'
        }}>
          <button
            onClick={handleClose}
            style={{
              position: 'absolute',
              top: '16px',
              right: '16px',
              background: 'rgba(255,255,255,0.2)',
              border: 'none',
              borderRadius: '50%',
              width: '32px',
              height: '32px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X style={{ width: '18px', height: '18px', color: 'white' }} />
          </button>

          <div style={{
            width: '64px',
            height: '64px',
            backgroundColor: 'rgba(255,255,255,0.2)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px'
          }}>
            <Gift style={{ width: '32px', height: '32px', color: 'white' }} />
          </div>

          <h2 style={{
            color: 'white',
            fontSize: '24px',
            fontWeight: 700,
            margin: '0 0 8px'
          }}>
            Get 10% Off Your First Booking!
          </h2>
          <p style={{
            color: 'rgba(255,255,255,0.9)',
            fontSize: '15px',
            margin: 0
          }}>
            Join our community and unlock exclusive deals
          </p>
        </div>

        {/* Benefits */}
        <div style={{ padding: '24px' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '24px' }}>
            {[
              { icon: Percent, text: '10% off your first surf camp booking', color: '#dc2626' },
              { icon: Bell, text: 'Early access to flash sales & discounts', color: '#f59e0b' },
              { icon: Heart, text: 'Save favorites and get price alerts', color: '#ec4899' },
            ].map((benefit, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: `${benefit.color}15`,
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  <benefit.icon style={{ width: '20px', height: '20px', color: benefit.color }} />
                </div>
                <span style={{ fontSize: '15px', color: '#334155' }}>{benefit.text}</span>
              </div>
            ))}
          </div>

          {/* CTA Buttons */}
          <button
            onClick={() => {
              onRegister?.();
              handleClose();
            }}
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
              marginBottom: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            Create Free Account
            <ChevronRight style={{ width: '20px', height: '20px' }} />
          </button>

          <p style={{
            textAlign: 'center',
            fontSize: '13px',
            color: '#94a3b8',
            margin: 0
          }}>
            Already have an account?{' '}
            <a href="/login" style={{ color: '#0ea5e9', textDecoration: 'none', fontWeight: 500 }}>
              Sign in
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

// Sticky banner at bottom of page
export function RegistrationBanner({ isLoggedIn, onRegister }: RegistrationMotivationProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    const dismissed = localStorage.getItem('reg_banner_dismissed');
    if (dismissed) {
      const dismissedDate = new Date(dismissed);
      const daysSinceDismissed = (Date.now() - dismissedDate.getTime()) / (1000 * 60 * 60 * 24);
      if (daysSinceDismissed < 7) {
        setIsDismissed(true);
      }
    }
  }, []);

  if (isLoggedIn || isDismissed) return null;

  const handleDismiss = () => {
    setIsDismissed(true);
    localStorage.setItem('reg_banner_dismissed', new Date().toISOString());
  };

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'linear-gradient(135deg, #1e293b, #0f172a)',
      padding: '16px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '24px',
      zIndex: 100,
      boxShadow: '0 -4px 20px rgba(0,0,0,0.15)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <Gift style={{ width: '24px', height: '24px', color: '#fbbf24' }} />
        <span style={{ color: 'white', fontSize: '15px' }}>
          <strong style={{ color: '#fbbf24' }}>10% OFF</strong> your first booking when you sign up!
        </span>
      </div>

      <button
        onClick={onRegister}
        style={{
          padding: '10px 20px',
          background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 600,
          cursor: 'pointer',
          whiteSpace: 'nowrap'
        }}
      >
        Sign Up Free
      </button>

      <button
        onClick={handleDismiss}
        style={{
          background: 'none',
          border: 'none',
          padding: '8px',
          cursor: 'pointer',
          color: '#64748b'
        }}
      >
        <X style={{ width: '20px', height: '20px' }} />
      </button>
    </div>
  );
}

// Exit intent popup
export function ExitIntentPopup({ isLoggedIn, onRegister }: RegistrationMotivationProps) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (isLoggedIn) return;

    const handleMouseLeave = (e: MouseEvent) => {
      if (e.clientY <= 0) {
        const shownToday = localStorage.getItem('exit_popup_shown');
        if (shownToday) {
          const shownDate = new Date(shownToday);
          if (new Date().toDateString() === shownDate.toDateString()) {
            return; // Already shown today
          }
        }
        setIsVisible(true);
        localStorage.setItem('exit_popup_shown', new Date().toISOString());
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    return () => document.removeEventListener('mouseleave', handleMouseLeave);
  }, [isLoggedIn]);

  if (!isVisible || isLoggedIn) return null;

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      backgroundColor: 'rgba(0,0,0,0.6)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '24px',
        maxWidth: '400px',
        width: '100%',
        padding: '32px',
        textAlign: 'center',
        position: 'relative'
      }}>
        <button
          onClick={() => setIsVisible(false)}
          style={{
            position: 'absolute',
            top: '16px',
            right: '16px',
            background: '#f1f5f9',
            border: 'none',
            borderRadius: '50%',
            width: '32px',
            height: '32px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          <X style={{ width: '18px', height: '18px', color: '#64748b' }} />
        </button>

        <div style={{
          fontSize: '48px',
          marginBottom: '16px'
        }}>
          🏄‍♂️
        </div>

        <h2 style={{
          fontSize: '22px',
          fontWeight: 700,
          color: '#0f172a',
          margin: '0 0 12px'
        }}>
          Wait! Don't miss out!
        </h2>

        <p style={{
          fontSize: '15px',
          color: '#64748b',
          margin: '0 0 24px',
          lineHeight: 1.6
        }}>
          Sign up now and get <strong style={{ color: '#dc2626' }}>10% off</strong> your dream surf camp booking. Limited time offer!
        </p>

        <button
          onClick={() => {
            onRegister?.();
            setIsVisible(false);
          }}
          style={{
            width: '100%',
            padding: '14px',
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
          Claim My 10% Discount
        </button>

        <button
          onClick={() => setIsVisible(false)}
          style={{
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          No thanks, I'll pay full price
        </button>
      </div>
    </div>
  );
}

// Inline signup card for camp detail pages
export function InlineSignupCard({ isLoggedIn, onRegister }: RegistrationMotivationProps) {
  if (isLoggedIn) return null;

  return (
    <div style={{
      background: 'linear-gradient(135deg, #fef3c7, #fde68a)',
      borderRadius: '16px',
      padding: '24px',
      marginBottom: '24px',
      border: '1px solid #fbbf24'
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
        <div style={{
          width: '48px',
          height: '48px',
          backgroundColor: '#fbbf24',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0
        }}>
          <Percent style={{ width: '24px', height: '24px', color: 'white' }} />
        </div>
        <div style={{ flex: 1 }}>
          <h3 style={{
            fontSize: '18px',
            fontWeight: 700,
            color: '#92400e',
            margin: '0 0 8px'
          }}>
            Save 10% on this camp!
          </h3>
          <p style={{
            fontSize: '14px',
            color: '#a16207',
            margin: '0 0 16px'
          }}>
            Create a free account to unlock your first-time booking discount.
          </p>
          <button
            onClick={onRegister}
            style={{
              padding: '10px 20px',
              backgroundColor: '#92400e',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Sign Up & Save
          </button>
        </div>
      </div>
    </div>
  );
}
