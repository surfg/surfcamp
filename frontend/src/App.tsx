import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Header } from './components/Header';
import { HomePage } from './pages/HomePage';
import { CampsPage } from './pages/CampsPage';
import { CampDetailPage } from './pages/CampDetailPage';
import { SpotsPage } from './pages/SpotsPage';
import { SpotDetailPage } from './pages/SpotDetailPage';
import { LessonsPage } from './pages/LessonsPage';
import { LessonDetailPage } from './pages/LessonDetailPage';
import { MapPage } from './pages/MapPage';
import { BookingPage } from './pages/BookingPage';
import { GuestInfoPage } from './pages/GuestInfoPage';
import { PaymentPage } from './pages/PaymentPage';
import { ConfirmationPage } from './pages/ConfirmationPage';
import { LanguageProvider } from './contexts/LanguageContext';
import './index.css';

function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gray-50">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/camps" element={<CampsPage />} />
              <Route path="/camps/:slug" element={<CampDetailPage />} />
              <Route path="/camps/:slug/book" element={<BookingPage />} />
              <Route path="/spots" element={<SpotsPage />} />
              <Route path="/spots/:slug" element={<SpotDetailPage />} />
              <Route path="/lessons" element={<LessonsPage />} />
              <Route path="/lessons/:slug" element={<LessonDetailPage />} />
              <Route path="/map" element={<MapPage />} />
              <Route path="/booking/:bookingNumber/guests" element={<GuestInfoPage />} />
              <Route path="/booking/:bookingNumber/payment" element={<PaymentPage />} />
              <Route path="/booking/:bookingNumber/confirmation" element={<ConfirmationPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
