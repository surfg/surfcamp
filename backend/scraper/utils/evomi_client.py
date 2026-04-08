"""
Evomi API Client with retry logic and error handling
"""
import requests
import time
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class EvomiResponse:
    """Response from Evomi API"""
    success: bool
    html: Optional[str] = None
    error: Optional[str] = None
    credits_used: int = 0
    status_code: int = 0


class EvomiClient:
    """
    Client for Evomi Scraper API with retry logic
    """

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://scrape.evomi.com/api/v1/scraper/realtime",
        max_retries: int = 3,
        retry_delay: float = 2.0,
        timeout: int = 60
    ):
        self.api_key = api_key
        self.api_url = api_url
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.total_credits_used = 0
        self.total_requests = 0
        self.failed_requests = 0

    def fetch(self, url: str, render_js: bool = True) -> EvomiResponse:
        """
        Fetch URL via Evomi API with retry logic

        Args:
            url: URL to fetch
            render_js: Whether to render JavaScript (default True)

        Returns:
            EvomiResponse with HTML content or error
        """
        payload = {
            "url": url,
            "render_js": render_js
        }

        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[Evomi] Fetching {url} (attempt {attempt}/{self.max_retries})")

                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=self.timeout
                )

                self.total_requests += 1

                if response.status_code == 200:
                    # Try to parse as JSON first
                    try:
                        data = response.json()
                        html = data.get('html', response.text)
                        credits = data.get('credits_used', 1)
                    except:
                        html = response.text
                        credits = 1

                    self.total_credits_used += credits

                    logger.info(f"[Evomi] Success: {url} ({len(html)} chars, {credits} credits)")

                    return EvomiResponse(
                        success=True,
                        html=html,
                        credits_used=credits,
                        status_code=200
                    )

                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = self.retry_delay * attempt * 2
                    logger.warning(f"[Evomi] Rate limited, waiting {wait_time}s...")
                    time.sleep(wait_time)
                    last_error = "Rate limited"

                elif response.status_code >= 500:
                    # Server error - retry
                    logger.warning(f"[Evomi] Server error {response.status_code}, retrying...")
                    time.sleep(self.retry_delay * attempt)
                    last_error = f"Server error: {response.status_code}"

                else:
                    # Client error - don't retry
                    error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                    logger.error(f"[Evomi] Client error: {error_msg}")
                    self.failed_requests += 1

                    return EvomiResponse(
                        success=False,
                        error=error_msg,
                        status_code=response.status_code
                    )

            except requests.Timeout:
                logger.warning(f"[Evomi] Timeout for {url}, retrying...")
                last_error = "Timeout"
                time.sleep(self.retry_delay)

            except requests.RequestException as e:
                logger.warning(f"[Evomi] Request error: {e}, retrying...")
                last_error = str(e)
                time.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"[Evomi] Unexpected error: {e}")
                last_error = str(e)
                break

        # All retries failed
        self.failed_requests += 1
        logger.error(f"[Evomi] All retries failed for {url}: {last_error}")

        return EvomiResponse(
            success=False,
            error=f"All {self.max_retries} retries failed: {last_error}"
        )

    def get_stats(self) -> dict:
        """Get client statistics"""
        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.total_requests - self.failed_requests) / max(self.total_requests, 1) * 100,
            "total_credits_used": self.total_credits_used
        }
