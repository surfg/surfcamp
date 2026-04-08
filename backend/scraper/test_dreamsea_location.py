#!/usr/bin/env python3
"""
Test parser on a specific DreamSea location
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
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")


def test_location(location_url: str, output_name: str):
    """Test parser on a specific DreamSea location"""
    from scraper.utils.direct_client import DirectClient
    from scraper.parsers.camp_parser import CampParser

    output_file = BACKEND_DIR / f"{output_name}_parsed.json"

    print(f"Testing parser on: {location_url}")
    print("Using: Direct HTTP client (curl)")
    print("=" * 60)

    # Initialize
    direct = DirectClient()
    parser = CampParser(
        anthropic_api_key=ANTHROPIC_API_KEY,
        use_ai=True,
        max_pages=4,
        evomi_client=None
    )

    # Fetch main location page
    print("\n[1] Fetching location page...")
    response = direct.fetch(location_url)

    if not response.success:
        print(f"ERROR: Failed to fetch {location_url}: {response.error}")
        return None

    print(f"    Page fetched: {len(response.html)} chars")

    # Also fetch accommodations if it's a specific location
    pages_crawled = [location_url]
    all_html = [response.html]

    # Try to get the accommodations page for this location
    location_slug = location_url.rstrip('/').split('/')[-1]
    accommodations_urls = [
        f"https://www.dreamsea.com/accommodations/?location={location_slug}",
        "https://www.dreamsea.com/accommodations/"
    ]

    print("\n[2] Fetching additional pages...")
    for acc_url in accommodations_urls[:1]:
        print(f"    Fetching: {acc_url}")
        acc_resp = direct.fetch(acc_url)
        if acc_resp.success:
            all_html.append(acc_resp.html)
            pages_crawled.append(acc_url)
            print(f"      ✓ {len(acc_resp.html)} chars")

    # Combine HTML
    combined_html = "\n\n<!-- PAGE BREAK -->\n\n".join(all_html)
    print(f"\n[3] Parsing with AI...")
    print(f"    Total HTML: {len(combined_html)} chars from {len(all_html)} pages")

    # Parse
    data = parser.parse(combined_html, location_url)
    data.pages_crawled = pages_crawled

    # Convert to dict
    result = asdict(data)

    # Print summary
    print("\n" + "=" * 60)
    print("PARSING RESULTS")
    print("=" * 60)

    print(f"\nName: {data.name}")
    print(f"Short description: {data.short_description[:100]}..." if data.short_description else "Short description: -")
    print(f"Description length: {len(data.description)} chars")
    print(f"Address: {data.address}")

    print(f"\n--- PRICING ---")
    print(f"Price per night: {data.price_per_night}")
    print(f"Price per lesson: {data.price_per_lesson}")
    print(f"Packages: {len(data.packages)}")
    for pkg in data.packages[:5]:
        print(f"  - {pkg.get('name', 'N/A')}: ${pkg.get('price', 'N/A')} ({pkg.get('duration', 'N/A')})")

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
        print(f"  - {room.get('name', 'N/A')}: ${room.get('price', 'N/A')}")

    print(f"\n--- TEAM ---")
    print(f"Instructors: {len(data.instructors)}")
    for inst in data.instructors[:5]:
        print(f"  - {inst.get('name', 'N/A')}: {inst.get('bio', '')[:50]}")

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

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✓ Results saved to: {output_file}")

    return result


if __name__ == '__main__':
    # DreamSea locations
    locations = {
        'bali': 'https://www.dreamsea.com/bali-uluwatu/',
        'costarica': 'https://www.dreamsea.com/costarica-avellanas/',
        'portugal': 'https://www.dreamsea.com/portugal-alentejo/',
        'srilanka': 'https://www.dreamsea.com/srilanka-ahangama/',
    }

    import argparse
    parser = argparse.ArgumentParser(description='Parse DreamSea location')
    parser.add_argument('location', choices=list(locations.keys()), help='Location to parse')

    args = parser.parse_args()
    test_location(locations[args.location], f"dreamsea_{args.location}")
