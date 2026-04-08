#!/usr/bin/env python3
"""
Batch test parser on multiple camps
"""
import os
import sys
import json
import time
from pathlib import Path
from dataclasses import asdict
from datetime import datetime

# Setup paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Config (set via environment variables — never commit secrets)
EVOMI_API_KEY = os.getenv("EVOMI_API_KEY", "")
EVOMI_API_URL = os.getenv("EVOMI_API_URL", "https://scrape.evomi.com/api/v1/scraper/realtime")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Test camps - 5 diverse camps
TEST_CAMPS = [
    {"name": "Baleal Surf Camp", "url": "https://www.balealsurfcamp.com/", "country": "Portugal"},
    {"name": "Lapoint Ericeira", "url": "https://laneezericeira.com/", "country": "Portugal"},
    {"name": "Surf Makers Bali", "url": "https://surfmakerscamp.com/surfcampbali", "country": "Bali"},
    {"name": "Zen Surf Morocco", "url": "https://www.zensurfmorocco.com", "country": "Morocco"},
    {"name": "Iguana Surf", "url": "https://iguanasurf.net/", "country": "Costa Rica"},
]


def is_blocked_response(html: str) -> bool:
    """Check if the response is a blocked/403 page"""
    if not html:
        return True

    # Check for common block indicators
    block_indicators = [
        '<title>403',
        '<title>Access Denied',
        '<title>Forbidden',
        '<title>Blocked',
        'Access Denied',
        '403 Forbidden',
        'You have been blocked',
        'Please verify you are a human',
        'Checking your browser',
        'cf-browser-verification',
        'Just a moment...',  # Cloudflare
    ]

    html_lower = html[:5000].lower()  # Check first 5000 chars
    for indicator in block_indicators:
        if indicator.lower() in html_lower:
            return True

    # Also check if content is too small (likely error page)
    if len(html) < 1000:
        return True

    return False


def test_camp(camp_info: dict, use_direct_fallback: bool = True) -> dict:
    """Test parser on a single camp with fallback support"""
    from scraper.utils.evomi_client import EvomiClient
    from scraper.utils.direct_client import DirectClient
    from scraper.parsers.camp_parser import CampParser

    url = camp_info["url"]
    name = camp_info["name"]

    print(f"\n{'='*60}")
    print(f"PARSING: {name}")
    print(f"URL: {url}")
    print(f"{'='*60}")

    # Initialize clients
    evomi = EvomiClient(EVOMI_API_KEY, EVOMI_API_URL)
    direct = DirectClient()

    result = {
        "input": camp_info,
        "success": False,
        "error": None,
        "client_used": None,
        "data": None,
        "parse_time": None
    }

    start_time = time.time()
    html = None

    # Try Evomi first
    print("\n[1] Trying Evomi client...")
    response = evomi.fetch(url)
    use_direct_for_crawl = False

    if response.success:
        # Check if response is actually blocked
        if is_blocked_response(response.html):
            print(f"    ⚠ Evomi returned blocked page, trying direct...")
            if use_direct_fallback:
                direct_resp = direct.fetch(url)
                if direct_resp.success and not is_blocked_response(direct_resp.html):
                    print(f"    ✓ Direct success: {len(direct_resp.html)} chars")
                    result["client_used"] = "direct"
                    html = direct_resp.html
                    use_direct_for_crawl = True
                else:
                    print(f"    ✗ Direct also blocked or failed")
                    result["error"] = "Both clients returned blocked content"
                    return result
            else:
                result["error"] = "Evomi returned blocked page"
                return result
        else:
            print(f"    ✓ Evomi success: {len(response.html)} chars")
            result["client_used"] = "evomi"
            html = response.html
    elif use_direct_fallback:
        print(f"    ✗ Evomi failed: {response.error}")
        print("    Trying direct client fallback...")
        direct_resp = direct.fetch(url)
        if direct_resp.success:
            print(f"    ✓ Direct success: {len(direct_resp.html)} chars")
            result["client_used"] = "direct"
            html = direct_resp.html
            use_direct_for_crawl = True
        else:
            print(f"    ✗ Direct also failed: {direct_resp.error}")
            result["error"] = f"Both clients failed. Evomi: {response.error}, Direct: {direct_resp.error}"
            return result
    else:
        result["error"] = f"Evomi failed: {response.error}"
        return result

    # Create parser with appropriate client
    if use_direct_for_crawl:
        # Create a wrapper that makes direct client look like evomi client
        class DirectClientWrapper:
            def __init__(self, client):
                self.client = client

            def fetch(self, url, render_js=True):
                resp = self.client.fetch(url)
                # Convert to evomi-like response
                class FakeResponse:
                    def __init__(self, r):
                        self.success = r.success
                        self.html = r.html
                        self.error = r.error
                return FakeResponse(resp)

        parser = CampParser(
            anthropic_api_key=ANTHROPIC_API_KEY,
            use_ai=True,
            max_pages=6,
            evomi_client=DirectClientWrapper(direct)
        )
    else:
        parser = CampParser(
            anthropic_api_key=ANTHROPIC_API_KEY,
            use_ai=True,
            max_pages=6,
            evomi_client=evomi
        )

    # Crawl subpages
    print("\n[2] Crawling subpages...")
    try:
        data = parser.crawl_and_parse(html, url)
        result["success"] = True
        result["data"] = asdict(data)
        result["parse_time"] = round(time.time() - start_time, 2)

        # Print summary
        print(f"\n[3] Results:")
        print(f"    Name: {data.name}")
        print(f"    Description: {len(data.description)} chars")
        print(f"    Packages: {len(data.packages)}")
        print(f"    Instructors: {len(data.instructors)}")
        print(f"    Activities: {len(data.activities)}")
        print(f"    Amenities: {data.amenities}")
        print(f"    Images: {len(data.image_urls)}")
        print(f"    Pages crawled: {len(data.pages_crawled)}")
        print(f"    Time: {result['parse_time']}s")

    except Exception as e:
        print(f"    ✗ Parse error: {e}")
        result["error"] = str(e)
        import traceback
        traceback.print_exc()

    return result


def run_batch_test():
    """Run tests on all camps"""
    print("="*60)
    print("BATCH PARSER TEST")
    print(f"Testing {len(TEST_CAMPS)} camps")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    results = []

    for i, camp in enumerate(TEST_CAMPS, 1):
        print(f"\n[{i}/{len(TEST_CAMPS)}] Processing {camp['name']}...")
        result = test_camp(camp)
        results.append(result)

        # Brief pause between camps
        if i < len(TEST_CAMPS):
            time.sleep(2)

    # Summary
    print("\n" + "="*60)
    print("BATCH TEST SUMMARY")
    print("="*60)

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\nSuccessful: {len(successful)}/{len(results)}")
    print(f"Failed: {len(failed)}/{len(results)}")

    if successful:
        print("\n✓ Successful camps:")
        for r in successful:
            d = r["data"]
            print(f"  - {r['input']['name']}: {len(d.get('packages', []))} packages, "
                  f"{len(d.get('activities', []))} activities, "
                  f"{len(d.get('image_urls', []))} images ({r['client_used']})")

    if failed:
        print("\n✗ Failed camps:")
        for r in failed:
            print(f"  - {r['input']['name']}: {r['error']}")

    # Save results
    output_file = BACKEND_DIR / "batch_test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "test_date": datetime.now().isoformat(),
            "total_camps": len(TEST_CAMPS),
            "successful": len(successful),
            "failed": len(failed),
            "results": results
        }, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✓ Results saved to: {output_file}")

    return results


if __name__ == '__main__':
    run_batch_test()
