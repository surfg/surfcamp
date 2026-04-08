"""
TripAdvisor Parser for reviews and ratings
"""
import re
import json
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


@dataclass
class TripAdvisorReview:
    """Single review from TripAdvisor"""
    author_name: str = ""
    author_country: str = ""
    rating: int = 5
    title: str = ""
    text: str = ""
    visit_date: str = ""
    helpful_votes: int = 0


@dataclass
class TripAdvisorData:
    """Data extracted from TripAdvisor"""
    found: bool = False
    tripadvisor_url: str = ""
    rating: float = 0.0
    reviews_count: int = 0
    reviews: List[TripAdvisorReview] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)
    ranking: str = ""
    price_range: str = ""
    errors: List[str] = field(default_factory=list)


class TripAdvisorParser:
    """
    Search and parse TripAdvisor for surf camp reviews
    """

    def __init__(self, evomi_client):
        """
        Args:
            evomi_client: EvomiClient instance for fetching pages
        """
        self.evomi = evomi_client

    def search_camp(self, camp_name: str, location: str) -> Optional[str]:
        """
        Search for a camp on TripAdvisor

        Args:
            camp_name: Name of the camp
            location: Location (city/country)

        Returns:
            TripAdvisor URL if found, None otherwise
        """
        try:
            # Build search query
            query = f"{camp_name} {location} surf"
            search_url = f"https://www.tripadvisor.com/Search?q={quote_plus(query)}"

            logger.info(f"[TripAdvisor] Searching: {query}")

            response = self.evomi.fetch(search_url)
            if not response.success:
                logger.warning(f"[TripAdvisor] Search failed: {response.error}")
                return None

            soup = BeautifulSoup(response.html, 'html.parser')

            # Look for search results
            # TripAdvisor uses various result containers
            result_links = soup.find_all('a', href=re.compile(r'/Attraction_Review|/Hotel_Review'))

            for link in result_links[:5]:
                href = link.get('href', '')
                text = link.get_text().lower()

                # Check if this looks like our camp
                camp_name_lower = camp_name.lower()
                if any(word in text for word in camp_name_lower.split()[:2]):
                    full_url = 'https://www.tripadvisor.com' + href if href.startswith('/') else href
                    logger.info(f"[TripAdvisor] Found: {full_url}")
                    return full_url

            # Alternative: look in JSON data
            for script in soup.find_all('script'):
                if script.string and 'locationId' in str(script.string):
                    try:
                        # Try to extract URL from embedded data
                        urls = re.findall(r'/(Attraction_Review[^"\']+)', str(script.string))
                        if urls:
                            return f"https://www.tripadvisor.com/{urls[0]}"
                    except:
                        pass

            logger.info(f"[TripAdvisor] Camp not found: {camp_name}")
            return None

        except Exception as e:
            logger.error(f"[TripAdvisor] Search error: {e}")
            return None

    def parse_reviews(self, tripadvisor_url: str, max_reviews: int = 20) -> TripAdvisorData:
        """
        Parse reviews from TripAdvisor page

        Args:
            tripadvisor_url: Full TripAdvisor URL
            max_reviews: Maximum number of reviews to collect

        Returns:
            TripAdvisorData with reviews and rating
        """
        data = TripAdvisorData(tripadvisor_url=tripadvisor_url)

        try:
            logger.info(f"[TripAdvisor] Parsing: {tripadvisor_url}")

            response = self.evomi.fetch(tripadvisor_url)
            if not response.success:
                data.errors.append(f"Failed to fetch: {response.error}")
                return data

            data.found = True
            soup = BeautifulSoup(response.html, 'html.parser')

            # Extract rating
            self._extract_rating(soup, data)

            # Extract reviews
            self._extract_reviews(soup, data, max_reviews)

            # Extract images
            self._extract_images(soup, data)

            # Extract ranking
            self._extract_ranking(soup, data)

            logger.info(f"[TripAdvisor] Parsed: rating={data.rating}, reviews={len(data.reviews)}")

        except Exception as e:
            logger.error(f"[TripAdvisor] Parse error: {e}")
            data.errors.append(str(e))

        return data

    def _extract_rating(self, soup: BeautifulSoup, data: TripAdvisorData):
        """Extract overall rating"""
        try:
            # Look for rating in various formats
            rating_patterns = [
                soup.find('span', class_=re.compile(r'.*rating.*|.*bubble.*')),
                soup.find('div', attrs={'data-test-target': 'review-rating'}),
                soup.find('svg', class_=re.compile(r'.*bubble.*')),
            ]

            for elem in rating_patterns:
                if elem:
                    # Try to get rating from class
                    classes = elem.get('class', [])
                    for cls in classes:
                        match = re.search(r'bubble_(\d+)', str(cls))
                        if match:
                            data.rating = int(match.group(1)) / 10.0
                            break

                    # Try to get from text
                    if not data.rating:
                        text = elem.get_text()
                        match = re.search(r'(\d+\.?\d*)\s*(?:of|out of|/)\s*5', text)
                        if match:
                            data.rating = float(match.group(1))
                            break

            # Look in JSON-LD
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    ld_data = json.loads(script.string)
                    if isinstance(ld_data, dict):
                        if 'aggregateRating' in ld_data:
                            ar = ld_data['aggregateRating']
                            if 'ratingValue' in ar:
                                data.rating = float(ar['ratingValue'])
                            if 'reviewCount' in ar:
                                data.reviews_count = int(ar['reviewCount'])
                except:
                    pass

            # Try to find review count
            count_elem = soup.find(text=re.compile(r'\d+\s*reviews?', re.I))
            if count_elem:
                match = re.search(r'(\d+)\s*reviews?', count_elem, re.I)
                if match:
                    data.reviews_count = int(match.group(1))

        except Exception as e:
            logger.warning(f"[TripAdvisor] Rating extraction error: {e}")
            data.errors.append(f"rating: {e}")

    def _extract_reviews(self, soup: BeautifulSoup, data: TripAdvisorData, max_reviews: int):
        """Extract individual reviews"""
        try:
            # Find review containers
            review_containers = soup.find_all('div', attrs={'data-test-target': 'HR_CC_CARD'})

            if not review_containers:
                # Alternative selectors
                review_containers = soup.find_all('div', class_=re.compile(r'review.*container|reviewSelector'))

            if not review_containers:
                # Try finding by review structure
                review_containers = soup.find_all('div', {'data-reviewid': True})

            for container in review_containers[:max_reviews]:
                review = TripAdvisorReview()

                # Author name
                author = container.find('a', class_=re.compile(r'ui_header_link|member')) or \
                         container.find('span', class_=re.compile(r'.*member.*|.*author.*'))
                if author:
                    review.author_name = author.get_text(strip=True)

                # Author country
                location = container.find('span', class_=re.compile(r'.*location.*|.*hometown.*'))
                if location:
                    review.author_country = location.get_text(strip=True)

                # Rating
                rating_elem = container.find('span', class_=re.compile(r'.*bubble.*|.*rating.*'))
                if rating_elem:
                    classes = rating_elem.get('class', [])
                    for cls in classes:
                        match = re.search(r'bubble_(\d+)', str(cls))
                        if match:
                            review.rating = int(match.group(1)) // 10
                            break

                # Title
                title_elem = container.find('a', class_=re.compile(r'title')) or \
                             container.find('span', class_=re.compile(r'.*title.*'))
                if title_elem:
                    review.title = title_elem.get_text(strip=True)

                # Text
                text_elem = container.find('q') or \
                            container.find('p', class_=re.compile(r'.*partial.*|.*text.*')) or \
                            container.find('span', class_=re.compile(r'.*text.*|.*review.*'))
                if text_elem:
                    review.text = text_elem.get_text(strip=True)

                # Visit date
                date_elem = container.find('span', class_=re.compile(r'.*date.*|.*stay.*'))
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # Extract date like "March 2024"
                    match = re.search(r'([A-Z][a-z]+\s+\d{4})', date_text)
                    if match:
                        review.visit_date = match.group(1)

                # Only add if we have meaningful content
                if review.text and len(review.text) > 20:
                    data.reviews.append(review)

        except Exception as e:
            logger.warning(f"[TripAdvisor] Reviews extraction error: {e}")
            data.errors.append(f"reviews: {e}")

    def _extract_images(self, soup: BeautifulSoup, data: TripAdvisorData):
        """Extract photo URLs"""
        try:
            image_urls = set()

            # Find gallery images
            for img in soup.find_all('img'):
                src = img.get('src') or img.get('data-src')
                if not src:
                    continue

                # TripAdvisor uses media-cdn
                if 'media-cdn.tripadvisor.com' in src or 'photo' in src.lower():
                    # Get larger version if possible
                    src = re.sub(r'/s/', '/o/', src)  # original size
                    src = re.sub(r'w=\d+', 'w=800', src)
                    image_urls.add(src)

            data.image_urls = list(image_urls)[:15]

        except Exception as e:
            logger.warning(f"[TripAdvisor] Image extraction error: {e}")
            data.errors.append(f"images: {e}")

    def _extract_ranking(self, soup: BeautifulSoup, data: TripAdvisorData):
        """Extract ranking info"""
        try:
            rank_elem = soup.find('span', class_=re.compile(r'.*rank.*|.*header_popularity.*'))
            if rank_elem:
                data.ranking = rank_elem.get_text(strip=True)

        except Exception as e:
            data.errors.append(f"ranking: {e}")

    def get_camp_data(self, camp_name: str, location: str, max_reviews: int = 20) -> TripAdvisorData:
        """
        Search for camp and parse its reviews

        Args:
            camp_name: Name of the camp
            location: Location (city/country)
            max_reviews: Maximum reviews to collect

        Returns:
            TripAdvisorData with all extracted information
        """
        # First search for the camp
        url = self.search_camp(camp_name, location)

        if not url:
            return TripAdvisorData(found=False, errors=["Camp not found on TripAdvisor"])

        # Then parse reviews
        return self.parse_reviews(url, max_reviews)
