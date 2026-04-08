#!/usr/bin/env python3
"""
Main scraper script for surf camps
Parses camp websites, TripAdvisor, and saves to database

Usage:
    cd /Users/surfg/projects/surfcamp/backend
    python -m scraper.run_scraper [options]

Options:
    --test          Only process first 2 camps (test mode)
    --skip-ta       Skip TripAdvisor scraping
    --skip-images   Skip image downloading
    --camp NAME     Process only camp with this name
    --start N       Start from camp number N (0-indexed)
"""

import os
import sys
import re
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration (set via environment variables — never commit secrets)
EVOMI_API_KEY = os.getenv("EVOMI_API_KEY", "")
EVOMI_API_URL = os.getenv("EVOMI_API_URL", "https://scrape.evomi.com/api/v1/scraper/realtime")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BACKEND_DIR / 'media'
CAMPS_FILE = BACKEND_DIR.parent / 'surf_camps.ru'

# Delays between requests (seconds)
DELAY_BETWEEN_CAMPS = 3
DELAY_BETWEEN_REQUESTS = 2


class SurfCampScraper:
    """
    Main scraper orchestrator
    """

    def __init__(
        self,
        skip_tripadvisor: bool = False,
        skip_images: bool = False,
        max_images: int = 10,
        crawl_subpages: bool = True,  # NEW: Enable multi-page crawling
        max_subpages: int = 6         # NEW: Max subpages per camp
    ):
        from scraper.utils.evomi_client import EvomiClient
        from scraper.utils.image_downloader import ImageDownloader
        from scraper.parsers.camp_parser import CampParser
        from scraper.parsers.tripadvisor_parser import TripAdvisorParser
        from scraper.utils.db_saver import DatabaseSaver

        self.skip_tripadvisor = skip_tripadvisor
        self.skip_images = skip_images
        self.max_images = max_images
        self.crawl_subpages = crawl_subpages
        self.max_subpages = max_subpages

        # Initialize components
        logger.info("Initializing scraper components...")

        self.evomi = EvomiClient(EVOMI_API_KEY, EVOMI_API_URL)
        # Pass evomi client to parser for subpage crawling
        self.camp_parser = CampParser(
            ANTHROPIC_API_KEY,
            use_ai=True,
            max_pages=max_subpages,
            evomi_client=self.evomi if crawl_subpages else None
        )
        self.tripadvisor = TripAdvisorParser(self.evomi) if not skip_tripadvisor else None
        self.image_downloader = ImageDownloader(str(MEDIA_DIR)) if not skip_images else None
        self.db_saver = DatabaseSaver(str(MEDIA_DIR))

        # Stats
        self.stats = {
            'total_camps': 0,
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

    def parse_camps_file(self, filepath: Path) -> list:
        """
        Parse surf_camps.ru file to extract camp entries

        Returns list of dicts with: name, url, location, country
        """
        camps = []
        current_country = None

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Detect country headers
            if line in ['PORTUGAL', 'SPAIN', 'INDONESIA', 'COSTA RICA', 'MOROCCO', 'SRI LANKA', 'RUSSIA']:
                current_country = line.title()
                i += 1
                continue

            # Detect camp entry (name - location format)
            if ' - ' in line and current_country:
                parts = line.split(' - ', 1)
                name = parts[0].strip()
                location = parts[1].strip() if len(parts) > 1 else ''

                # Next line should be URL
                if i + 1 < len(lines):
                    url_line = lines[i + 1].strip()
                    if url_line.startswith('http'):
                        # Check if it's not marked as error
                        status_line = lines[i + 2].strip() if i + 2 < len(lines) else ''

                        if 'SSL error' in status_line or 'n/a' in status_line:
                            logger.info(f"Skipping {name} - SSL/error status")
                            i += 3
                            continue

                        camps.append({
                            'name': name,
                            'url': url_line,
                            'location': location,
                            'country': current_country
                        })
                        i += 2
                        continue

            i += 1

        return camps

    def process_camp(self, camp_entry: dict) -> bool:
        """
        Process a single camp: scrape website, TripAdvisor, download images, save to DB

        Args:
            camp_entry: Dict with name, url, location, country

        Returns:
            True if successful, False otherwise
        """
        name = camp_entry['name']
        url = camp_entry['url']
        location = camp_entry['location']
        country = camp_entry['country']

        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {name}")
        logger.info(f"URL: {url}")
        logger.info(f"Location: {location}, {country}")
        logger.info(f"{'='*60}")

        try:
            # 1. Fetch and parse camp website (with optional subpage crawling)
            logger.info("[1/4] Fetching camp website...")
            response = self.evomi.fetch(url)

            if not response.success:
                logger.warning(f"Failed to fetch {url}: {response.error}")
                # Continue anyway - we can still get TripAdvisor data
                camp_data = None
            else:
                # Use multi-page crawling if enabled
                if self.crawl_subpages:
                    logger.info("[1/4] Crawling website (homepage + subpages)...")
                    camp_data = self.camp_parser.crawl_and_parse(response.html, url)
                    logger.info(f"Parsed {len(camp_data.pages_crawled)} pages: {camp_data.name}")
                    logger.info(f"  - Images: {len(camp_data.image_urls)}")
                    logger.info(f"  - Instructors: {len(camp_data.instructors)}")
                    logger.info(f"  - Activities: {len(camp_data.activities)}")
                    logger.info(f"  - Packages: {len(camp_data.packages)}")
                else:
                    camp_data = self.camp_parser.parse(response.html, url)
                    logger.info(f"Parsed: {camp_data.name}, {len(camp_data.image_urls)} images found")

            time.sleep(DELAY_BETWEEN_REQUESTS)

            # 2. Fetch TripAdvisor data
            tripadvisor_data = None
            if not self.skip_tripadvisor:
                logger.info("[2/4] Searching TripAdvisor...")
                try:
                    tripadvisor_data = self.tripadvisor.get_camp_data(
                        name,
                        f"{location} {country}",
                        max_reviews=20
                    )
                    if tripadvisor_data.found:
                        logger.info(f"TripAdvisor: rating={tripadvisor_data.rating}, {len(tripadvisor_data.reviews)} reviews")
                    else:
                        logger.info("Camp not found on TripAdvisor")
                except Exception as e:
                    logger.warning(f"TripAdvisor error: {e}")

                time.sleep(DELAY_BETWEEN_REQUESTS)

            # 3. Download images
            image_paths = []
            if not self.skip_images and camp_data and camp_data.image_urls:
                logger.info(f"[3/4] Downloading images ({min(len(camp_data.image_urls), self.max_images)} max)...")
                try:
                    from django.utils.text import slugify
                    camp_slug = slugify(f"{name}-{location}")[:50]
                    image_paths = self.image_downloader.download_images(
                        camp_data.image_urls,
                        camp_slug,
                        self.max_images
                    )
                    logger.info(f"Downloaded {len(image_paths)} images")
                except Exception as e:
                    logger.warning(f"Image download error: {e}")
            else:
                logger.info("[3/4] Skipping image download")

            # 4. Save to database
            logger.info("[4/4] Saving to database...")

            # Prepare data for DB
            db_camp_data = {}
            if camp_data:
                # Use parsed name only if valid, otherwise use name from file
                parsed_name = camp_data.name
                # Check for invalid names (errors, blocked pages, etc)
                invalid_names = ['403', '404', '500', 'forbidden', 'not found', 'error', 'access denied', 'blocked']
                is_invalid = (
                    not parsed_name or
                    len(parsed_name) < 3 or
                    parsed_name.isdigit() or
                    any(inv in parsed_name.lower() for inv in invalid_names)
                )
                if is_invalid:
                    parsed_name = name
                    logger.info(f"Using name from file: {name}")

                db_camp_data = {
                    'name': parsed_name,
                    'description': camp_data.description,
                    'short_description': camp_data.short_description,
                    'history': camp_data.history,
                    'address': camp_data.address,
                    'price_per_night': camp_data.price_per_night,
                    'price_per_lesson': camp_data.price_per_lesson,
                    'email': camp_data.email,
                    'phone': camp_data.phone,
                    'whatsapp': camp_data.whatsapp,
                    'instagram': camp_data.instagram,
                    'website': camp_data.website or url,
                    'skill_levels': camp_data.skill_levels,
                    'amenities': camp_data.amenities,
                    'has_pool': camp_data.has_pool,
                    'has_restaurant': camp_data.has_restaurant,
                    'has_yoga': camp_data.has_yoga,
                    'instructors': camp_data.instructors,
                    'activities': camp_data.activities,
                }
            else:
                db_camp_data = {
                    'name': name,
                    'website': url,
                }

            db_tripadvisor_data = None
            if tripadvisor_data and tripadvisor_data.found:
                db_tripadvisor_data = {
                    'rating': tripadvisor_data.rating,
                    'reviews_count': tripadvisor_data.reviews_count,
                    'reviews': [
                        {
                            'author_name': r.author_name,
                            'author_country': r.author_country,
                            'rating': r.rating,
                            'title': r.title,
                            'text': r.text,
                            'visit_date': r.visit_date,
                        }
                        for r in tripadvisor_data.reviews
                    ]
                }

            saved_camp = self.db_saver.save_camp(
                db_camp_data,
                db_tripadvisor_data,
                image_paths,
                location,
                country
            )

            if saved_camp:
                logger.info(f"SUCCESS: Saved {saved_camp.name} (ID: {saved_camp.id})")
                self.stats['success'] += 1
                return True
            else:
                logger.error(f"FAILED: Could not save {name}")
                self.stats['failed'] += 1
                return False

        except Exception as e:
            logger.error(f"ERROR processing {name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['failed'] += 1
            self.stats['errors'].append(f"{name}: {e}")
            return False

    def run(
        self,
        test_mode: bool = False,
        specific_camp: str = None,
        start_from: int = 0
    ):
        """
        Run the scraper

        Args:
            test_mode: Only process first 2 camps
            specific_camp: Only process camp with this name
            start_from: Start from camp number N
        """
        logger.info("="*60)
        logger.info("SURF CAMP SCRAPER")
        logger.info("="*60)

        # Parse camps file
        logger.info(f"Reading camps from: {CAMPS_FILE}")
        camps = self.parse_camps_file(CAMPS_FILE)
        self.stats['total_camps'] = len(camps)
        logger.info(f"Found {len(camps)} camps to process")

        # Filter if needed
        if specific_camp:
            camps = [c for c in camps if specific_camp.lower() in c['name'].lower()]
            logger.info(f"Filtered to {len(camps)} camps matching '{specific_camp}'")

        if start_from > 0:
            camps = camps[start_from:]
            logger.info(f"Starting from camp #{start_from}")

        if test_mode:
            camps = camps[:2]
            logger.info("TEST MODE: Processing only first 2 camps")

        # Process each camp
        for i, camp in enumerate(camps):
            logger.info(f"\n[{i+1}/{len(camps)}] Processing: {camp['name']}")

            try:
                self.process_camp(camp)
                self.stats['processed'] += 1
            except KeyboardInterrupt:
                logger.info("\nInterrupted by user")
                break
            except Exception as e:
                logger.error(f"Unhandled error: {e}")
                self.stats['errors'].append(str(e))
                continue  # Continue with next camp

            # Delay between camps
            if i < len(camps) - 1:
                logger.info(f"Waiting {DELAY_BETWEEN_CAMPS}s before next camp...")
                time.sleep(DELAY_BETWEEN_CAMPS)

        # Print final stats
        self._print_stats()

    def _print_stats(self):
        """Print final statistics"""
        logger.info("\n" + "="*60)
        logger.info("SCRAPING COMPLETE")
        logger.info("="*60)

        logger.info(f"Total camps in file: {self.stats['total_camps']}")
        logger.info(f"Processed: {self.stats['processed']}")
        logger.info(f"Success: {self.stats['success']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")

        logger.info("\nEvomi API stats:")
        evomi_stats = self.evomi.get_stats()
        logger.info(f"  Requests: {evomi_stats['total_requests']}")
        logger.info(f"  Failed: {evomi_stats['failed_requests']}")
        logger.info(f"  Credits used: {evomi_stats['total_credits_used']}")

        if not self.skip_images:
            logger.info("\nImage downloader stats:")
            img_stats = self.image_downloader.get_stats()
            logger.info(f"  Downloaded: {img_stats['downloaded']}")
            logger.info(f"  Failed: {img_stats['failed']}")

        logger.info("\nDatabase saver stats:")
        db_stats = self.db_saver.get_stats()
        logger.info(f"  Camps created: {db_stats['camps_created']}")
        logger.info(f"  Camps updated: {db_stats['camps_updated']}")
        logger.info(f"  Images saved: {db_stats['images_saved']}")
        logger.info(f"  Reviews saved: {db_stats['reviews_saved']}")
        logger.info(f"  Instructors saved: {db_stats['instructors_saved']}")
        logger.info(f"  Activities saved: {db_stats['activities_saved']}")

        if self.stats['errors']:
            logger.info(f"\nErrors ({len(self.stats['errors'])}):")
            for err in self.stats['errors'][:10]:
                logger.info(f"  - {err}")

        # Save stats to file
        stats_file = BACKEND_DIR / f'scraper_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(stats_file, 'w') as f:
            json.dump({
                'scraper': self.stats,
                'evomi': evomi_stats,
                'images': self.image_downloader.get_stats() if not self.skip_images else {},
                'database': db_stats
            }, f, indent=2)
        logger.info(f"\nStats saved to: {stats_file}")


def main():
    parser = argparse.ArgumentParser(description='Surf Camp Scraper v2.0')
    parser.add_argument('--test', action='store_true', help='Test mode - only 2 camps')
    parser.add_argument('--skip-ta', action='store_true', help='Skip TripAdvisor')
    parser.add_argument('--skip-images', action='store_true', help='Skip image download')
    parser.add_argument('--camp', type=str, help='Process only specific camp')
    parser.add_argument('--start', type=int, default=0, help='Start from camp N')
    parser.add_argument('--max-images', type=int, default=10, help='Max images per camp')
    parser.add_argument('--no-crawl', action='store_true', help='Disable subpage crawling (homepage only)')
    parser.add_argument('--max-subpages', type=int, default=6, help='Max subpages to crawl per camp')

    args = parser.parse_args()

    scraper = SurfCampScraper(
        skip_tripadvisor=args.skip_ta,
        skip_images=args.skip_images,
        max_images=args.max_images,
        crawl_subpages=not args.no_crawl,
        max_subpages=args.max_subpages
    )

    scraper.run(
        test_mode=args.test,
        specific_camp=args.camp,
        start_from=args.start
    )


if __name__ == '__main__':
    main()
