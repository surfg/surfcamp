"""
Scraper Configuration
"""
import os
from pathlib import Path

# API Keys (set via environment variables — never commit secrets)
EVOMI_API_KEY = os.getenv('EVOMI_API_KEY', '')
EVOMI_API_URL = os.getenv('EVOMI_API_URL', 'https://scrape.evomi.com/api/v1/scraper/realtime')

# Anthropic API for AI parsing
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

# Paths
BACKEND_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BACKEND_DIR / 'media'
CAMPS_FILE = BACKEND_DIR.parent / 'surf_camps.ru'

# Request settings
REQUEST_TIMEOUT = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2.0  # seconds

# Delays between requests (be respectful)
DELAY_BETWEEN_CAMPS = 3  # seconds
DELAY_BETWEEN_REQUESTS = 2  # seconds

# Image settings
MAX_IMAGES_PER_CAMP = 10
MAX_IMAGE_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.gif')

# TripAdvisor settings
MAX_REVIEWS_PER_CAMP = 20
