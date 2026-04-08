#!/usr/bin/env python3
"""
Test parser on DreamSea using direct HTTP client (bypasses Evomi blocking)
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


def test_dreamsea():
    """Test parser on DreamSea using direct client"""
    from scraper.utils.direct_client import DirectClient
    from scraper.parsers.camp_parser import CampParser

    url = "https://www.dreamsea.com/"
    output_file = BACKEND_DIR / "dreamsea_parsed.json"

    print(f"Testing parser on: {url}")
    print("Using: Direct HTTP client (curl)")
    print("=" * 60)

    # Initialize direct client
    direct = DirectClient()

    # Initialize parser with direct client instead of evomi
    parser = CampParser(
        anthropic_api_key=ANTHROPIC_API_KEY,
        use_ai=True,
        max_pages=8,
        evomi_client=None  # Will inject direct client
    )

    # Monkey-patch the fetch method to use direct client
    def fetch_with_direct(url):
        resp = direct.fetch(url)
        # Convert DirectResponse to match EvomiResponse interface
        class FakeEvomiResponse:
            def __init__(self, resp):
                self.success = resp.success
                self.html = resp.html
                self.error = resp.error
        return FakeEvomiResponse(resp)

    # Fetch homepage
    print("\n[1] Fetching homepage with direct client...")
    response = direct.fetch(url)

    if not response.success:
        print(f"ERROR: Failed to fetch {url}: {response.error}")
        return None

    print(f"    Homepage fetched: {len(response.html)} chars")

    # For subpage crawling, we need to patch the parser
    # Let's create a custom crawler
    print("\n[2] Crawling subpages...")

    # Get links from homepage
    from scraper.parsers.camp_parser import CampParser
    import re
    from urllib.parse import urljoin, urlparse

    # Find all internal links
    base_domain = urlparse(url).netloc
    link_pattern = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)

    all_links = link_pattern.findall(response.html)
    internal_links = set()

    for link in all_links:
        full_url = urljoin(url, link)
        parsed = urlparse(full_url)
        if parsed.netloc == base_domain or parsed.netloc == '':
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if clean_url.endswith('/'):
                clean_url = clean_url[:-1]
            internal_links.add(clean_url + '/')

    # Prioritize important pages
    priority_keywords = ['price', 'surf', 'about', 'contact', 'team', 'camp', 'accommodation', 'room']
    priority_pages = []
    other_pages = []

    for link in internal_links:
        if any(kw in link.lower() for kw in priority_keywords):
            priority_pages.append(link)
        else:
            other_pages.append(link)

    pages_to_crawl = priority_pages[:6] + other_pages[:2]
    print(f"    Found {len(internal_links)} internal links")
    print(f"    Will crawl {len(pages_to_crawl)} priority pages:")
    for p in pages_to_crawl:
        print(f"      - {p}")

    # Collect all HTML
    all_html = {"homepage": response.html}
    pages_crawled = [url]

    for page_url in pages_to_crawl:
        if page_url == url or page_url == url.rstrip('/'):
            continue
        print(f"\n    Fetching: {page_url}")
        page_resp = direct.fetch(page_url)
        if page_resp.success and page_resp.html:
            all_html[page_url] = page_resp.html
            pages_crawled.append(page_url)
            print(f"      ✓ {len(page_resp.html)} chars")
        else:
            print(f"      ✗ Failed: {page_resp.error}")

    # Now parse all collected HTML
    print("\n[3] Parsing with AI...")

    # Combine all HTML for parsing
    combined_html = "\n\n<!-- PAGE BREAK -->\n\n".join(all_html.values())
    print(f"    Total HTML: {len(combined_html)} chars from {len(all_html)} pages")

    # Use parser on combined content
    from scraper.parsers.camp_parser import CampData

    # Create fake evomi response for the parser
    class FakeResponse:
        success = True
        html = combined_html
        error = None

    # Parse using the internal method
    data = parser.parse(combined_html, url)
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
        print(f"  - {room.get('name', 'N/A')}: {room.get('price', 'N/A')}")

    print(f"\n--- TEAM ---")
    print(f"Instructors: {len(data.instructors)}")
    for inst in data.instructors[:5]:
        print(f"  - {inst.get('name', 'N/A')}: {inst.get('bio', '?')}")

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
    test_dreamsea()
