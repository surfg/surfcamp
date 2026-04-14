export interface Country {
  id: number;
  name: string;
  name_en: string;
  code: string;
  image: string | null;
  description: string;
  camps_count: number;
}

export interface Region {
  id: number;
  name: string;
  name_en: string;
  country: number;
  country_name: string;
  latitude: number | null;
  longitude: number | null;
  camps_count: number;
}

export interface BoardType {
  id: number;
  name: string;
  name_en: string;
  icon: string;
  description: string;
}

export interface Amenity {
  id: number;
  name: string;
  name_en: string;
  icon: string;
  category: string;
}

export interface CampImage {
  id: number;
  image: string;
  alt_text: string;
  is_main: boolean;
  order: number;
}

export interface Instructor {
  id: number;
  name: string;
  photo: string | null;
  bio: string;
  experience_years: number;
  certifications: string;
  languages: string;
  is_head_coach: boolean;
}

export interface Activity {
  id: number;
  name: string;
  name_en: string;
  description: string;
  price: number | null;
  is_included: boolean;
  image: string | null;
}

export interface Review {
  id: number;
  author_name: string;
  author_country: string;
  author_photo: string | null;
  rating: number;
  title: string;
  text: string;
  surf_level: string;
  visit_date: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface SurfCamp {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  region_name: string;
  country_name: string;
  country_code: string;
  latitude: number | null;
  longitude: number | null;
  price_per_night: number;
  has_bed_breakfast: boolean;
  bed_breakfast_price: number | null;
  skill_levels: string[];
  teaching_languages: string[];
  rating: number;
  reviews_count: number;
  has_pool: boolean;
  has_yoga: boolean;
  is_featured: boolean;
  main_image: string | null;
  // Discount fields
  discount_percent: number | null;
  discount_ends_at: string | null;
  discount_description: string | null;
}

export interface SurfCampDetail extends SurfCamp {
  region: Region;
  country: Country;
  description: string;
  history: string;
  address: string;
  price_per_lesson: number | null;
  board_types: BoardType[];
  board_rental_available: boolean;
  board_rental_price: number | null;
  amenities: Amenity[];
  has_restaurant: boolean;
  has_parties: boolean;
  website: string;
  email: string;
  phone: string;
  instagram: string;
  whatsapp: string;
  images: CampImage[];
  instructors: Instructor[];
  activities: Activity[];
  reviews: Review[];
  spots: SurfSpot[];
}

export interface SurfSpot {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  region_name: string;
  country_name: string;
  latitude: number;
  longitude: number;
  wave_type: string;
  wave_direction: string;
  skill_levels: string[];
  crowd_level: string;
  rating: number;
  main_image: string | null;
}

export interface SpotImage {
  id: number;
  image: string;
  alt_text: string;
  is_main: boolean;
  order: number;
}

export interface SurfSpotDetail extends SurfSpot {
  description: string;
  wave_height_min: number | null;
  wave_height_max: number | null;
  best_tide: string;
  best_swell: string;
  best_wind: string;
  best_season: string;
  hazards: string;
  has_rocks: boolean;
  has_reef: boolean;
  has_currents: boolean;
  has_sharks: boolean;
  has_parking: boolean;
  has_showers: boolean;
  has_rentals: boolean;
  has_cafe: boolean;
  has_lifeguard: boolean;
  images: SpotImage[];
  nearby_camps: SurfCamp[];
}

export interface FilterParams {
  country?: string;
  region?: number;
  min_price?: number;
  max_price?: number;
  skill_level?: string;
  language?: string;
  has_pool?: boolean;
  has_yoga?: boolean;
  has_parties?: boolean;
  has_bed_breakfast?: boolean;
  board_rental?: boolean;
  min_rating?: number;
  search?: string;
  check_in?: string;
  check_out?: string;
  guests?: number;
  page?: number;
}

// Search autocomplete types
export interface SearchResultCountry {
  type: 'country';
  id: number;
  name: string;
  code: string;
  camps_count: number;
  image: string | null;
}

export interface SearchResultRegion {
  type: 'region';
  id: number;
  name: string;
  country_name: string;
  country_code: string;
  camps_count: number;
}

export interface SearchResultCamp {
  type: 'camp';
  id: number;
  slug: string;
  name: string;
  region_name: string;
  country_name: string;
  price_per_night: number;
  rating: number;
  image: string | null;
}

export type SearchResult = SearchResultCountry | SearchResultRegion | SearchResultCamp;

// Filter options
export interface FilterOptions {
  countries: Array<{
    id: number;
    name: string;
    name_en: string;
    code: string;
    camps_count: number;
  }>;
  regions: Array<{
    id: number;
    name: string;
    name_en: string;
    country__code: string;
    country__name_en: string;
    camps_count: number;
  }>;
  price_range: {
    min: number;
    max: number;
    avg: number;
  };
  skill_levels: Array<{
    value: string;
    label: string;
  }>;
  languages: Array<{
    value: string;
    label: string;
    label_ru: string;
  }>;
  amenities: Array<{
    id: number;
    name: string;
    name_en: string;
    icon: string;
    category: string;
  }>;
  board_types: Array<{
    id: number;
    name: string;
    name_en: string;
    icon: string;
  }>;
  features: Array<{
    key: string;
    label: string;
  }>;
}

// Booking types
export interface Guest {
  id?: number;
  is_primary: boolean;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  country: string;
  city: string;
  surf_level: 'beginner' | 'intermediate' | 'advanced';
  emergency_name: string;
  emergency_phone: string;
}

export interface Payment {
  id: string;
  amount: number;
  currency: string;
  method: 'card' | 'paypal' | 'bank_transfer';
  status: string;
  card_last_four: string;
  card_brand: string;
  created_at: string;
  completed_at: string | null;
}

export interface Booking {
  id: string;
  booking_number: string;
  camp: number;
  camp_name: string;
  camp_slug: string;
  camp_image: string | null;
  camp_address: string;
  check_in: string;
  check_out: string;
  nights: number;
  adults: number;
  children: number;
  include_breakfast: boolean;
  include_lessons: boolean;
  lessons_count: number;
  include_board_rental: boolean;
  price_per_night: number;
  breakfast_total: number;
  lessons_total: number;
  board_rental_total: number;
  subtotal: number;
  service_fee: number;
  total_price: number;
  currency: string;
  status: 'pending' | 'confirmed' | 'paid' | 'cancelled' | 'completed';
  payment_status: 'pending' | 'processing' | 'paid' | 'failed' | 'refunded';
  special_requests: string;
  arrival_time: string | null;
  created_at: string;
  guests: Guest[];
  payments: Payment[];
}

export interface BookingCreateData {
  camp: number;
  check_in: string;
  check_out: string;
  adults: number;
  children: number;
  include_breakfast?: boolean;
  include_lessons?: boolean;
  lessons_count?: number;
  include_board_rental?: boolean;
  special_requests?: string;
  arrival_time?: string;
}

export interface PaymentData {
  method: 'card' | 'paypal' | 'bank_transfer';
  card_number?: string;
  card_expiry?: string;
  card_cvc?: string;
  card_holder?: string;
}

export interface PriceBreakdown {
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
}

// Surf Lessons
export interface LessonProvider {
  id: number;
  name: string;
  slug: string;
  description: string;
  description_ru: string;
  region_name: string;
  country_name: string;
  country_code: string;
  address: string;
  latitude: number | null;
  longitude: number | null;
  phone: string;
  email: string;
  website: string;
  instagram: string;
  whatsapp: string;
  logo: string | null;
  main_image: string | null;
  rating: number;
  reviews_count: number;
  is_featured: boolean;
}

export interface SurfLesson {
  id: number;
  name: string;
  name_ru: string;
  slug: string;
  short_description: string;
  short_description_ru: string;
  provider_name: string;
  provider_slug: string;
  region_name: string;
  country_name: string;
  country_code: string;
  lesson_type: 'private' | 'group' | 'semi_private';
  skill_level: 'beginner' | 'intermediate' | 'advanced' | 'all';
  duration_minutes: number;
  duration_hours: number;
  max_participants: number;
  min_age: number;
  price: number;
  currency: string;
  price_per_person: boolean;
  is_package: boolean;
  lessons_in_package: number;
  includes_equipment: boolean;
  includes_transport: boolean;
  main_image: string | null;
  rating: number;
  reviews_count: number;
  is_featured: boolean;
}

export interface LessonImage {
  id: number;
  image: string;
  alt_text: string;
  is_main: boolean;
  order: number;
}

export interface LessonReview {
  id: number;
  author_name: string;
  author_country: string;
  author_photo: string | null;
  rating: number;
  title: string;
  text: string;
  surf_level: string;
  visit_date: string | null;
  is_verified: boolean;
  created_at: string;
}

export interface SurfLessonDetail extends Omit<SurfLesson, 'provider_name' | 'provider_slug'> {
  description: string;
  description_ru: string;
  provider: LessonProvider;
  includes_wetsuit: boolean;
  includes_photos: boolean;
  includes_video: boolean;
  includes_theory: boolean;
  includes_insurance: boolean;
  package_discount_percent: number;
  images: LessonImage[];
  reviews: LessonReview[];
  bookings_count: number;
  created_at: string;
}

export interface LessonFilterOptions {
  countries: Array<{
    id: number;
    name: string;
    name_en: string;
    code: string;
    lessons_count: number;
  }>;
  lesson_types: Array<{
    value: string;
    label: string;
    label_ru: string;
  }>;
  skill_levels: Array<{
    value: string;
    label: string;
    label_ru: string;
  }>;
  price_range: {
    min: number;
    max: number;
    avg: number;
  };
  durations: Array<{
    value: number;
    label: string;
    label_ru: string;
  }>;
}

// Booking state for multi-step flow
export interface BookingState {
  step: 'dates' | 'options' | 'guests' | 'payment' | 'confirmation';
  camp: SurfCampDetail | null;
  checkIn: Date | null;
  checkOut: Date | null;
  adults: number;
  children: number;
  includeBreakfast: boolean;
  includeLessons: boolean;
  lessonsCount: number;
  includeBoardRental: boolean;
  specialRequests: string;
  arrivalTime: string;
  guests: Guest[];
  bookingNumber: string | null;
}
