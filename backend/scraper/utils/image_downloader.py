"""
Image downloader with error handling
"""
import os
import hashlib
import requests
import logging
from typing import Optional, List
from urllib.parse import urljoin, urlparse
from pathlib import Path

logger = logging.getLogger(__name__)


class ImageDownloader:
    """
    Download and save images locally with error handling
    """

    def __init__(
        self,
        base_dir: str,
        timeout: int = 30,
        max_size_mb: int = 10,
        allowed_extensions: tuple = ('.jpg', '.jpeg', '.png', '.webp', '.gif')
    ):
        self.base_dir = Path(base_dir)
        self.timeout = timeout
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.allowed_extensions = allowed_extensions
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.downloaded_count = 0
        self.failed_count = 0

    def _get_extension(self, url: str, content_type: str = None) -> str:
        """Get file extension from URL or content type"""
        # Try from URL
        parsed = urlparse(url)
        path = parsed.path.lower()

        for ext in self.allowed_extensions:
            if path.endswith(ext):
                return ext

        # Try from content type
        if content_type:
            ct = content_type.lower()
            if 'jpeg' in ct or 'jpg' in ct:
                return '.jpg'
            elif 'png' in ct:
                return '.png'
            elif 'webp' in ct:
                return '.webp'
            elif 'gif' in ct:
                return '.gif'

        return '.jpg'  # Default

    def _generate_filename(self, url: str, camp_slug: str, index: int) -> str:
        """Generate unique filename for image"""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return f"{camp_slug}_{index:02d}_{url_hash}"

    def download_image(
        self,
        url: str,
        camp_slug: str,
        index: int = 0
    ) -> Optional[str]:
        """
        Download single image

        Args:
            url: Image URL
            camp_slug: Camp slug for directory/filename
            index: Image index

        Returns:
            Relative path to saved image or None on failure
        """
        # Skip data: URLs (inline SVG placeholders)
        if url.startswith('data:'):
            return None

        try:
            # Create camp directory
            camp_dir = self.base_dir / "camps" / camp_slug
            camp_dir.mkdir(parents=True, exist_ok=True)

            # Download image
            logger.info(f"[Image] Downloading: {url[:80]}...")

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout,
                stream=True
            )

            if response.status_code != 200:
                logger.warning(f"[Image] HTTP {response.status_code} for {url}")
                self.failed_count += 1
                return None

            # Check size
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > self.max_size_bytes:
                logger.warning(f"[Image] Too large ({content_length} bytes): {url}")
                self.failed_count += 1
                return None

            # Get extension
            content_type = response.headers.get('Content-Type', '')
            extension = self._get_extension(url, content_type)

            # Generate filename
            filename = self._generate_filename(url, camp_slug, index) + extension
            filepath = camp_dir / filename

            # Save image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Verify file was saved
            if filepath.exists() and filepath.stat().st_size > 0:
                self.downloaded_count += 1
                relative_path = f"camps/{camp_slug}/{filename}"
                logger.info(f"[Image] Saved: {relative_path}")
                return relative_path
            else:
                logger.warning(f"[Image] Empty file: {filepath}")
                self.failed_count += 1
                return None

        except requests.Timeout:
            logger.warning(f"[Image] Timeout: {url}")
            self.failed_count += 1
            return None

        except requests.RequestException as e:
            logger.warning(f"[Image] Request error: {e}")
            self.failed_count += 1
            return None

        except Exception as e:
            logger.error(f"[Image] Unexpected error downloading {url}: {e}")
            self.failed_count += 1
            return None

    def download_images(
        self,
        urls: List[str],
        camp_slug: str,
        max_images: int = 10
    ) -> List[str]:
        """
        Download multiple images

        Args:
            urls: List of image URLs
            camp_slug: Camp slug
            max_images: Maximum number of images to download

        Returns:
            List of relative paths to saved images
        """
        saved_paths = []
        unique_urls = list(dict.fromkeys(urls))  # Remove duplicates, preserve order

        for i, url in enumerate(unique_urls[:max_images]):
            path = self.download_image(url, camp_slug, i)
            if path:
                saved_paths.append(path)

        logger.info(f"[Image] Downloaded {len(saved_paths)}/{len(unique_urls[:max_images])} for {camp_slug}")
        return saved_paths

    def get_stats(self) -> dict:
        """Get downloader statistics"""
        return {
            "downloaded": self.downloaded_count,
            "failed": self.failed_count,
            "success_rate": self.downloaded_count / max(self.downloaded_count + self.failed_count, 1) * 100
        }
