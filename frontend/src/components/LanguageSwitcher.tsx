import { useLanguage } from '../contexts/LanguageContext';

export function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage();

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      backgroundColor: '#f1f5f9',
      borderRadius: '20px',
      padding: '4px',
      gap: '2px',
    }}>
      <button
        onClick={() => setLanguage('en')}
        style={{
          padding: '6px 12px',
          borderRadius: '16px',
          border: 'none',
          backgroundColor: language === 'en' ? 'white' : 'transparent',
          color: language === 'en' ? '#0f172a' : '#64748b',
          fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
          boxShadow: language === 'en' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
          transition: 'all 0.2s',
        }}
      >
        EN
      </button>
      <button
        onClick={() => setLanguage('ru')}
        style={{
          padding: '6px 12px',
          borderRadius: '16px',
          border: 'none',
          backgroundColor: language === 'ru' ? 'white' : 'transparent',
          color: language === 'ru' ? '#0f172a' : '#64748b',
          fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
          boxShadow: language === 'ru' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none',
          transition: 'all 0.2s',
        }}
      >
        RU
      </button>
    </div>
  );
}
