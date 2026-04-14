import type {
  SurfCamp, SurfCampDetail, SurfSpot, SurfSpotDetail, Country, FilterParams,
  SearchResult, FilterOptions, Booking, BookingCreateData, PaymentData, Guest,
  SurfLesson, SurfLessonDetail, LessonFilterOptions
} from '../types';

const API_BASE = '/api';

export async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.error || `API Error: ${response.status}`);
  }
  return response.json();
}

// Camps
export async function getCamps(params?: FilterParams): Promise<{ results: SurfCamp[]; count: number }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        searchParams.append(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  return fetchAPI(`/camps/${query ? `?${query}` : ''}`);
}

export async function getCamp(slug: string): Promise<SurfCampDetail> {
  return fetchAPI(`/camps/${slug}/`);
}

export async function getFeaturedCamps(): Promise<SurfCamp[]> {
  return fetchAPI('/camps/featured/');
}

export async function getCampsMapData(params?: FilterParams): Promise<SurfCamp[]> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        searchParams.append(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  return fetchAPI(`/camps/map_data/${query ? `?${query}` : ''}`);
}

// Spots
export async function getSpots(params?: FilterParams): Promise<{ results: SurfSpot[]; count: number }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        searchParams.append(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  return fetchAPI(`/spots/${query ? `?${query}` : ''}`);
}

export async function getSpot(slug: string): Promise<SurfSpotDetail> {
  return fetchAPI(`/spots/${slug}/`);
}

export async function getSpotsMapData(): Promise<SurfSpot[]> {
  return fetchAPI('/spots/map_data/');
}

// Countries & Regions
export async function getCountries(): Promise<Country[]> {
  return fetchAPI('/countries/');
}

export async function getRegions(countryCode?: string): Promise<{ id: number; name: string; camps_count: number }[]> {
  const query = countryCode ? `?country=${countryCode}` : '';
  return fetchAPI(`/regions/${query}`);
}

// Search & Filters
export async function searchAutocomplete(query: string, lang: string = 'en'): Promise<{ results: SearchResult[] }> {
  if (query.length < 2) return { results: [] };
  return fetchAPI(`/search/?q=${encodeURIComponent(query)}&lang=${lang}`);
}

export async function getFilterOptions(): Promise<FilterOptions> {
  return fetchAPI('/filters/');
}

// Bookings
export async function createBooking(data: BookingCreateData): Promise<Booking> {
  return fetchAPI('/bookings/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function getBooking(bookingNumber: string): Promise<Booking> {
  return fetchAPI(`/bookings/${bookingNumber}/`);
}

export async function updateBookingGuests(bookingNumber: string, guests: Omit<Guest, 'id'>[]): Promise<Booking> {
  return fetchAPI(`/bookings/${bookingNumber}/update_guests/`, {
    method: 'PUT',
    body: JSON.stringify({ guests }),
  });
}

export async function processPayment(bookingNumber: string, paymentData: PaymentData): Promise<{
  success: boolean;
  payment_id: string;
  transaction_id: string;
  booking: Booking;
}> {
  return fetchAPI(`/bookings/${bookingNumber}/process_payment/`, {
    method: 'POST',
    body: JSON.stringify(paymentData),
  });
}

export async function cancelBooking(bookingNumber: string, reason?: string): Promise<Booking> {
  return fetchAPI(`/bookings/${bookingNumber}/cancel/`, {
    method: 'POST',
    body: JSON.stringify({ reason }),
  });
}

export async function getBookingPriceBreakdown(bookingNumber: string): Promise<{
  nights: number;
  price_per_night: number;
  accommodation_total: number;
  breakfast_total: number;
  lessons_total: number;
  board_rental_total: number;
  subtotal: number;
  service_fee: number;
  total_price: number;
  currency: string;
}> {
  return fetchAPI(`/bookings/${bookingNumber}/price_breakdown/`);
}

// Lessons
export async function getLessons(params?: FilterParams): Promise<{ results: SurfLesson[]; count: number }> {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== '' && value !== null) {
        searchParams.append(key, String(value));
      }
    });
  }
  const query = searchParams.toString();
  return fetchAPI(`/lessons/${query ? `?${query}` : ''}`);
}

export async function getLesson(slug: string): Promise<SurfLessonDetail> {
  return fetchAPI(`/lessons/${slug}/`);
}

export async function getFeaturedLessons(): Promise<SurfLesson[]> {
  return fetchAPI('/lessons/featured/');
}

export async function getLessonFilters(): Promise<LessonFilterOptions> {
  return fetchAPI('/lessons/filters/');
}

// Calculate price preview (client-side)
export function calculatePricePreview(
  camp: SurfCampDetail,
  nights: number,
  adults: number,
  children: number,
  options: {
    includeBreakfast?: boolean;
    includeLessons?: boolean;
    lessonsCount?: number;
    includeBoardRental?: boolean;
  }
): {
  accommodationTotal: number;
  breakfastTotal: number;
  lessonsTotal: number;
  boardRentalTotal: number;
  subtotal: number;
  serviceFee: number;
  total: number;
} {
  const accommodationTotal = camp.price_per_night * nights;

  let breakfastTotal = 0;
  if (options.includeBreakfast && camp.has_bed_breakfast && camp.bed_breakfast_price) {
    breakfastTotal = camp.bed_breakfast_price * nights * (adults + children);
  }

  let lessonsTotal = 0;
  if (options.includeLessons && camp.price_per_lesson && options.lessonsCount) {
    lessonsTotal = camp.price_per_lesson * options.lessonsCount;
  }

  let boardRentalTotal = 0;
  if (options.includeBoardRental && camp.board_rental_available && camp.board_rental_price) {
    boardRentalTotal = camp.board_rental_price * nights;
  }

  const subtotal = accommodationTotal + breakfastTotal + lessonsTotal + boardRentalTotal;
  const serviceFee = Math.round(subtotal * 0.1 * 100) / 100; // 10% service fee
  const total = subtotal + serviceFee;

  return {
    accommodationTotal,
    breakfastTotal,
    lessonsTotal,
    boardRentalTotal,
    subtotal,
    serviceFee,
    total,
  };
}
