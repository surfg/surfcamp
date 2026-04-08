"""
Surf Camp Website Parser v2.0
Multi-page crawling with specialized extractors for different page types
"""
import re
import json
import logging
from typing import Optional, List, Dict, Any, Set
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
import anthropic

logger = logging.getLogger(__name__)


@dataclass
class CampData:
    """Structured data extracted from camp website"""
    name: str = ""
    description: str = ""
    short_description: str = ""
    history: str = ""
    address: str = ""

    # Pricing
    price_per_night: Optional[float] = None
    price_per_lesson: Optional[float] = None
    packages: List[Dict] = field(default_factory=list)

    # Contact
    email: str = ""
    phone: str = ""
    whatsapp: str = ""
    instagram: str = ""
    facebook: str = ""
    youtube: str = ""
    website: str = ""

    # Features
    skill_levels: List[str] = field(default_factory=list)
    amenities: List[str] = field(default_factory=list)
    has_pool: bool = False
    has_restaurant: bool = False
    has_yoga: bool = False

    # Accommodation
    room_types: List[Dict] = field(default_factory=list)
    max_guests: Optional[int] = None

    # Media
    image_urls: List[str] = field(default_factory=list)

    # Instructors
    instructors: List[Dict] = field(default_factory=list)

    # Activities
    activities: List[Dict] = field(default_factory=list)

    # Surf info
    surf_spots: List[str] = field(default_factory=list)
    board_types: List[str] = field(default_factory=list)

    # Meta
    source_url: str = ""
    pages_crawled: List[str] = field(default_factory=list)
    parse_errors: List[str] = field(default_factory=list)


# Page type patterns for link classification
PAGE_PATTERNS = {
    'about': [
        r'/about', r'/о-нас', r'/uber-uns', r'/sobre', r'/chi-siamo',
        r'/who-we-are', r'/our-story', r'/history', r'/team'
    ],
    'pricing': [
        r'/pric', r'/rate', r'/cost', r'/tarif', r'/price',
        r'/booking', r'/book-now', r'/reserve', r'/packages', r'/offers'
    ],
    'accommodation': [
        r'/room', r'/accomm', r'/stay', r'/lodge', r'/住宿',
        r'/unterkunft', r'/alojamiento', r'/hébergement', r'/sleep'
    ],
    'team': [
        r'/team', r'/instructor', r'/coach', r'/staff', r'/trainer',
        r'/our-team', r'/meet-the-team', r'/teachers'
    ],
    'activities': [
        r'/activit', r'/things-to-do', r'/experience', r'/adventure',
        r'/excursion', r'/tour', r'/yoga', r'/fitness'
    ],
    'gallery': [
        r'/gallery', r'/photo', r'/media', r'/image', r'/galerie',
        r'/portfolio', r'/pictures'
    ],
    'contact': [
        r'/contact', r'/kontakt', r'/contacto', r'/reach-us',
        r'/get-in-touch', r'/location', r'/find-us'
    ],
    'surf': [
        r'/surf', r'/wave', r'/spot', r'/lesson', r'/course',
        r'/learn', r'/beginner', r'/camp'
    ],
    'equipment': [
        r'/equipment', r'/board', r'/gear', r'/rental', r'/wetsuit',
        r'/surfboard', r'/material', r'/ausrustung'
    ],
    'faq': [
        r'/faq', r'/question', r'/help', r'/support'
    ]
}


