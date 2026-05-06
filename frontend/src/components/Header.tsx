import { Link, useLocation } from 'react-router-dom';
import { Waves, Menu, X } from 'lucide-react';
import { useState } from 'react';
import { LanguageSwitcher } from './LanguageSwitcher';
import { useLanguage } from '../contexts/LanguageContext';

export function Header() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  const { t } = useLanguage();

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { path: '/camps', label: t('nav.surfCamps') },
    { path: '/lessons', label: t('nav.surfLessons') },
    { path: '/map', label: t('nav.map') },
  ];

  return (
    <header style={{
      position: 'sticky',
      top: 0,
      zIndex: 50,
      backgroundColor: 'white',
      borderBottom: '1px solid #f3f4f6',
      boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        padding: '0 24px',
        height: '72px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        {/* Logo */}
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none'
        }}>
          <div style={{
            width: '42px',
            height: '42px',
            background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <Waves style={{ width: '24px', height: '24px', color: 'white' }} />
          </div>
          <span style={{
            fontSize: '22px',
            fontWeight: 700,
            color: '#0f172a'
          }}>
            SurfSelect
          </span>
        </Link>

        {/* Desktop Navigation */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }} className="hidden md:flex">
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              style={{
                padding: '10px 18px',
                borderRadius: '24px',
                fontSize: '15px',
                fontWeight: 500,
                textDecoration: 'none',
                transition: 'all 0.2s',
                backgroundColor: isActive(link.path) ? '#f0f9ff' : 'transparent',
                color: isActive(link.path) ? '#0284c7' : '#64748b'
              }}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        {/* Right Side - Language Switcher & Mobile Menu */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <LanguageSwitcher />

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden"
            style={{
              padding: '10px',
              borderRadius: '12px',
              border: 'none',
              background: isMenuOpen ? '#f1f5f9' : 'transparent',
              cursor: 'pointer'
            }}
          >
            {isMenuOpen ? (
              <X style={{ width: '24px', height: '24px', color: '#334155' }} />
            ) : (
              <Menu style={{ width: '24px', height: '24px', color: '#334155' }} />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {isMenuOpen && (
        <div className="md:hidden" style={{
          borderTop: '1px solid #f3f4f6',
          padding: '16px 24px',
          backgroundColor: 'white'
        }}>
          {navLinks.map(link => (
            <Link
              key={link.path}
              to={link.path}
              onClick={() => setIsMenuOpen(false)}
              style={{
                display: 'block',
                padding: '14px 16px',
                borderRadius: '12px',
                fontSize: '16px',
                fontWeight: 500,
                textDecoration: 'none',
                marginBottom: '4px',
                backgroundColor: isActive(link.path) ? '#f0f9ff' : 'transparent',
                color: isActive(link.path) ? '#0284c7' : '#334155'
              }}
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}
