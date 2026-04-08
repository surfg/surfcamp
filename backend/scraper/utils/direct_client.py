"""
Direct HTTP Client - fallback when Evomi is blocked
Uses simple requests without proxy to fetch static HTML sites
"""
import subprocess
import logging
import time
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DirectResponse:
    """Response from direct HTTP request"""
    success: bool
    html: Optional[str] = None
    error: Optional[str] = None
    status_code: int = 0


class DirectClient:
    """
    Direct HTTP client using curl as fallback for sites that block Evomi
    """

    def __init__(
        self,
        max_retries: int = 2,
        retry_delay: float = 1.0,
        timeout: int = 30
    ):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout
        # Use Windows user agent - some sites block Mac
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        )
        self.total_requests = 0
        self.failed_requests = 0

    def fetch(self, url: str) -> DirectResponse:
        """
        Fetch URL using curl

        Args:
            url: URL to fetch

        Returns:
            DirectResponse with HTML content or error
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[Direct] Fetching {url} (attempt {attempt}/{self.max_retries})")
                self.total_requests += 1

                # Use curl for reliable fetching
                result = subprocess.run(
                    [
                        'curl',
                        '-s',  # Silent
                        '-L',  # Follow redirects
                        '-A', self.user_agent,
                        '--max-time', str(self.timeout),
                        '-H', 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        '-H', 'Accept-Language: en-US,en;q=0.5',
                        '-w', '\n__STATUS_CODE__:%{http_code}',
                        url
                    ],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout + 5
                )

                output = result.stdout

                # Parse status code from output
                if '__STATUS_CODE__:' in output:
                    parts = output.rsplit('__STATUS_CODE__:', 1)
                    html = parts[0]
                    status_code = int(parts[1].strip())
                else:
                    html = output
                    status_code = 200 if output else 0

                if status_code == 200 and html:
                    logger.info(f"[Direct] Success: {url} ({len(html)} chars)")
                    return DirectResponse(
                        success=True,
                        html=html,
                        status_code=status_code
                    )
                elif status_code >= 400:
                    last_error = f"HTTP {status_code}"
                    logger.warning(f"[Direct] HTTP error {status_code} for {url}")
                else:
                    last_error = "Empty response"
                    logger.warning(f"[Direct] Empty response for {url}")

                time.sleep(self.retry_delay)

            except subprocess.TimeoutExpired:
                logger.warning(f"[Direct] Timeout for {url}")
                last_error = "Timeout"
                time.sleep(self.retry_delay)

            except Exception as e:
                logger.warning(f"[Direct] Error: {e}")
                last_error = str(e)
                time.sleep(self.retry_delay)

        self.failed_requests += 1
        logger.error(f"[Direct] All retries failed for {url}: {last_error}")

        return DirectResponse(
            success=False,
            error=f"Failed after {self.max_retries} attempts: {last_error}"
        )

    def get_stats(self) -> dict:
        """Get client statistics"""
        return {
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.total_requests - self.failed_requests) / max(self.total_requests, 1) * 100
        }