class CampParser:
    """
    Multi-page surf camp website parser
    Crawls subpages and extracts specialized data from each
    """

    def __init__(
        self,
        anthropic_api_key: str = None,
        use_ai: bool = False,
        max_pages: int = 8,
        evomi_client=None
    ):
        self.anthropic_api_key = anthropic_api_key
        self.use_ai = use_ai
        self.max_pages = max_pages
        self.evomi_client = evomi_client

        if anthropic_api_key and use_ai:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Anthropic client: {e}")
                self.anthropic_client = None
        else:
            self.anthropic_client = None

    def parse(self, html: str, url: str) -> CampData:
        """
        Parse homepage only (backward compatible)
        """
        return self.parse_single_page(html, url)

    def parse_single_page(self, html: str, url: str) -> CampData:
        """
        Parse a single page (homepage)
        """
        data = CampData(source_url=url, website=url)
        data.pages_crawled.append(url)

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove unwanted tags
            for tag in soup(['script', 'style', 'noscript', 'iframe']):
                tag.decompose()

            # Extract data from homepage
            self._extract_basic_info(soup, data)
            self._extract_images(soup, url, data)  # Images from homepage
            self._extract_contacts(soup, html, data)
            self._extract_social(soup, html, data)
            self._extract_structured_data(soup, data)

            # Use AI for complex extraction
            if self.use_ai and self.anthropic_client:
                self._ai_extract(html, url, data)

        except Exception as e:
            logger.error(f"[CampParser] Error parsing {url}: {e}")
            data.parse_errors.append(str(e))

        return data

    def crawl_and_parse(self, homepage_html: str, homepage_url: str) -> CampData:
        """
        Crawl multiple pages and extract comprehensive data

        1. Parse homepage (get images, basic info)
        2. Discover internal links
        3. Classify links by page type
        4. Fetch and parse important pages
        5. Merge all data
        """
        # Start with homepage
        data = self.parse_single_page(homepage_html, homepage_url)
        logger.info(f"[Crawler] Parsed homepage: {homepage_url}")

        if not self.evomi_client:
            logger.warning("[Crawler] No evomi client - skipping subpage crawling")
            return data

        try:
            soup = BeautifulSoup(homepage_html, 'html.parser')
            base_domain = urlparse(homepage_url).netloc

            # Discover and classify links
            links_by_type = self._discover_links(soup, homepage_url, base_domain)

            # Prioritize pages to crawl
            pages_to_crawl = self._prioritize_pages(links_by_type)
            logger.info(f"[Crawler] Found {len(pages_to_crawl)} subpages to crawl")

            # Crawl each page
            crawled_count = 0
            for page_type, page_url in pages_to_crawl:
                if crawled_count >= self.max_pages:
                    break

                if page_url in data.pages_crawled:
                    continue

                try:
                    logger.info(f"[Crawler] Fetching [{page_type}]: {page_url}")
                    response = self.evomi_client.fetch(page_url)

                    if response.success and response.html:
                        data.pages_crawled.append(page_url)
                        self._parse_subpage(response.html, page_url, page_type, data)
                        crawled_count += 1
                    else:
                        logger.warning(f"[Crawler] Failed to fetch: {page_url}")

                except Exception as e:
                    logger.warning(f"[Crawler] Error crawling {page_url}: {e}")
                    continue

            logger.info(f"[Crawler] Crawled {crawled_count} subpages for {homepage_url}")

        except Exception as e:
            logger.error(f"[Crawler] Crawl error: {e}")
            data.parse_errors.append(f"crawl: {e}")

        return data

    def _discover_links(
        self,
        soup: BeautifulSoup,
        base_url: str,
        base_domain: str
    ) -> Dict[str, List[str]]:
        """
        Discover and classify internal links
        """
        links_by_type = {ptype: [] for ptype in PAGE_PATTERNS.keys()}
        links_by_type['other'] = []
        seen_urls = set()

        for a_tag in soup.find_all('a', href=True):
            href = a_tag.get('href', '').strip()

            # Skip empty, anchors, javascript, mailto, tel
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            # Make absolute URL
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif not href.startswith('http'):
                full_url = urljoin(base_url, href)
            else:
                full_url = href

            # Check if same domain
            parsed = urlparse(full_url)
            if parsed.netloc != base_domain:
                continue

            # Normalize URL (remove trailing slash, fragments)
            normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

            if normalized in seen_urls:
                continue
            seen_urls.add(normalized)

            # Skip file downloads
            if any(normalized.lower().endswith(ext) for ext in ['.pdf', '.doc', '.zip', '.jpg', '.png']):
                continue

            # Classify link
            path_lower = parsed.path.lower()
            classified = False

            for page_type, patterns in PAGE_PATTERNS.items():
                if any(re.search(pattern, path_lower) for pattern in patterns):
                    links_by_type[page_type].append(normalized)
                    classified = True
                    break

            if not classified:
                links_by_type['other'].append(normalized)

        return links_by_type

    def _prioritize_pages(self, links_by_type: Dict[str, List[str]]) -> List[tuple]:
        """
        Prioritize which pages to crawl first
        Returns list of (page_type, url) tuples
        """
        priority_order = [
            'pricing',      # Most important - prices
            'accommodation',# Room types
            'team',         # Instructors
            'activities',   # Activities/yoga/tours
            'surf',         # Surf spots, lessons, boards
            'equipment',    # Board types, rental info
            'about',        # History, description
            'contact',      # Contact info
            'gallery',      # More images (but we prioritize homepage)
        ]

        result = []
        for page_type in priority_order:
            urls = links_by_type.get(page_type, [])
            # Take max 2 pages per type
            for url in urls[:2]:
                result.append((page_type, url))

        return result

    def _parse_subpage(
        self,
        html: str,
        url: str,
        page_type: str,
        data: CampData
    ):
        """
        Parse a subpage based on its type
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Remove unwanted tags
            for tag in soup(['script', 'style', 'noscript', 'iframe', 'nav', 'footer']):
                tag.decompose()

            # Call specialized extractor based on page type
            extractors = {
                'pricing': self._extract_pricing_page,
                'accommodation': self._extract_accommodation_page,
                'team': self._extract_team_page,
                'activities': self._extract_activities_page,
                'about': self._extract_about_page,
                'contact': self._extract_contact_page,
                'surf': self._extract_surf_page,
                'equipment': self._extract_equipment_page,
                'gallery': self._extract_gallery_page,
            }

            extractor = extractors.get(page_type)
            if extractor:
                extractor(soup, html, url, data)

            # Always try to extract contacts from any page
            self._extract_contacts(soup, html, data)

        except Exception as e:
            logger.warning(f"[Crawler] Error parsing {page_type} page {url}: {e}")
            data.parse_errors.append(f"{page_type}: {e}")

    # ==================== SPECIALIZED EXTRACTORS ====================

    def _extract_pricing_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract pricing information from pricing/rates page"""
        logger.info(f"[Extractor] Parsing pricing page: {url}")

        # Look for price patterns
        text = soup.get_text()

        # Extract prices with currency
        price_patterns = [
            r'€\s*(\d+(?:[.,]\d{2})?)',  # €50 or €50.00
            r'(\d+(?:[.,]\d{2})?)\s*€',  # 50€
            r'\$\s*(\d+(?:[.,]\d{2})?)',  # $50
            r'(\d+(?:[.,]\d{2})?)\s*(?:EUR|USD|per night|/night|per person)',
        ]

        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                try:
                    price = float(m.replace(',', '.'))
                    if 10 < price < 5000:  # Reasonable price range
                        prices.append(price)
                except:
                    pass

        # Set lowest reasonable price as price_per_night if not set
        if prices and not data.price_per_night:
            # Filter out likely per-lesson prices (usually lower)
            night_prices = [p for p in prices if p >= 30]
            if night_prices:
                data.price_per_night = min(night_prices)

        # Look for packages/offers
        package_sections = soup.find_all(['div', 'section'], class_=re.compile(
            r'package|offer|price|rate|plan', re.I
        ))

        for section in package_sections[:5]:
            package = self._extract_package(section)
            if package and package not in data.packages:
                data.packages.append(package)

        # Use AI for detailed extraction if available
        if self.use_ai and self.anthropic_client:
            self._ai_extract_prices(text[:8000], data)

    def _extract_accommodation_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract accommodation/room information"""
        logger.info(f"[Extractor] Parsing accommodation page: {url}")

        # Look for room types
        room_sections = soup.find_all(['div', 'article', 'section'], class_=re.compile(
            r'room|suite|dorm|accommodation|bungalow|villa', re.I
        ))

        for section in room_sections[:10]:
            room = {
                'name': '',
                'description': '',
                'price': None,
                'capacity': None,
                'amenities': []
            }

            # Get room name
            heading = section.find(['h2', 'h3', 'h4'])
            if heading:
                room['name'] = heading.get_text(strip=True)

            # Get description
            desc = section.find('p')
            if desc:
                room['description'] = desc.get_text(strip=True)[:300]

            # Get price
            price_elem = section.find(string=re.compile(r'[€$]\s*\d+|\d+\s*[€$]'))
            if price_elem:
                price_match = re.search(r'(\d+)', str(price_elem))
                if price_match:
                    room['price'] = int(price_match.group(1))

            # Get capacity
            capacity_match = re.search(r'(\d+)\s*(?:person|guest|people|pax)', section.get_text(), re.I)
            if capacity_match:
                room['capacity'] = int(capacity_match.group(1))

            if room['name']:
                data.room_types.append(room)

        # Extract additional amenities
        amenity_keywords = [
            'air conditioning', 'ac', 'wifi', 'private bathroom', 'shared bathroom',
            'balcony', 'sea view', 'ocean view', 'terrace', 'kitchen', 'tv',
            'safe', 'mini fridge', 'fan', 'mosquito net'
        ]

        text_lower = soup.get_text().lower()
        for amenity in amenity_keywords:
            if amenity in text_lower and amenity not in data.amenities:
                data.amenities.append(amenity)

    def _extract_team_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract team/instructor information"""
        logger.info(f"[Extractor] Parsing team page: {url}")

        # Look for team member sections
        team_sections = soup.find_all(['div', 'article', 'li'], class_=re.compile(
            r'team|member|instructor|coach|staff|person|trainer', re.I
        ))

        for section in team_sections[:15]:
            instructor = {
                'name': '',
                'bio': '',
                'experience_years': None,
                'certifications': [],
                'languages': [],
                'is_head_coach': False
            }

            # Get name
            name_elem = section.find(['h2', 'h3', 'h4', 'strong'])
            if name_elem:
                instructor['name'] = name_elem.get_text(strip=True)

            # Get bio
            bio_elem = section.find('p')
            if bio_elem:
                instructor['bio'] = bio_elem.get_text(strip=True)[:500]

            # Check for head coach
            section_text = section.get_text().lower()
            if any(x in section_text for x in ['head coach', 'head instructor', 'founder', 'owner', 'director']):
                instructor['is_head_coach'] = True

            # Extract years of experience
            exp_match = re.search(r'(\d+)\+?\s*(?:years?|ans?|años?)', section_text)
            if exp_match:
                instructor['experience_years'] = int(exp_match.group(1))

            # Extract certifications
            cert_patterns = ['ISA', 'ASI', 'BSA', 'lifeguard', 'first aid', 'CPR', 'yoga certified', 'RYT']
            for cert in cert_patterns:
                if cert.lower() in section_text:
                    instructor['certifications'].append(cert)

            # Extract languages
            lang_patterns = ['english', 'spanish', 'portuguese', 'french', 'german', 'italian', 'russian', 'dutch']
            for lang in lang_patterns:
                if lang in section_text:
                    instructor['languages'].append(lang.capitalize())

            # Only add if we found a name
            if instructor['name'] and len(instructor['name']) > 2:
                # Check if instructor already exists
                existing_names = [i['name'].lower() for i in data.instructors]
                if instructor['name'].lower() not in existing_names:
                    data.instructors.append(instructor)

    def _extract_activities_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract activities and additional services"""
        logger.info(f"[Extractor] Parsing activities page: {url}")

        # Look for activity sections
        activity_sections = soup.find_all(['div', 'article', 'li'], class_=re.compile(
            r'activity|service|experience|adventure|tour|excursion', re.I
        ))

        for section in activity_sections[:15]:
            activity = {
                'name': '',
                'description': '',
                'price': None,
                'is_included': False
            }

            # Get name
            name_elem = section.find(['h2', 'h3', 'h4', 'strong'])
            if name_elem:
                activity['name'] = name_elem.get_text(strip=True)

            # Get description
            desc_elem = section.find('p')
            if desc_elem:
                activity['description'] = desc_elem.get_text(strip=True)[:300]

            # Check if included
            section_text = section.get_text().lower()
            if any(x in section_text for x in ['included', 'free', 'complimentary']):
                activity['is_included'] = True

            # Get price
            price_match = re.search(r'[€$]\s*(\d+)|(\d+)\s*[€$]', section.get_text())
            if price_match:
                price_str = price_match.group(1) or price_match.group(2)
                activity['price'] = int(price_str)

            if activity['name'] and len(activity['name']) > 2:
                existing_names = [a['name'].lower() for a in data.activities]
                if activity['name'].lower() not in existing_names:
                    data.activities.append(activity)

        # Check for yoga
        if 'yoga' in soup.get_text().lower():
            data.has_yoga = True
            if 'yoga' not in [a.lower() for a in data.amenities]:
                data.amenities.append('yoga')

    def _extract_about_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract about/history information"""
        logger.info(f"[Extractor] Parsing about page: {url}")

        # Find main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|about'))

        if main_content:
            paragraphs = main_content.find_all('p')
            text_parts = []

            for p in paragraphs[:15]:
                text = p.get_text(strip=True)
                if len(text) > 50:
                    text_parts.append(text)

            if text_parts:
                # Update description if current one is short
                combined = '\n\n'.join(text_parts[:5])
                if len(combined) > len(data.description):
                    data.description = combined

                # Try to extract history
                history_text = '\n\n'.join(text_parts)
                history_keywords = ['founded', 'started', 'began', 'history', 'since', 'established', 'years ago']
                if any(kw in history_text.lower() for kw in history_keywords):
                    # Find paragraphs with history keywords
                    history_parts = [p for p in text_parts if any(kw in p.lower() for kw in history_keywords)]
                    if history_parts:
                        data.history = '\n\n'.join(history_parts[:2])

    def _extract_contact_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract contact information"""
        logger.info(f"[Extractor] Parsing contact page: {url}")

        # This mainly uses the general _extract_contacts method
        # but we can also look for embedded maps for address

        # Look for Google Maps embed
        maps_iframe = soup.find('iframe', src=re.compile(r'google.*maps', re.I))
        if maps_iframe:
            src = maps_iframe.get('src', '')
            # Try to extract place name from maps URL
            place_match = re.search(r'place/([^/&]+)', src)
            if place_match and not data.address:
                data.address = place_match.group(1).replace('+', ' ')

    def _extract_surf_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract surf-specific information"""
        logger.info(f"[Extractor] Parsing surf page: {url}")

        text = soup.get_text().lower()

        # Extract surf spots mentioned
        spot_patterns = [
            r'surf (?:spot|break|beach)[:\s]+([A-Za-z\s]+)',
            r'(?:surfing at|waves at|lessons at)\s+([A-Za-z\s]+)',
        ]

        for pattern in spot_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                spot = match.strip().title()
                if spot and len(spot) > 3 and spot not in data.surf_spots:
                    data.surf_spots.append(spot)

        # Extract board types (comprehensive list)
        board_types_map = {
            'shortboard': ['shortboard', 'short board'],
            'longboard': ['longboard', 'long board'],
            'funboard': ['funboard', 'fun board', 'hybrid'],
            'fish': ['fish', 'retro fish'],
            'mini malibu': ['mini malibu', 'minimalibu', 'mini mal'],
            'soft top': ['soft top', 'softtop', 'foam board', 'softboard'],
            'SUP': ['sup', 'stand up paddle', 'paddleboard'],
            'bodyboard': ['bodyboard', 'boogie'],
            'mid-length': ['mid length', 'midlength', 'egg'],
        }

        for board_name, keywords in board_types_map.items():
            for keyword in keywords:
                if keyword in text and board_name not in data.board_types:
                    data.board_types.append(board_name)
                    break

        # Extract skill levels
        if 'beginner' in text and 'beginner' not in data.skill_levels:
            data.skill_levels.append('beginner')
        if 'intermediate' in text and 'intermediate' not in data.skill_levels:
            data.skill_levels.append('intermediate')
        if 'advanced' in text and 'advanced' not in data.skill_levels:
            data.skill_levels.append('advanced')

        # Extract lesson prices
        lesson_price_pattern = r'(?:lesson|class|course)[^€$\d]*[€$]\s*(\d+)|(\d+)\s*[€$][^a-z]*(?:lesson|class|hour)'
        matches = re.findall(lesson_price_pattern, text, re.I)
        for match in matches:
            price = match[0] or match[1]
            if price:
                price_int = int(price)
                if 20 <= price_int <= 200 and not data.price_per_lesson:
                    data.price_per_lesson = price_int

    def _extract_equipment_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract equipment/board information"""
        logger.info(f"[Extractor] Parsing equipment page: {url}")

        text = soup.get_text().lower()

        # Comprehensive board type list
        board_types_map = {
            'shortboard': ['shortboard', 'short board', 'performance board'],
            'longboard': ['longboard', 'long board', 'classic longboard', 'noserider'],
            'funboard': ['funboard', 'fun board', 'hybrid'],
            'fish': ['fish', 'retro fish', 'quad fish'],
            'mini malibu': ['mini malibu', 'minimalibu', 'mini-mal', 'mini mal'],
            'soft top': ['soft top', 'softtop', 'foam board', 'softboard', 'soft board'],
            'gun': ['gun', 'big wave board'],
            'SUP': ['sup', 'stand up paddle', 'paddleboard', 'stand-up paddle'],
            'bodyboard': ['bodyboard', 'boogie board', 'body board'],
            'foamie': ['foamie', 'beginner board', 'learner board'],
            'mid-length': ['mid length', 'midlength', 'mid-length', 'egg'],
            'epoxy': ['epoxy board', 'epoxy'],
        }

        for board_name, keywords in board_types_map.items():
            for keyword in keywords:
                if keyword in text and board_name not in data.board_types:
                    data.board_types.append(board_name)
                    break

        # Extract wetsuit info
        wetsuit_keywords = ['wetsuit', 'wet suit', 'rashguard', 'rash guard', 'booties', 'surf boots']
        for kw in wetsuit_keywords:
            if kw in text and kw not in data.amenities:
                data.amenities.append(kw)

        # Extract rental prices
        rental_patterns = [
            r'board rental[:\s]*[€$]?\s*(\d+)',
            r'rent(?:al)?[:\s]*[€$]?\s*(\d+)',
            r'(\d+)\s*[€$]?\s*(?:per day|/day|daily)',
        ]

        for pattern in rental_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                # Store in activities as rental service
                rental_activity = {
                    'name': 'Board Rental',
                    'description': 'Surfboard rental available',
                    'price': int(match.group(1)),
                    'is_included': False
                }
                if not any(a.get('name') == 'Board Rental' for a in data.activities):
                    data.activities.append(rental_activity)
                break

    def _extract_gallery_page(self, soup: BeautifulSoup, html: str, url: str, data: CampData):
        """Extract additional images from gallery (supplement to homepage images)"""
        logger.info(f"[Extractor] Parsing gallery page: {url}")

        # We already got images from homepage, but we can add more
        # Only add high-quality images
        current_count = len(data.image_urls)
        max_additional = 10  # Add max 10 more from gallery

        for img in soup.find_all('img'):
            if len(data.image_urls) >= current_count + max_additional:
                break

            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if not src:
                continue

            # Make absolute URL
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = urljoin(url, src)
            elif not src.startswith('http'):
                src = urljoin(url, src)

            # Filter quality - gallery images should be larger
            if any(x in src.lower() for x in ['thumb', 'icon', 'logo', 'avatar', '150x', '100x']):
                continue

            if src not in data.image_urls:
                data.image_urls.append(src)

    # ==================== HELPER EXTRACTORS ====================

    def _extract_package(self, section) -> Optional[Dict]:
        """Extract package details from a section"""
        package = {
            'name': '',
            'price': None,
            'duration': '',
            'includes': []
        }

        # Get package name
        heading = section.find(['h2', 'h3', 'h4', 'strong'])
        if heading:
            package['name'] = heading.get_text(strip=True)[:100]

        # Get price
        price_text = section.find(string=re.compile(r'[€$]\d+|\d+[€$]'))
        if price_text:
            price_match = re.search(r'(\d+)', str(price_text))
            if price_match:
                package['price'] = int(price_match.group(1))

        # Get duration
        duration_match = re.search(r'(\d+)\s*(?:night|day|week)', section.get_text(), re.I)
        if duration_match:
            num = duration_match.group(1)
            unit = 'nights' if 'night' in duration_match.group(0).lower() else 'days'
            package['duration'] = f"{num} {unit}"

        # Get includes
        list_items = section.find_all('li')
        for li in list_items[:10]:
            text = li.get_text(strip=True)
            if text and len(text) > 3:
                package['includes'].append(text[:100])

        if package['name'] and (package['price'] or package['includes']):
            return package
        return None

    def _extract_basic_info(self, soup: BeautifulSoup, data: CampData):
        """Extract basic info from HTML (unchanged from v1)"""
        try:
            # Title - with validation
            title = soup.find('title')
            if title:
                title_text = title.text.strip()
                name = title_text.split('|')[0].split(' - ')[0].strip()
                if name and len(name) > 3 and not name.isdigit() and name.lower() not in ['error', 'forbidden', 'not found', '403', '404', '500']:
                    data.name = name

            # Fallback: try h1 tag
            if not data.name:
                h1 = soup.find('h1')
                if h1:
                    h1_text = h1.get_text(strip=True)
                    if h1_text and len(h1_text) > 3 and len(h1_text) < 100:
                        data.name = h1_text

            # Fallback: try og:title meta
            if not data.name:
                og_title = soup.find('meta', property='og:title')
                if og_title:
                    data.name = og_title.get('content', '').split('|')[0].strip()

            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data.short_description = meta_desc.get('content', '')[:300]

            # OG description (often better)
            og_desc = soup.find('meta', property='og:description')
            if og_desc and not data.short_description:
                data.short_description = og_desc.get('content', '')[:300]

            # Main content - look for description
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|about'))
            if main_content:
                paragraphs = main_content.find_all('p')
                description_parts = []
                for p in paragraphs[:10]:
                    text = p.get_text(strip=True)
                    if len(text) > 50:
                        description_parts.append(text)
                if description_parts:
                    data.description = '\n\n'.join(description_parts[:5])

            # Look for skill levels
            text_content = soup.get_text().lower()
            if 'beginner' in text_content:
                data.skill_levels.append('beginner')
            if 'intermediate' in text_content:
                data.skill_levels.append('intermediate')
            if 'advanced' in text_content:
                data.skill_levels.append('advanced')

            # Look for amenities
            if any(x in text_content for x in ['pool', 'бассейн', 'piscina']):
                data.has_pool = True
                data.amenities.append('pool')
            if any(x in text_content for x in ['restaurant', 'ресторан', 'dining']):
                data.has_restaurant = True
                data.amenities.append('restaurant')
            if any(x in text_content for x in ['yoga', 'йога']):
                data.has_yoga = True
                data.amenities.append('yoga')
            if any(x in text_content for x in ['wifi', 'wi-fi']):
                data.amenities.append('wifi')
            if any(x in text_content for x in ['breakfast', 'завтрак']):
                data.amenities.append('breakfast')

        except Exception as e:
            logger.warning(f"[CampParser] Error in basic extraction: {e}")
            data.parse_errors.append(f"basic_info: {e}")

    def _extract_images(self, soup: BeautifulSoup, base_url: str, data: CampData):
        """Extract image URLs from HTML (homepage only, high priority)"""
        try:
            image_urls = []
            seen = set()

            # Find all images
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or img.get('data-original')
                if not src:
                    continue

                # Skip data: URLs
                if src.startswith('data:'):
                    continue

                # Make absolute URL
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                elif not src.startswith('http'):
                    src = urljoin(base_url, src)

                # Filter out small images, icons, logos
                src_lower = src.lower()
                if any(x in src_lower for x in ['logo', 'icon', 'avatar', 'flag', 'pixel', '1x1', 'tracking', 'blank', 'spacer']):
                    continue

                # Filter by extension
                if any(src_lower.endswith(ext) for ext in ['.svg', '.ico', '.gif']):
                    continue

                # Check image dimensions hint in URL
                if re.search(r'[_-](50|100|150)x', src_lower):
                    continue

                if src not in seen:
                    seen.add(src)
                    image_urls.append(src)

            # Also check background images in style
            for elem in soup.find_all(style=re.compile(r'background.*url')):
                style = elem.get('style', '')
                urls = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
                for url in urls:
                    if url.startswith('/'):
                        url = urljoin(base_url, url)
                    if url.startswith('http') and url not in seen:
                        seen.add(url)
                        image_urls.append(url)

            # Also check srcset for high-res images
            for img in soup.find_all('img', srcset=True):
                srcset = img.get('srcset', '')
                # Parse srcset and get largest image
                parts = srcset.split(',')
                for part in parts:
                    url_part = part.strip().split()[0]
                    if url_part.startswith('/'):
                        url_part = urljoin(base_url, url_part)
                    if url_part.startswith('http') and url_part not in seen:
                        seen.add(url_part)
                        image_urls.append(url_part)

            data.image_urls = image_urls[:25]  # Limit to 25 images from homepage

        except Exception as e:
            logger.warning(f"[CampParser] Error extracting images: {e}")
            data.parse_errors.append(f"images: {e}")

    def _extract_contacts(self, soup: BeautifulSoup, html: str, data: CampData):
        """Extract contact information"""
        try:
            # Email
            if not data.email:
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', html)
                emails = [e for e in emails if not any(x in e.lower() for x in ['example', 'test', 'wordpress', 'cloudways', 'wix', 'squarespace'])]
                if emails:
                    data.email = emails[0]

            # Phone
            if not data.phone:
                phones = re.findall(r'[\+]?[\d\s\-\(\)]{10,20}', html)
                phones = [p.strip() for p in phones if len(re.sub(r'\D', '', p)) >= 9]
                if phones:
                    data.phone = phones[0]

            # WhatsApp
            if not data.whatsapp:
                whatsapp_match = re.search(r'whatsapp[^\d]*(\+?[\d\s\-]+)', html.lower())
                if whatsapp_match:
                    data.whatsapp = re.sub(r'\s', '', whatsapp_match.group(1))

            # Address - look for address tags or structured data
            if not data.address:
                address_elem = soup.find('address') or soup.find(class_=re.compile(r'address'))
                if address_elem:
                    data.address = address_elem.get_text(strip=True)[:300]

        except Exception as e:
            logger.warning(f"[CampParser] Error extracting contacts: {e}")
            data.parse_errors.append(f"contacts: {e}")

    def _extract_social(self, soup: BeautifulSoup, html: str, data: CampData):
        """Extract social media links"""
        try:
            # Instagram
            if not data.instagram:
                insta_match = re.search(r'instagram\.com/([a-zA-Z0-9_\.]+)', html)
                if insta_match:
                    data.instagram = '@' + insta_match.group(1).strip('/')

            # Facebook
            if not data.facebook:
                fb_match = re.search(r'facebook\.com/([a-zA-Z0-9\.\-]+)', html)
                if fb_match:
                    data.facebook = fb_match.group(1).strip('/')

            # YouTube
            if not data.youtube:
                yt_match = re.search(r'youtube\.com/(?:channel/|c/|user/)?([a-zA-Z0-9_\-]+)', html)
                if yt_match:
                    data.youtube = yt_match.group(1)

        except Exception as e:
            logger.warning(f"[CampParser] Error extracting social: {e}")
            data.parse_errors.append(f"social: {e}")

    def _extract_structured_data(self, soup: BeautifulSoup, data: CampData):
        """Extract JSON-LD structured data"""
        try:
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    ld_data = json.loads(script.string)
                    if isinstance(ld_data, list):
                        ld_data = ld_data[0] if ld_data else {}

                    if isinstance(ld_data, dict):
                        # Address
                        if 'address' in ld_data and not data.address:
                            addr = ld_data['address']
                            if isinstance(addr, dict):
                                parts = [
                                    addr.get('streetAddress', ''),
                                    addr.get('addressLocality', ''),
                                    addr.get('addressRegion', ''),
                                    addr.get('postalCode', ''),
                                    addr.get('addressCountry', '')
                                ]
                                data.address = ', '.join(p for p in parts if p)
                            elif isinstance(addr, str):
                                data.address = addr

                        # Phone
                        if 'telephone' in ld_data and not data.phone:
                            data.phone = ld_data['telephone']

                        # Email
                        if 'email' in ld_data and not data.email:
                            data.email = ld_data['email']

                        # Price
                        if 'priceRange' in ld_data and not data.price_per_night:
                            price_match = re.search(r'(\d+)', ld_data['priceRange'])
                            if price_match:
                                data.price_per_night = float(price_match.group(1))

                        # Rating
                        if 'aggregateRating' in ld_data:
                            rating = ld_data['aggregateRating']
                            # Could be used for external ratings

                except json.JSONDecodeError:
                    pass

        except Exception as e:
            logger.warning(f"[CampParser] Error extracting structured data: {e}")

    def _ai_extract(self, html: str, url: str, data: CampData):
        """Use Claude AI to extract structured data from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            text_content = soup.get_text(separator='\n', strip=True)
            text_content = text_content[:15000]

            prompt = f"""Analyze this surf camp website content and extract structured data.
Website URL: {url}

Content:
{text_content}

Extract and return JSON with these fields (use null if not found):
{{
    "name": "camp name",
    "description": "detailed description (2-3 paragraphs)",
    "short_description": "one sentence summary",
    "address": "full address",
    "price_per_night": number or null (in USD/EUR),
    "price_per_lesson": number or null,
    "packages": [
        {{"name": "package name", "price": number, "duration": "7 nights", "includes": ["item1", "item2"]}}
    ],
    "skill_levels": ["beginner", "intermediate", "advanced"] - only include what's offered,
    "amenities": ["pool", "restaurant", "yoga", "wifi", "breakfast", etc],
    "instructors": [
        {{"name": "name", "bio": "short bio", "experience_years": number, "languages": ["English", "Spanish"]}}
    ],
    "activities": [
        {{"name": "activity name", "description": "description", "price": number or null, "is_included": boolean}}
    ],
    "board_types": ["shortboard", "longboard", "funboard", "soft top", etc] - only include what's mentioned,
    "surf_spots": ["spot names mentioned"],
    "has_pool": boolean,
    "has_restaurant": boolean,
    "has_yoga": boolean
}}

Return ONLY valid JSON, no markdown or explanations."""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()

            # Extract JSON
            if '```' in response_text:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                if match:
                    response_text = match.group(1)

            ai_data = json.loads(response_text)

            # Merge AI data
            if ai_data.get('name') and not data.name:
                data.name = ai_data['name']
            if ai_data.get('description') and len(ai_data['description']) > len(data.description):
                data.description = ai_data['description']
            if ai_data.get('short_description') and not data.short_description:
                data.short_description = ai_data['short_description']
            if ai_data.get('address') and not data.address:
                data.address = ai_data['address']
            if ai_data.get('price_per_night') and not data.price_per_night:
                data.price_per_night = float(ai_data['price_per_night'])
            if ai_data.get('price_per_lesson') and not data.price_per_lesson:
                data.price_per_lesson = float(ai_data['price_per_lesson'])
            if ai_data.get('packages'):
                data.packages.extend(ai_data['packages'])
            if ai_data.get('skill_levels'):
                data.skill_levels = list(set(data.skill_levels + ai_data['skill_levels']))
            if ai_data.get('amenities'):
                data.amenities = list(set(data.amenities + ai_data['amenities']))
            if ai_data.get('instructors'):
                for inst in ai_data['instructors']:
                    if inst.get('name') and inst['name'].lower() not in [i['name'].lower() for i in data.instructors]:
                        data.instructors.append(inst)
            if ai_data.get('activities'):
                for act in ai_data['activities']:
                    if act.get('name') and act['name'].lower() not in [a['name'].lower() for a in data.activities]:
                        data.activities.append(act)

            # Board types
            if ai_data.get('board_types'):
                data.board_types = list(set(data.board_types + ai_data['board_types']))

            # Surf spots
            if ai_data.get('surf_spots'):
                data.surf_spots = list(set(data.surf_spots + ai_data['surf_spots']))

            # Update boolean flags
            amenities_lower = [a.lower() for a in data.amenities]
            data.has_pool = ai_data.get('has_pool', False) or 'pool' in amenities_lower or data.has_pool
            data.has_restaurant = ai_data.get('has_restaurant', False) or 'restaurant' in amenities_lower or data.has_restaurant
            data.has_yoga = ai_data.get('has_yoga', False) or 'yoga' in amenities_lower or data.has_yoga

            logger.info(f"[CampParser] AI extraction successful for {url}")

        except json.JSONDecodeError as e:
            logger.warning(f"[CampParser] Failed to parse AI response as JSON: {e}")
            data.parse_errors.append(f"ai_json: {e}")
        except Exception as e:
            logger.warning(f"[CampParser] AI extraction failed: {e}")
            data.parse_errors.append(f"ai: {e}")

    def _ai_extract_prices(self, text: str, data: CampData):
        """Use AI specifically for price extraction"""
        try:
            prompt = f"""Extract pricing information from this surf camp website text.

Text:
{text}

Return JSON with:
{{
    "price_per_night": number or null (accommodation only),
    "price_per_lesson": number or null (single surf lesson),
    "packages": [
        {{
            "name": "package name",
            "price": number,
            "duration": "X nights/days",
            "includes": ["accommodation", "lessons", "breakfast", etc]
        }}
    ]
}}

Return ONLY valid JSON."""

            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text.strip()
            if '```' in response_text:
                match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                if match:
                    response_text = match.group(1)

            ai_data = json.loads(response_text)

            if ai_data.get('price_per_night') and not data.price_per_night:
                data.price_per_night = float(ai_data['price_per_night'])
            if ai_data.get('price_per_lesson') and not data.price_per_lesson:
                data.price_per_lesson = float(ai_data['price_per_lesson'])
            if ai_data.get('packages'):
                for pkg in ai_data['packages']:
                    if pkg not in data.packages:
                        data.packages.append(pkg)

        except Exception as e:
            logger.warning(f"[CampParser] AI price extraction failed: {e}")
