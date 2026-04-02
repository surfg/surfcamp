import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

export type Language = 'en' | 'ru';

interface Translations {
  [key: string]: {
    en: string;
    ru: string;
  };
}

const translations: Translations = {
  // Navigation
  'nav.surfCamps': { en: 'Surf Camps', ru: 'Серф-кемпы' },
  'nav.surfSpots': { en: 'Surf Spots', ru: 'Серф-споты' },
  'nav.map': { en: 'Map', ru: 'Карта' },

  // Hero
  'hero.title1': { en: 'Find Your Perfect', ru: 'Найди свой идеальный' },
  'hero.title2': { en: 'Surf Camp', ru: 'серф-кемп' },
  'hero.subtitle': { en: 'Compare and book surf camps worldwide. From Bali to Portugal, find your next adventure.', ru: 'Сравнивайте и бронируйте серф-кемпы по всему миру. От Бали до Португалии — найдите своё приключение.' },
  'hero.searchPlaceholder': { en: 'Where do you want to surf?', ru: 'Куда хотите поехать серфить?' },
  'hero.search': { en: 'Search', ru: 'Поиск' },

  // Stats
  'stats.surfCamps': { en: 'Surf Camps', ru: 'Серф-кемпов' },
  'stats.countries': { en: 'Countries', ru: 'Стран' },
  'stats.avgRating': { en: 'Avg Rating', ru: 'Ср. рейтинг' },

  // Featured
  'featured.title': { en: 'Featured Surf Camps', ru: 'Рекомендуемые серф-кемпы' },
  'featured.subtitle': { en: 'Hand-picked camps with exceptional experiences', ru: 'Лучшие кемпы с уникальным опытом' },
  'featured.viewAll': { en: 'View all', ru: 'Смотреть все' },

  // CTA
  'cta.title': { en: 'Ready for your next surf adventure?', ru: 'Готовы к новому серф-приключению?' },
  'cta.subtitle': { en: 'Join thousands of surfers who found their perfect camp', ru: 'Присоединяйтесь к тысячам серферов, нашедших свой идеальный кемп' },
  'cta.button': { en: 'Explore Camps', ru: 'Смотреть кемпы' },

  // Footer
  'footer.rights': { en: 'All rights reserved.', ru: 'Все права защищены.' },

  // Search
  'search.destination': { en: 'Destination', ru: 'Направление' },
  'search.whereTo': { en: 'Where are you going?', ru: 'Куда вы едете?' },
  'search.checkIn': { en: 'Check in', ru: 'Заезд' },
  'search.checkOut': { en: 'Check out', ru: 'Выезд' },
  'search.guests': { en: 'Guests', ru: 'Гости' },
  'search.guest': { en: 'guest', ru: 'гость' },
  'search.searchDest': { en: 'Search destinations...', ru: 'Поиск направлений...' },
  'search.showOnMap': { en: 'Show on map', ru: 'Показать на карте' },
  'search.perNight': { en: 'per night', ru: 'за ночь' },
  'search.camps': { en: 'camps', ru: 'кемпов' },
  'search.country': { en: 'Country', ru: 'Страна' },
  'search.region': { en: 'Region', ru: 'Регион' },
  'search.camp': { en: 'Camp', ru: 'Кемп' },

  // Filters
  'filters.title': { en: 'Filters', ru: 'Фильтры' },
  'filters.country': { en: 'Country', ru: 'Страна' },
  'filters.allCountries': { en: 'All countries', ru: 'Все страны' },
  'filters.priceRange': { en: 'Price Range', ru: 'Цена' },
  'filters.pricePerNight': { en: 'per night', ru: 'за ночь' },
  'filters.skillLevel': { en: 'Skill Level', ru: 'Уровень серфинга' },
  'filters.beginner': { en: 'Beginner', ru: 'Начинающий' },
  'filters.intermediate': { en: 'Intermediate', ru: 'Средний' },
  'filters.advanced': { en: 'Advanced', ru: 'Продвинутый' },
  'filters.boardTypes': { en: 'Board Types', ru: 'Типы досок' },
  'filters.softTops': { en: 'Soft tops', ru: 'Софттопы' },
  'filters.longboards': { en: 'Longboards', ru: 'Лонгборды' },
  'filters.midLengths': { en: 'Mid lengths', ru: 'Миды' },
  'filters.shortboards': { en: 'Shortboards', ru: 'Шортборды' },
  'filters.amenities': { en: 'Amenities', ru: 'Удобства' },
  'filters.pool': { en: 'Pool', ru: 'Бассейн' },
  'filters.yoga': { en: 'Yoga', ru: 'Йога' },
  'filters.parties': { en: 'Parties', ru: 'Вечеринки' },
  'filters.boardRental': { en: 'Board Rental', ru: 'Аренда досок' },
  'filters.bedBreakfast': { en: 'Bed & Breakfast only', ru: 'Только B&B (без уроков)' },
  'filters.clearAll': { en: 'Clear all', ru: 'Сбросить всё' },
  'filters.apply': { en: 'Apply filters', ru: 'Применить' },

  // Camps Page
  'camps.title': { en: 'Surf Camps', ru: 'Серф-кемпы' },
  'camps.places': { en: 'places to stay', ru: 'мест для отдыха' },
  'camps.noResults': { en: 'No camps found', ru: 'Кемпы не найдены' },
  'camps.adjustFilters': { en: 'Try adjusting your filters', ru: 'Попробуйте изменить фильтры' },
  'camps.error': { en: 'Something went wrong', ru: 'Что-то пошло не так' },
  'camps.tryAgain': { en: 'Try Again', ru: 'Попробовать снова' },

  // Camp Detail
  'camp.backToCamps': { en: 'Back to camps', ru: 'К списку кемпов' },
  'camp.guestFavourite': { en: 'Guest favourite', ru: 'Любимец гостей' },
  'camp.reviews': { en: 'reviews', ru: 'отзывов' },
  'camp.overview': { en: 'Overview', ru: 'Обзор' },
  'camp.instructors': { en: 'Instructors', ru: 'Инструкторы' },
  'camp.reviewsTab': { en: 'Reviews', ru: 'Отзывы' },
  'camp.surfSpots': { en: 'Surf Spots', ru: 'Серф-споты' },
  'camp.history': { en: 'Our Story', ru: 'Наша история' },
  'camp.about': { en: 'About', ru: 'О кемпе' },
  'camp.whatsIncluded': { en: "What's included", ru: 'Что включено' },
  'camp.included': { en: 'Included', ru: 'Включено' },
  'camp.activities': { en: 'Activities & Excursions', ru: 'Активности и экскурсии' },
  'camp.lessonsWithoutStay': { en: 'Lessons without accommodation', ru: 'Уроки без проживания' },
  'camp.pricePerLesson': { en: 'per lesson', ru: 'за урок' },
  'camp.noInstructors': { en: 'No instructors listed', ru: 'Инструкторы не указаны' },
  'camp.noReviews': { en: 'No reviews yet', ru: 'Отзывов пока нет' },
  'camp.yearsExp': { en: 'years experience', ru: 'лет опыта' },
  'camp.languages': { en: 'Languages', ru: 'Языки' },
  'camp.headCoach': { en: 'Head Coach', ru: 'Главный тренер' },
  'camp.bookNow': { en: 'Book Now', ru: 'Забронировать' },
  'camp.noCharge': { en: "You won't be charged yet", ru: 'Оплата не будет списана сейчас' },
  'camp.contact': { en: 'Contact', ru: 'Контакты' },
  'camp.website': { en: 'Website', ru: 'Сайт' },
  'camp.bbOnly': { en: 'B&B only', ru: 'Только B&B' },
  'camp.perNight': { en: 'night', ru: 'ночь' },

  // Booking
  'booking.title': { en: 'Book your stay at', ru: 'Забронируйте проживание в' },
  'booking.backToCamp': { en: 'Back to camp', ru: 'Назад к кемпу' },
  'booking.step1': { en: 'Dates & Options', ru: 'Даты и опции' },
  'booking.step2': { en: 'Guest Info', ru: 'Данные гостей' },
  'booking.step3': { en: 'Confirmation', ru: 'Подтверждение' },
  'booking.selectDates': { en: 'Select your dates', ru: 'Выберите даты' },
  'booking.checkIn': { en: 'Check-in', ru: 'Заезд' },
  'booking.checkOut': { en: 'Check-out', ru: 'Выезд' },
  'booking.night': { en: 'night', ru: 'ночь' },
  'booking.nights': { en: 'nights', ru: 'ночей' },
  'booking.guests': { en: 'Guests', ru: 'Гости' },
  'booking.adults': { en: 'Adults', ru: 'Взрослые' },
  'booking.age18': { en: 'Age 18+', ru: 'От 18 лет' },
  'booking.children': { en: 'Children', ru: 'Дети' },
  'booking.age017': { en: 'Age 0-17', ru: '0-17 лет' },
  'booking.enhance': { en: 'Enhance your stay', ru: 'Дополнительные опции' },
  'booking.breakfast': { en: 'Breakfast included', ru: 'Завтрак включён' },
  'booking.breakfastDesc': { en: 'Start your day with a delicious breakfast buffet', ru: 'Начните день с вкусного завтрака' },
  'booking.perPersonNight': { en: 'per person/night', ru: 'чел/ночь' },
  'booking.surfLessons': { en: 'Surf lessons', ru: 'Уроки серфинга' },
  'booking.lessonsDesc': { en: 'Professional instructors for all levels', ru: 'Профессиональные инструкторы для всех уровней' },
  'booking.perLesson': { en: 'per lesson', ru: 'за урок' },
  'booking.numLessons': { en: 'Number of lessons', ru: 'Количество уроков' },
  'booking.boardRental': { en: 'Board rental', ru: 'Аренда доски' },
  'booking.boardDesc': { en: 'Quality boards for all skill levels', ru: 'Качественные доски для всех уровней' },
  'booking.perDay': { en: 'per day', ru: 'в день' },
  'booking.additionalInfo': { en: 'Additional information', ru: 'Дополнительная информация' },
  'booking.arrivalTime': { en: 'Estimated arrival time', ru: 'Ожидаемое время прибытия' },
  'booking.specialRequests': { en: 'Special requests (optional)', ru: 'Особые пожелания (необязательно)' },
  'booking.requestsPlaceholder': { en: 'Any special requirements or requests?', ru: 'Есть ли особые пожелания?' },
  'booking.priceSummary': { en: 'Price summary', ru: 'Итого к оплате' },
  'booking.selectDatesToSee': { en: 'Select dates to see pricing', ru: 'Выберите даты для расчёта' },
  'booking.serviceFee': { en: 'Service fee', ru: 'Сервисный сбор' },
  'booking.total': { en: 'Total', ru: 'Итого' },
  'booking.continue': { en: 'Continue to guest details', ru: 'Перейти к данным гостей' },
  'booking.freeCancellation': { en: 'Free cancellation before 48 hours', ru: 'Бесплатная отмена за 48 часов' },
  'booking.processing': { en: 'Processing...', ru: 'Обработка...' },

  // Guest Info
  'guest.title': { en: 'Guest Information', ru: 'Информация о гостях' },
  'guest.primary': { en: 'Primary Guest', ru: 'Основной гость' },
  'guest.additional': { en: 'Additional Guest', ru: 'Дополнительный гость' },
  'guest.firstName': { en: 'First name', ru: 'Имя' },
  'guest.lastName': { en: 'Last name', ru: 'Фамилия' },
  'guest.email': { en: 'Email', ru: 'Email' },
  'guest.phone': { en: 'Phone', ru: 'Телефон' },
  'guest.country': { en: 'Country', ru: 'Страна' },
  'guest.city': { en: 'City', ru: 'Город' },
  'guest.surfLevel': { en: 'Surf Level', ru: 'Уровень серфинга' },
  'guest.emergency': { en: 'Emergency Contact', ru: 'Контакт для экстренной связи' },
  'guest.emergencyName': { en: 'Contact name', ru: 'Имя контакта' },
  'guest.emergencyPhone': { en: 'Contact phone', ru: 'Телефон контакта' },
  'guest.continueCheckout': { en: 'Submit booking request', ru: 'Оформить бронирование' },

  // Payment
  'payment.title': { en: 'Payment', ru: 'Оплата' },
  'payment.method': { en: 'Payment method', ru: 'Способ оплаты' },
  'payment.card': { en: 'Credit/Debit Card', ru: 'Банковская карта' },
  'payment.paypal': { en: 'PayPal', ru: 'PayPal' },
  'payment.bankTransfer': { en: 'Bank Transfer', ru: 'Банковский перевод' },
  'payment.cardNumber': { en: 'Card number', ru: 'Номер карты' },
  'payment.expiry': { en: 'Expiry date', ru: 'Срок действия' },
  'payment.cvv': { en: 'CVV', ru: 'CVV' },
  'payment.cardHolder': { en: 'Cardholder name', ru: 'Имя владельца' },
  'payment.payNow': { en: 'Pay now', ru: 'Оплатить' },
  'payment.secure': { en: 'Secure payment', ru: 'Безопасная оплата' },

  // Confirmation
  'confirmation.title': { en: 'Booking Request Submitted!', ru: 'Заявка на бронирование отправлена!' },
  'confirmation.thankYou': { en: 'Thank you for your booking', ru: 'Спасибо за бронирование' },
  'confirmation.managerContact': { en: 'Our manager will contact you shortly to confirm the details and arrange payment.', ru: 'Наш менеджер свяжется с вами в ближайшее время для подтверждения деталей и оформления оплаты.' },
  'confirmation.number': { en: 'Booking number', ru: 'Номер бронирования' },
  'confirmation.details': { en: 'Booking Details', ru: 'Детали бронирования' },
  'confirmation.dates': { en: 'Dates', ru: 'Даты' },
  'confirmation.download': { en: 'Download confirmation', ru: 'Скачать подтверждение' },
  'confirmation.backHome': { en: 'Back to home', ru: 'На главную' },

  // Map
  'map.title': { en: 'Surf Map', ru: 'Карта серфинга' },
  'map.camps': { en: 'Camps', ru: 'Кемпы' },
  'map.spots': { en: 'Spots', ru: 'Споты' },
  'map.viewDetails': { en: 'View Details', ru: 'Подробнее' },
  'map.viewSpot': { en: 'View Spot', ru: 'Посмотреть спот' },

  // Pagination
  'pagination.showing': { en: 'Showing', ru: 'Показано' },
  'pagination.of': { en: 'of', ru: 'из' },
  'pagination.prev': { en: 'Previous', ru: 'Назад' },
  'pagination.next': { en: 'Next', ru: 'Далее' },

  // Spots
  'spots.title': { en: 'Surf Spots', ru: 'Серф-споты' },
  'spots.subtitle': { en: 'Discover the best waves around the world', ru: 'Откройте лучшие волны по всему миру' },
  'spots.places': { en: 'spots', ru: 'спотов' },

  // Lessons
  'nav.surfLessons': { en: 'Surf Lessons', ru: 'Уроки серфинга' },
  'lessons.title': { en: 'Surf Lessons', ru: 'Уроки серфинга' },
  'lessons.subtitle': { en: 'Learn to surf with professional instructors', ru: 'Научитесь серфингу с профессиональными инструкторами' },
  'lessons.places': { en: 'lessons available', ru: 'доступных уроков' },
  'lessons.noResults': { en: 'No lessons found', ru: 'Уроки не найдены' },
  'lessons.adjustFilters': { en: 'Try adjusting your filters', ru: 'Попробуйте изменить фильтры' },
  'lessons.duration': { en: 'Duration', ru: 'Длительность' },
  'lessons.groupSize': { en: 'Group size', ru: 'Размер группы' },
  'lessons.level': { en: 'Level', ru: 'Уровень' },
  'lessons.price': { en: 'Price', ru: 'Цена' },
  'lessons.perLesson': { en: 'per lesson', ru: 'за урок' },
  'lessons.perPackage': { en: 'per package', ru: 'за пакет' },
  'lessons.hours': { en: 'hours', ru: 'часов' },
  'lessons.minutes': { en: 'minutes', ru: 'минут' },
  'lessons.people': { en: 'people', ru: 'человек' },
  'lessons.private': { en: 'Private', ru: 'Индивидуальный' },
  'lessons.group': { en: 'Group', ru: 'Групповой' },
  'lessons.includesEquipment': { en: 'Equipment included', ru: 'Оборудование включено' },
  'lessons.includesTransport': { en: 'Transport included', ru: 'Трансфер включён' },
  'lessons.bookLesson': { en: 'Book Lesson', ru: 'Забронировать урок' },
  'lesson.backToLessons': { en: 'Back to lessons', ru: 'К списку уроков' },

  // Common
  'common.loading': { en: 'Loading...', ru: 'Загрузка...' },
  'common.error': { en: 'Error', ru: 'Ошибка' },
  'common.notFound': { en: 'Not found', ru: 'Не найдено' },
  'common.save': { en: 'Save', ru: 'Сохранить' },
  'common.cancel': { en: 'Cancel', ru: 'Отмена' },
  'common.close': { en: 'Close', ru: 'Закрыть' },
  'common.viewAll': { en: 'View all', ru: 'Смотреть все' },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
  getLocalized: (ru: string | undefined, en: string | undefined) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<Language>(() => {
    const saved = localStorage.getItem('surfcamp_language');
    return (saved as Language) || 'en';
  });

  useEffect(() => {
    localStorage.setItem('surfcamp_language', language);
    document.documentElement.lang = language;
  }, [language]);

  const t = (key: string): string => {
    const translation = translations[key];
    if (!translation) {
      console.warn(`Missing translation for key: ${key}`);
      return key;
    }
    return translation[language] || translation.en || key;
  };

  const getLocalized = (ru: string | undefined, en: string | undefined): string => {
    if (language === 'ru' && ru) return ru;
    return en || ru || '';
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, getLocalized }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
