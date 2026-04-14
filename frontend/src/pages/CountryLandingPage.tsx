import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CampCard } from '../components/CampCard';
import { useLanguage } from '../contexts/LanguageContext';
import { fetchAPI } from '../lib/api';
import type { SurfCamp } from '../types';

type FaqItem = { q: string; a: string };

interface LandingData {
  id: number;
  name: string;
  name_en: string;
  code: string;
  slug: string;
  image: string | null;
  description: string;
  landing_h1: string;
  landing_intro: string;
  landing_faq: FaqItem[];
  seo_title: string;
  seo_description: string;
  top_camps: SurfCamp[];
}

function setMeta(name: string, content: string) {
  let tag = document.querySelector(`meta[name="${name}"]`) as HTMLMetaElement | null;
  if (!tag) {
    tag = document.createElement('meta');
    tag.setAttribute('name', name);
    document.head.appendChild(tag);
  }
  tag.setAttribute('content', content);
}

export function CountryLandingPage() {
  const { countrySlug } = useParams<{ countrySlug: string }>();
  const { language } = useLanguage();
  const [data, setData] = useState<LandingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  useEffect(() => {
    if (!countrySlug) return;
    setLoading(true);
    setNotFound(false);
    fetchAPI(`/countries/${countrySlug}/landing/`)
      .then((d: LandingData) => setData(d))
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [countrySlug]);

  useEffect(() => {
    if (!data) return;
    const title = data.seo_title || `${data.name_en} Surf Camps`;
    document.title = title;
    if (data.seo_description) setMeta('description', data.seo_description);
  }, [data]);

  if (loading) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 40, height: 40, border: '3px solid #e2e8f0', borderTopColor: '#0ea5e9', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
      </div>
    );
  }

  if (notFound || !data) {
    return (
      <div style={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontSize: 24, fontWeight: 700 }}>{language === 'ru' ? 'Страница не найдена' : 'Page not found'}</h1>
          <Link to="/camps" style={{ color: '#0ea5e9' }}>{language === 'ru' ? 'К списку кемпов' : 'Back to camps'}</Link>
        </div>
      </div>
    );
  }

  const h1 = data.landing_h1 || `${data.name_en} Surf Camps`;

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>
      {data.image && (
        <div style={{
          width: '100%', height: 280, borderRadius: 16, overflow: 'hidden', marginBottom: 24,
          backgroundImage: `url(${data.image})`, backgroundSize: 'cover', backgroundPosition: 'center'
        }} />
      )}

      <h1 style={{ fontSize: 36, fontWeight: 700, color: '#0f172a', marginBottom: 12 }}>{h1}</h1>
      {data.landing_intro && (
        <p style={{ fontSize: 17, color: '#475569', lineHeight: 1.6, marginBottom: 32, whiteSpace: 'pre-wrap' }}>
          {data.landing_intro}
        </p>
      )}

      {data.top_camps.length > 0 && (
        <section style={{ marginBottom: 48 }}>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>
            {language === 'ru' ? 'Лучшие кемпы' : 'Top surf camps'}
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 20 }}>
            {data.top_camps.map(c => <CampCard key={c.id} camp={c} />)}
          </div>
          <div style={{ textAlign: 'center', marginTop: 24 }}>
            <Link
              to={`/camps?country=${data.code}`}
              style={{ display: 'inline-block', padding: '12px 24px', background: 'linear-gradient(135deg, #0ea5e9, #0284c7)', color: 'white', borderRadius: 10, textDecoration: 'none', fontWeight: 600 }}
            >
              {language === 'ru' ? 'Смотреть все кемпы' : 'View all camps'}
            </Link>
          </div>
        </section>
      )}

      {data.landing_faq && data.landing_faq.length > 0 && (
        <section style={{ marginBottom: 48 }}>
          <h2 style={{ fontSize: 24, fontWeight: 700, color: '#0f172a', marginBottom: 16 }}>FAQ</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {data.landing_faq.map((item, i) => (
              <div key={i} style={{ border: '1px solid #e2e8f0', borderRadius: 10, overflow: 'hidden' }}>
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  style={{ width: '100%', textAlign: 'left', padding: 16, background: 'white', border: 'none', fontSize: 16, fontWeight: 600, color: '#0f172a', cursor: 'pointer', display: 'flex', justifyContent: 'space-between' }}
                >
                  <span>{item.q}</span>
                  <span>{openFaq === i ? '−' : '+'}</span>
                </button>
                {openFaq === i && (
                  <div style={{ padding: '0 16px 16px', color: '#475569', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
                    {item.a}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
