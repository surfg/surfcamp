#!/bin/bash
# SurfCamp Database Backup Script

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

BACKUP_DIR="/opt/backups/surfcamp"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="surfcamp_backup_${DATE}.sql"

echo -e "${YELLOW}🗄️  Creating SurfCamp database backup...${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
docker exec surfcamp_db pg_dump -U surfcamp_user surfcamp > "${BACKUP_DIR}/${BACKUP_FILE}"
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

echo -e "${GREEN}✅ Backup created: ${BACKUP_DIR}/${BACKUP_FILE}.gz${NC}"

# Delete backups older than 7 days
echo -e "${YELLOW}🧹 Cleaning old backups...${NC}"
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete 2>/dev/null || true

# List recent backups
echo ""
echo -e "${GREEN}📋 Recent backups:${NC}"
ls -lh $BACKUP_DIR/*.gz 2>/dev/null | tail -5 || echo "No backups found"
