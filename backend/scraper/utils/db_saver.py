"""
Database saver for scraped surf camp data
Integrates with Django models
"""
import os
import sys
import logging
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Add Django project to path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils.text import slugify
from django.core.files import File
from camps.models import (
    SurfCamp, CampImage, Instructor, Activity, Review,
    Country, Region, Amenity, BoardType
)

logger = logging.getLogger(__name__)


class DatabaseSaver:
    """
    Save scraped data to Django database
    """

    def __init__(self, media_root: str = None):
        """
        Args:
            media_root: Path to media directory
        """
        self.media_root = Path(media_root) if media_root else BACKEND_DIR / 'media'
        self.stats = {
            'camps_created': 0,
            'camps_updated': 0,
            'images_saved': 0,
            'reviews_saved': 0,
            'instructors_saved': 0,
            'activities_saved': 0,
            'errors': []
        }

    def find_or_create_region(self, location: str, country_name: str) -> Optional[Region]:
        """
        Find or create a region based on location string

        Args:
            location: Location string (e.g., "Peniche", "Bali, Canggu")
            country_name: Country name

        Returns:
            Region instance or None
        """
        try:
            # Try to find country
            country = Country.objects.filter(
                models.Q(name__icontains=country_name) |
                models.Q(name_en__icontains=country_name)
            ).first()

            if not country:
                logger.warning(f"[DB] Country not found: {country_name}")
                # Create country
                country = Country.objects.create(
                    name=country_name,
                    name_en=country_name,
                    code=country_name[:3].upper()
                )

            # Parse location for region name
            region_name = location.split(',')[0].strip() if ',' in location else location

            # Try to find region
            region = Region.objects.filter(
                country=country
            ).filter(
                models.Q(name__icontains=region_name) |
                models.Q(name_en__icontains=region_name)
            ).first()

            if not region:
                # Create region
                region = Region.objects.create(
                    country=country,
                    name=region_name,
                    name_en=region_name
                )
                logger.info(f"[DB] Created region: {region_name}, {country_name}")

            return region

        except Exception as e:
            logger.error(f"[DB] Error finding/creating region: {e}")
            self.stats['errors'].append(f"region: {e}")
            return None

    def save_camp(
        self,
        camp_data: dict,
        tripadvisor_data: dict = None,
        image_paths: List[str] = None,
        location: str = "",
        country: str = ""
    ) -> Optional[SurfCamp]:
        """
        Save or update a surf camp

        Args:
            camp_data: Data from CampParser
            tripadvisor_data: Data from TripAdvisorParser
            image_paths: List of local image paths
            location: Location string
            country: Country name

        Returns:
            SurfCamp instance or None
        """
        try:
            # Get region
            region = self.find_or_create_region(location, country)
            if not region:
                logger.error(f"[DB] Cannot save camp without region: {camp_data.get('name', 'Unknown')}")
                return None

            name = camp_data.get('name', 'Unknown Camp')
            slug = slugify(f"{name}-{location}")[:200]

            # Check if camp exists
            camp, created = SurfCamp.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'region': region,
                    'short_description': camp_data.get('short_description', '')[:300],
                    'description': camp_data.get('description', ''),
                    'address': camp_data.get('address', '')[:300],
                    'latitude': Decimal('0'),
                    'longitude': Decimal('0'),
                    'price_per_night': Decimal(str(camp_data.get('price_per_night') or 0)),
                }
            )

            if created:
                self.stats['camps_created'] += 1
                logger.info(f"[DB] Created camp: {name}")
            else:
                self.stats['camps_updated'] += 1
                logger.info(f"[DB] Updating camp: {name}")

            # Update fields
            if camp_data.get('description'):
                camp.description = camp_data['description']
            if camp_data.get('short_description'):
                camp.short_description = camp_data['short_description'][:300]
            if camp_data.get('history'):
                camp.history = camp_data['history']
            if camp_data.get('address'):
                camp.address = camp_data['address'][:300]

            # Prices
            if camp_data.get('price_per_night'):
                camp.price_per_night = Decimal(str(camp_data['price_per_night']))
            if camp_data.get('price_per_lesson'):
                camp.price_per_lesson = Decimal(str(camp_data['price_per_lesson']))

            # Contacts
            if camp_data.get('email'):
                camp.email = camp_data['email']
            if camp_data.get('phone'):
                camp.phone = camp_data['phone'][:30]
            if camp_data.get('whatsapp'):
                camp.whatsapp = camp_data['whatsapp'][:30]
            if camp_data.get('instagram'):
                camp.instagram = camp_data['instagram'][:100]
            if camp_data.get('website'):
                camp.website = camp_data['website']

            # Features
            if camp_data.get('skill_levels'):
                camp.skill_levels = camp_data['skill_levels']
            if 'has_pool' in camp_data:
                camp.has_pool = camp_data['has_pool']
            if 'has_restaurant' in camp_data:
                camp.has_restaurant = camp_data['has_restaurant']
            if 'has_yoga' in camp_data:
                camp.has_yoga = camp_data['has_yoga']

            # Rating from TripAdvisor
            if tripadvisor_data and tripadvisor_data.get('rating'):
                camp.rating = Decimal(str(tripadvisor_data['rating']))
                if tripadvisor_data.get('reviews_count'):
                    camp.reviews_count = tripadvisor_data['reviews_count']

            camp.save()

            # Save amenities
            if camp_data.get('amenities'):
                self._save_amenities(camp, camp_data['amenities'])

            # Save images
            if image_paths:
                self._save_images(camp, image_paths)

            # Save instructors
            if camp_data.get('instructors'):
                self._save_instructors(camp, camp_data['instructors'])

            # Save activities
            if camp_data.get('activities'):
                self._save_activities(camp, camp_data['activities'])

            # Save reviews from TripAdvisor
            if tripadvisor_data and tripadvisor_data.get('reviews'):
                self._save_reviews(camp, tripadvisor_data['reviews'])

            return camp

        except Exception as e:
            logger.error(f"[DB] Error saving camp: {e}")
            self.stats['errors'].append(f"camp: {e}")
            return None

    def _save_amenities(self, camp: SurfCamp, amenity_names: List[str]):
        """Save amenities for a camp"""
        try:
            for name in amenity_names:
                name_lower = name.lower().strip()

                # Try to find existing amenity
                amenity = Amenity.objects.filter(
                    models.Q(name__iexact=name_lower) |
                    models.Q(name_en__iexact=name_lower)
                ).first()

                if not amenity:
                    # Determine category
                    category = 'services'
                    if name_lower in ['pool', 'wifi', 'ac', 'tv']:
                        category = 'accommodation'
                    elif name_lower in ['restaurant', 'bar', 'breakfast', 'kitchen']:
                        category = 'food'
                    elif name_lower in ['yoga', 'gym', 'fitness', 'excursions']:
                        category = 'activities'
                    elif name_lower in ['board', 'wetsuit', 'video analysis']:
                        category = 'surf'

                    amenity = Amenity.objects.create(
                        name=name.capitalize(),
                        name_en=name.capitalize(),
                        category=category
                    )

                camp.amenities.add(amenity)

        except Exception as e:
            logger.warning(f"[DB] Error saving amenities: {e}")
            self.stats['errors'].append(f"amenities: {e}")

    def _save_images(self, camp: SurfCamp, image_paths: List[str]):
        """Save images for a camp"""
        try:
            for i, rel_path in enumerate(image_paths):
                full_path = self.media_root / rel_path

                if not full_path.exists():
                    logger.warning(f"[DB] Image not found: {full_path}")
                    continue

                # Check if image already exists
                existing = CampImage.objects.filter(
                    camp=camp,
                    image=rel_path
                ).exists()

                if existing:
                    continue

                # Create image record
                CampImage.objects.create(
                    camp=camp,
                    image=rel_path,
                    alt_text=f"{camp.name} - Image {i+1}",
                    is_main=(i == 0),
                    order=i
                )
                self.stats['images_saved'] += 1

        except Exception as e:
            logger.warning(f"[DB] Error saving images: {e}")
            self.stats['errors'].append(f"images: {e}")

    def _save_instructors(self, camp: SurfCamp, instructors: List[dict]):
        """Save instructors for a camp"""
        try:
            for inst_data in instructors:
                name = inst_data.get('name', '')
                if not name:
                    continue

                # Check if exists
                existing = Instructor.objects.filter(
                    camp=camp,
                    name=name
                ).exists()

                if existing:
                    continue

                Instructor.objects.create(
                    camp=camp,
                    name=name,
                    bio=inst_data.get('bio', ''),
                    experience_years=inst_data.get('experience_years', 0),
                    languages=', '.join(inst_data.get('languages', [])) if inst_data.get('languages') else '',
                    is_head_coach=inst_data.get('is_head_coach', False)
                )
                self.stats['instructors_saved'] += 1

        except Exception as e:
            logger.warning(f"[DB] Error saving instructors: {e}")
            self.stats['errors'].append(f"instructors: {e}")

    def _save_activities(self, camp: SurfCamp, activities: List[dict]):
        """Save activities for a camp"""
        try:
            for act_data in activities:
                name = act_data.get('name', '')
                if not name:
                    continue

                # Check if exists
                existing = Activity.objects.filter(
                    camp=camp,
                    name_en=name
                ).exists()

                if existing:
                    continue

                Activity.objects.create(
                    camp=camp,
                    name=name,
                    name_en=name,
                    description=act_data.get('description', ''),
                    price=Decimal(str(act_data.get('price', 0))) if act_data.get('price') else None,
                    is_included=act_data.get('is_included', False)
                )
                self.stats['activities_saved'] += 1

        except Exception as e:
            logger.warning(f"[DB] Error saving activities: {e}")
            self.stats['errors'].append(f"activities: {e}")

    def _save_reviews(self, camp: SurfCamp, reviews: List[dict]):
        """Save reviews for a camp"""
        try:
            for rev_data in reviews:
                text = rev_data.get('text', '')
                author = rev_data.get('author_name', 'Anonymous')

                if not text or len(text) < 20:
                    continue

                # Check if similar review exists
                existing = Review.objects.filter(
                    camp=camp,
                    author_name=author,
                    text__startswith=text[:50]
                ).exists()

                if existing:
                    continue

                # Parse visit date
                visit_date = None
                if rev_data.get('visit_date'):
                    try:
                        visit_date = datetime.strptime(rev_data['visit_date'], '%B %Y').date()
                    except:
                        pass

                Review.objects.create(
                    camp=camp,
                    author_name=author,
                    author_country=rev_data.get('author_country', ''),
                    rating=rev_data.get('rating', 5),
                    title=rev_data.get('title', '')[:200],
                    text=text,
                    visit_date=visit_date,
                    is_verified=False,
                    is_published=True
                )
                self.stats['reviews_saved'] += 1

        except Exception as e:
            logger.warning(f"[DB] Error saving reviews: {e}")
            self.stats['errors'].append(f"reviews: {e}")

    def get_stats(self) -> dict:
        """Get saver statistics"""
        return self.stats


# Import models for Q objects
from django.db import models
