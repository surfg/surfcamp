#!/usr/bin/env python3
"""
Image optimization script for SurfCamp
Converts images to WebP, creates thumbnails, optimizes quality

Usage:
    python optimize_images.py [--dry-run] [--local] [--remote]

Requirements:
    pip install Pillow
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from PIL import Image
except ImportError:
    print("Installing Pillow...")
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow"], check=True)
    from PIL import Image

# Configuration
SIZES = {
    'thumb': (400, 300),      # For list cards
    'medium': (800, 600),     # For detail page gallery
    'large': (1200, 900),     # For full view
}
WEBP_QUALITY = 82
JPEG_QUALITY = 85
MAX_WORKERS = 4


def get_image_info(filepath: Path) -> dict:
    """Get image dimensions and size"""
    try:
        with Image.open(filepath) as img:
            return {
                'path': str(filepath),
                'size_bytes': filepath.stat().st_size,
                'size_kb': filepath.stat().st_size / 1024,
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
            }
    except Exception as e:
        return {'path': str(filepath), 'error': str(e)}


def optimize_image(filepath: Path, output_dir: Path, dry_run: bool = False) -> dict:
    """
    Optimize single image:
    1. Convert to WebP
    2. Create thumbnail, medium, large versions
    3. Strip metadata
    """
    results = {
        'original': str(filepath),
        'original_size': filepath.stat().st_size,
        'created': [],
        'saved_bytes': 0,
    }

    try:
        with Image.open(filepath) as img:
            # Convert RGBA to RGB for JPEG/WebP compatibility
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Get base name without extension
            stem = filepath.stem
            camp_dir = filepath.parent.name

            # Create output directory
            out_camp_dir = output_dir / camp_dir
            if not dry_run:
                out_camp_dir.mkdir(parents=True, exist_ok=True)

            # Generate each size
            for size_name, (max_w, max_h) in SIZES.items():
                # Calculate new size maintaining aspect ratio
                ratio = min(max_w / img.width, max_h / img.height)
                if ratio >= 1:
                    # Image is smaller than target, use original size
                    new_size = (img.width, img.height)
                else:
                    new_size = (int(img.width * ratio), int(img.height * ratio))

                # Resize
                resized = img.resize(new_size, Image.LANCZOS)

                # Output filename
                out_filename = f"{stem}_{size_name}.webp"
                out_path = out_camp_dir / out_filename

                if not dry_run:
                    resized.save(
                        out_path,
                        'WEBP',
                        quality=WEBP_QUALITY,
                        method=4,  # Compression method (0-6, higher = slower but smaller)
                    )
                    new_size_bytes = out_path.stat().st_size
                else:
                    new_size_bytes = 0  # Estimate

                results['created'].append({
                    'path': str(out_path),
                    'size_name': size_name,
                    'dimensions': new_size,
                    'size_bytes': new_size_bytes,
                })

            # Calculate savings
            if not dry_run:
                total_new = sum(c['size_bytes'] for c in results['created'])
                results['saved_bytes'] = results['original_size'] - total_new
                results['compression_ratio'] = total_new / results['original_size'] if results['original_size'] > 0 else 0

    except Exception as e:
        results['error'] = str(e)

    return results


def analyze_images(media_dir: Path) -> dict:
    """Analyze all images in media directory"""
    stats = {
        'total_files': 0,
        'total_bytes': 0,
        'by_format': {},
        'by_size': {'small': 0, 'medium': 0, 'large': 0, 'huge': 0},
        'largest': [],
        'issues': [],
    }

    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

    for filepath in media_dir.rglob('*'):
        if filepath.suffix.lower() in image_extensions:
            stats['total_files'] += 1
            size = filepath.stat().st_size
            stats['total_bytes'] += size

            # By format
            ext = filepath.suffix.lower()
            stats['by_format'][ext] = stats['by_format'].get(ext, 0) + 1

            # By size
            size_kb = size / 1024
            if size_kb < 100:
                stats['by_size']['small'] += 1
            elif size_kb < 500:
                stats['by_size']['medium'] += 1
            elif size_kb < 2000:
                stats['by_size']['large'] += 1
            else:
                stats['by_size']['huge'] += 1
                stats['issues'].append(f"HUGE: {filepath.name} ({size_kb:.0f} KB)")

            # Track largest
            stats['largest'].append((size, str(filepath)))

    stats['largest'] = sorted(stats['largest'], reverse=True)[:10]
    stats['avg_size_kb'] = (stats['total_bytes'] / stats['total_files'] / 1024) if stats['total_files'] > 0 else 0

    return stats


def optimize_all(media_dir: Path, output_dir: Path, dry_run: bool = False) -> dict:
    """Optimize all images with parallel processing"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

    # Collect all image files
    image_files = [
        f for f in media_dir.rglob('*')
        if f.suffix.lower() in image_extensions and f.stat().st_size > 0
    ]

    print(f"Found {len(image_files)} images to optimize")

    if dry_run:
        print("[DRY RUN] Would create optimized versions in:", output_dir)
        return {'processed': 0, 'dry_run': True}

    results = {
        'processed': 0,
        'failed': 0,
        'total_saved_bytes': 0,
        'errors': [],
    }

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(optimize_image, f, output_dir, dry_run): f
            for f in image_files
        }

        for i, future in enumerate(as_completed(futures)):
            filepath = futures[future]
            try:
                result = future.result()
                if 'error' in result:
                    results['failed'] += 1
                    results['errors'].append(f"{filepath.name}: {result['error']}")
                else:
                    results['processed'] += 1
                    results['total_saved_bytes'] += result.get('saved_bytes', 0)

                if (i + 1) % 50 == 0:
                    print(f"Progress: {i + 1}/{len(image_files)}")

            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"{filepath.name}: {e}")

    return results


