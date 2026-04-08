#!/usr/bin/env python3
"""
Test the multi-page parser on a single camp
"""
import os
import sys
import json
from pathlib import Path
from dataclasses import asdict

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Config (set via environment variables — never commit secrets)
EVOMI_API_KEY = os.getenv("EVOMI_API_KEY", "")
EVOMI_API_URL = os.getenv("EVOMI_API_URL", "https://scrape.evomi.com/api/v1/scraper/realtime")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

def test_parser(url: str, output_file: str = None):
    """Test parser on a single URL"""
    from scraper.utils.evomi_client import EvomiClient
    from scraper.parsers.camp_parser import CampParser

    print(f"Testing parser on: {url}")
    print("=" * 60)

    # Initialize
    evomi = EvomiClient(EVOMI_API_KEY, EVOMI_API_URL)
    parser = CampParser(
        anthropic_api_key=ANTHROPIC_API_KEY,
        use_ai=True,
        max_pages=8,
        evomi_client=evomi
    )

    # Fetch homepage
    print("\n[1] Fetching homepage...")
    response = evomi.fetch(url)

    if not response.success:
        print(f"ERROR: Failed to fetch {url}: {response.error}")
        return None

    print(f"    Homepage fetched: {len(response.html)} chars")

    # Parse with multi-page crawling
    print("\n[2] Crawling and parsing...")
    data = parser.crawl_and_parse(response.html, url)

    # Convert to dict
    result = asdict(data)

    # Print summary
    print("\n" + "=" * 60)
    print("PARSING RESULTS")
    print("=" * 60)

    print(f"\nName: {data.name}")
    print(f"Short description: {data.short_description[:100]}..." if data.short_description else "Short description: -")
    print(f"Description length: {len(data.description)} chars")
    print(f"History: {data.history[:100]}..." if data.history else "History: -")
    print(f"Address: {data.address}")

    print(f"\n--- PRICING ---")
    print(f"Price per night: {data.price_per_night}")
    print(f"Price per lesson: {data.price_per_lesson}")
    print(f"Packages: {len(data.packages)}")
    for pkg in data.packages[:3]:
        print(f"  - {pkg.get('name', 'N/A')}: {pkg.get('price', 'N/A')} ({pkg.get('duration', 'N/A')})")

    print(f"\n--- CONTACTS ---")
    print(f"Email: {data.email}")
    print(f"Phone: {data.phone}")
    print(f"WhatsApp: {data.whatsapp}")
    print(f"Instagram: {data.instagram}")
    print(f"Facebook: {data.facebook}")
    print(f"Website: {data.website}")

    print(f"\n--- FEATURES ---")
    print(f"Skill levels: {data.skill_levels}")
    print(f"Amenities: {data.amenities}")
    print(f"Has pool: {data.has_pool}")
    print(f"Has restaurant: {data.has_restaurant}")
    print(f"Has yoga: {data.has_yoga}")

    print(f"\n--- ACCOMMODATION ---")
    print(f"Room types: {len(data.room_types)}")
    for room in data.room_types[:5]:
        print(f"  - {room.get('name', 'N/A')}: {room.get('price', 'N/A')} ({room.get('capacity', '?')} guests)")

    print(f"\n--- TEAM ---")
    print(f"Instructors: {len(data.instructors)}")
    for inst in data.instructors[:5]:
        print(f"  - {inst.get('name', 'N/A')}: {inst.get('experience_years', '?')} years, {inst.get('languages', [])}")

    print(f"\n--- ACTIVITIES ---")
    print(f"Activities: {len(data.activities)}")
    for act in data.activities[:5]:
        included = "included" if act.get('is_included') else f"${act.get('price', '?')}"
        print(f"  - {act.get('name', 'N/A')}: {included}")

    print(f"\n--- SURF ---")
    print(f"Surf spots: {data.surf_spots}")
    print(f"Board types: {data.board_types}")

    print(f"\n--- MEDIA ---")
    print(f"Images found: {len(data.image_urls)}")
    for img in data.image_urls[:5]:
        print(f"  - {img[:80]}...")

    print(f"\n--- META ---")
    print(f"Pages crawled: {len(data.pages_crawled)}")
    for page in data.pages_crawled:
        print(f"  - {page}")
    print(f"Parse errors: {data.parse_errors}")

    # Save to file
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n✓ Results saved to: {output_path}")

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Test multi-page parser')
    parser.add_argument('url', help='URL to parse')
    parser.add_argument('-o', '--output', help='Output JSON file', default='parser_test_result.json')

    args = parser.parse_args()

    test_parser(args.url, args.output)
