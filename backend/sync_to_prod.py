#!/usr/bin/env python3
"""
Sync local data and media to production server

Usage:
    python sync_to_prod.py [--dry-run] [--images-only] [--db-only]

Requirements:
    - SSH access to production server
    - rsync installed locally
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

# Production server config
PROD_HOST = "root@146.190.31.111"
PROD_DIR = "/root/surfcamp"
PROD_MEDIA_DIR = f"{PROD_DIR}/backend/media"
PROD_COMPOSE_FILE = "docker-compose.prod.yml"

# Local paths
LOCAL_DIR = Path(__file__).resolve().parent.parent
LOCAL_BACKEND = LOCAL_DIR / "backend"
LOCAL_MEDIA = LOCAL_BACKEND / "media"
LOCAL_DB = LOCAL_BACKEND / "db.sqlite3"


def run_cmd(cmd, dry_run=False, check=True):
    """Run shell command"""
    print(f"  $ {cmd}")
    if dry_run:
        print("  [DRY RUN - skipped]")
        return None
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return None
    return result


def sync_images(dry_run=False):
    """Sync media files to production using rsync"""
    print("\n" + "="*60)
    print("SYNCING IMAGES TO PRODUCTION")
    print("="*60)

    if not LOCAL_MEDIA.exists():
        print(f"ERROR: Local media directory not found: {LOCAL_MEDIA}")
        return False

    # Count local images
    local_images = list(LOCAL_MEDIA.glob("**/*.jpg")) + \
                   list(LOCAL_MEDIA.glob("**/*.jpeg")) + \
                   list(LOCAL_MEDIA.glob("**/*.png")) + \
                   list(LOCAL_MEDIA.glob("**/*.webp"))
    print(f"Local images to sync: {len(local_images)}")

    # Rsync command with:
    # -a: archive mode (preserves permissions, timestamps)
    # -v: verbose
    # -z: compress during transfer
    # --progress: show progress
    # --delete: remove files on dest that don't exist on source
    rsync_cmd = f"""rsync -avz --progress \\
        --exclude='*.tmp' \\
        --exclude='.DS_Store' \\
        {LOCAL_MEDIA}/ {PROD_HOST}:{PROD_MEDIA_DIR}/"""

    if dry_run:
        rsync_cmd = rsync_cmd.replace("rsync ", "rsync --dry-run ")

    print(f"\nRunning rsync...")
    result = run_cmd(rsync_cmd, dry_run=False)  # rsync has its own dry-run

    if result and result.returncode == 0:
        print("Images synced successfully!")
        return True
    else:
        print("Image sync failed!")
        return False


def export_db_data(dry_run=False):
    """Export database data to JSON for import on prod"""
    print("\n" + "="*60)
    print("EXPORTING DATABASE DATA")
    print("="*60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = LOCAL_BACKEND / f"data_export_{timestamp}.json"

    # Django dumpdata command
    cmd = f"""cd {LOCAL_BACKEND} && \\
        source venv/bin/activate && \\
        python manage.py dumpdata \\
            camps.country \\
            camps.region \\
            camps.boardtype \\
            camps.amenity \\
            camps.surfcamp \\
            camps.campimage \\
            camps.instructor \\
            camps.activity \\
            camps.review \\
            --indent 2 \\
            -o {export_file}"""

    print(f"Exporting to: {export_file}")
    result = run_cmd(cmd, dry_run=dry_run)

    if result is None and not dry_run:
        print("Export failed!")
        return None

    print(f"Exported: {export_file}")
    return export_file


def upload_db_data(export_file, dry_run=False):
    """Upload JSON data to production"""
    print("\n" + "="*60)
    print("UPLOADING DATABASE DATA")
    print("="*60)

    if not export_file or not Path(export_file).exists():
        print("ERROR: Export file not found")
        return False

    # Upload file
    scp_cmd = f"scp {export_file} {PROD_HOST}:{PROD_DIR}/backend/"
    run_cmd(scp_cmd, dry_run=dry_run)

    # Import on production
    import_cmd = f"""ssh {PROD_HOST} 'cd {PROD_DIR} && \\
        docker-compose -f {PROD_COMPOSE_FILE} exec -T backend \\
        python manage.py loaddata /app/{Path(export_file).name}'"""

    print("Importing data on production...")
    result = run_cmd(import_cmd, dry_run=dry_run)

    if result and result.returncode == 0:
        print("Database data imported successfully!")
        return True
    else:
        print("Database import may have failed - check manually")
        return False