def main():
    parser = argparse.ArgumentParser(description='Optimize images for SurfCamp')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--analyze', action='store_true', help='Only analyze, no optimization')
    parser.add_argument('--local', action='store_true', help='Process local media folder')
    parser.add_argument('--input', type=str, help='Input media directory')
    parser.add_argument('--output', type=str, help='Output directory for optimized images')

    args = parser.parse_args()

    # Determine paths
    script_dir = Path(__file__).resolve().parent
    media_dir = Path(args.input) if args.input else script_dir / 'media' / 'camps'
    output_dir = Path(args.output) if args.output else script_dir / 'media' / 'optimized' / 'camps'

    if not media_dir.exists():
        print(f"ERROR: Media directory not found: {media_dir}")
        sys.exit(1)

    print("=" * 60)
    print("SURFCAMP IMAGE OPTIMIZER")
    print("=" * 60)
    print(f"Input:  {media_dir}")
    print(f"Output: {output_dir}")
    print()

    # Analyze first
    print("Analyzing images...")
    stats = analyze_images(media_dir)

    print(f"\nTotal images: {stats['total_files']}")
    print(f"Total size: {stats['total_bytes'] / 1024 / 1024:.1f} MB")
    print(f"Average size: {stats['avg_size_kb']:.0f} KB")
    print(f"\nBy format:")
    for fmt, count in sorted(stats['by_format'].items()):
        print(f"  {fmt}: {count}")
    print(f"\nBy size:")
    print(f"  Small (<100KB): {stats['by_size']['small']}")
    print(f"  Medium (100-500KB): {stats['by_size']['medium']}")
    print(f"  Large (500KB-2MB): {stats['by_size']['large']}")
    print(f"  HUGE (>2MB): {stats['by_size']['huge']}")

    if stats['issues']:
        print(f"\nIssues found ({len(stats['issues'])}):")
        for issue in stats['issues'][:5]:
            print(f"  - {issue}")

    if args.analyze:
        return

    # Optimize
    print("\n" + "=" * 60)
    print("OPTIMIZING IMAGES")
    print("=" * 60)

    results = optimize_all(media_dir, output_dir, args.dry_run)

    print(f"\nProcessed: {results['processed']}")
    print(f"Failed: {results['failed']}")
    if results.get('total_saved_bytes'):
        print(f"Space saved: {results['total_saved_bytes'] / 1024 / 1024:.1f} MB")

    if results.get('errors'):
        print(f"\nErrors ({len(results['errors'])}):")
        for err in results['errors'][:5]:
            print(f"  - {err}")


if __name__ == '__main__':
    main()
