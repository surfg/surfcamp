"""Auto-generate optimized WebP copies when CampImage is saved."""
import logging
import os

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CampImage

logger = logging.getLogger(__name__)

SIZES = {
    'thumb': (400, 300),
    'medium': (800, 600),
    'large': (1200, 900),
}
WEBP_QUALITY = 82


def _optimize_image_file(image_field):
    try:
        from PIL import Image
    except ImportError:
        logger.warning("Pillow not installed, skipping optimization")
        return

    src_path = image_field.path
    if not os.path.exists(src_path):
        return

    rel_name = image_field.name  # e.g. camps/slug/img.jpg
    dir_name = os.path.dirname(rel_name)
    base_name = os.path.basename(rel_name)
    stem = os.path.splitext(base_name)[0]

    out_dir = os.path.join(settings.MEDIA_ROOT, 'optimized', dir_name)
    os.makedirs(out_dir, exist_ok=True)

    with Image.open(src_path) as img:
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        for size_name, (max_w, max_h) in SIZES.items():
            ratio = min(max_w / img.width, max_h / img.height)
            new_size = (img.width, img.height) if ratio >= 1 else (
                int(img.width * ratio), int(img.height * ratio)
            )
            resized = img.resize(new_size, Image.LANCZOS)
            out_path = os.path.join(out_dir, f"{stem}_{size_name}.webp")
            resized.save(out_path, 'WEBP', quality=WEBP_QUALITY, method=4)


@receiver(post_save, sender=CampImage)
def optimize_camp_image(sender, instance, created, **kwargs):
    if not instance.image:
        return
    try:
        _optimize_image_file(instance.image)
    except Exception as e:
        logger.exception("Failed to optimize CampImage %s: %s", instance.pk, e)