def optimize_images_on_prod(dry_run=False):
    """Optimize images on production server"""
    print("\n" + "="*60)
    print("OPTIMIZING IMAGES ON PRODUCTION")
    print("="*60)

    # Install optipng/jpegoptim if not present, then optimize
    optimize_cmd = f"""ssh {PROD_HOST} '
        # Check if already optimized recently
        if [ -f {PROD_MEDIA_DIR}/.optimized ]; then
            echo "Images already optimized"
            exit 0
        fi

        # Install optimization tools
        apt-get update -qq && apt-get install -y -qq jpegoptim optipng 2>/dev/null

        # Optimize JPEGs (lossy, max quality 85)
        echo "Optimizing JPEGs..."
        find {PROD_MEDIA_DIR} -name "*.jpg" -o -name "*.jpeg" | head -100 | xargs -I {{}} jpegoptim --max=85 --strip-all {{}} 2>/dev/null

        # Optimize PNGs (lossless)
        echo "Optimizing PNGs..."
        find {PROD_MEDIA_DIR} -name "*.png" | head -50 | xargs -I {{}} optipng -o2 -quiet {{}} 2>/dev/null

        # Mark as optimized
        touch {PROD_MEDIA_DIR}/.optimized
        echo "Optimization complete!"
    '"""

    run_cmd(optimize_cmd, dry_run=dry_run)


def restart_prod_services(dry_run=False):
    """Restart production services to pick up new data"""
    print("\n" + "="*60)
    print("RESTARTING PRODUCTION SERVICES")
    print("="*60)

    cmd = f"""ssh {PROD_HOST} 'cd {PROD_DIR} && \\
        docker-compose -f {PROD_COMPOSE_FILE} restart backend && \\
        docker-compose -f {PROD_COMPOSE_FILE} exec -T backend python manage.py collectstatic --noinput'"""

    run_cmd(cmd, dry_run=dry_run)
    print("Services restarted!")


def check_prod_status():
    """Check production server status"""
    print("\n" + "="*60)
    print("PRODUCTION STATUS")
    print("="*60)

    cmd = f"""ssh {PROD_HOST} 'cd {PROD_DIR} && \\
        echo "=== Docker Containers ===" && \\
        docker-compose -f {PROD_COMPOSE_FILE} ps && \\
        echo "" && \\
        echo "=== Media Files ===" && \\
        find {PROD_MEDIA_DIR}/camps -type f 2>/dev/null | wc -l && \\
        echo "images in /media/camps/" && \\
        echo "" && \\
        echo "=== Disk Usage ===" && \\
        du -sh {PROD_MEDIA_DIR} 2>/dev/null || echo "N/A"
    '"""

    run_cmd(cmd, dry_run=False, check=False)


def main():
    parser = argparse.ArgumentParser(description='Sync data to production')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    parser.add_argument('--images-only', action='store_true', help='Only sync images')
    parser.add_argument('--db-only', action='store_true', help='Only sync database')
    parser.add_argument('--status', action='store_true', help='Check prod status only')
    parser.add_argument('--optimize', action='store_true', help='Optimize images on prod')

    args = parser.parse_args()

    print("="*60)
    print("SURFCAMP PRODUCTION SYNC")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    if args.status:
        check_prod_status()
        return

    if args.optimize:
        optimize_images_on_prod(args.dry_run)
        return

    if args.images_only:
        sync_images(args.dry_run)
        return

    if args.db_only:
        export_file = export_db_data(args.dry_run)
        if export_file:
            upload_db_data(export_file, args.dry_run)
        return

    # Full sync
    print("\nStarting full sync to production...")

    # 1. Sync images first
    sync_images(args.dry_run)

    # 2. Export and upload database data
    export_file = export_db_data(args.dry_run)
    if export_file:
        upload_db_data(export_file, args.dry_run)

    # 3. Optimize images
    optimize_images_on_prod(args.dry_run)

    # 4. Restart services
    restart_prod_services(args.dry_run)

    # 5. Check status
    check_prod_status()

    print("\n" + "="*60)
    print("SYNC COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
