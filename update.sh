#!/bin/bash
# SurfCamp Safe Deployment Script

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

BRANCH="main"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}🏄 SurfCamp Safe Deployment Script${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 1. Check current branch
echo -e "${YELLOW}📍 Step 1/8: Checking current branch...${NC}"
CURRENT_BRANCH=$(git branch --show-current)
echo "   Current branch: $CURRENT_BRANCH"
echo "   Target branch: $BRANCH"

if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
    echo -e "${YELLOW}⚠️  Switching to $BRANCH...${NC}"
    git fetch
    git checkout $BRANCH
fi
echo -e "${GREEN}✅ Branch OK${NC}"
echo ""

# 2. Check container status
echo -e "${YELLOW}📍 Step 2/8: Checking container status...${NC}"
if docker ps | grep -q surfcamp; then
    echo -e "${GREEN}✅ Containers running${NC}"
else
    echo -e "${YELLOW}⚠️  Containers not running, will start fresh${NC}"
fi
echo ""

# 3. Check PostgreSQL (if running)
echo -e "${YELLOW}📍 Step 3/8: Checking PostgreSQL...${NC}"
if docker ps | grep -q surfcamp_db; then
    if docker exec surfcamp_db pg_isready -U surfcamp_user -d surfcamp > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is healthy${NC}"

        # 4. Create backup
        echo ""
        echo -e "${YELLOW}📍 Step 4/8: Creating database backup...${NC}"
        BACKUP_DIR="/opt/backups/surfcamp"
        mkdir -p $BACKUP_DIR
        DATE=$(date +%Y%m%d_%H%M%S)
        BACKUP_FILE="surfcamp_backup_${DATE}.sql"

        docker exec surfcamp_db pg_dump -U surfcamp_user surfcamp > "${BACKUP_DIR}/${BACKUP_FILE}"
        gzip "${BACKUP_DIR}/${BACKUP_FILE}"
        echo -e "${GREEN}✅ Backup created: ${BACKUP_FILE}.gz${NC}"

        # Delete old backups (keep last 7 days)
        find $BACKUP_DIR -name "*.gz" -mtime +7 -delete 2>/dev/null || true
    else
        echo -e "${YELLOW}⚠️  PostgreSQL not ready, skipping backup${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Database not running, skipping backup${NC}"
fi
echo ""

# 5. Pull latest changes
echo -e "${YELLOW}📍 Step 5/8: Pulling latest changes...${NC}"
git fetch origin $BRANCH
BEFORE_COMMIT=$(git rev-parse HEAD)
git pull origin $BRANCH
AFTER_COMMIT=$(git rev-parse HEAD)

if [ "$BEFORE_COMMIT" = "$AFTER_COMMIT" ]; then
    echo -e "${BLUE}ℹ️  No new changes${NC}"
else
    echo -e "${GREEN}✅ Changes pulled${NC}"
    echo "   Commit: $AFTER_COMMIT"
fi
echo ""

# 6. Check for config changes
echo -e "${YELLOW}📍 Step 6/8: Checking configuration changes...${NC}"
REBUILD_ALL=false
if git diff $BEFORE_COMMIT $AFTER_COMMIT --name-only 2>/dev/null | grep -q "docker-compose"; then
    echo -e "${YELLOW}⚠️  Docker config changed, rebuilding all${NC}"
    REBUILD_ALL=true
else
    echo -e "${GREEN}✅ Config unchanged${NC}"
fi
echo ""

# 7. Rebuild and restart containers
echo -e "${YELLOW}📍 Step 7/8: Rebuilding containers...${NC}"

if [ "$REBUILD_ALL" = true ] || git diff $BEFORE_COMMIT $AFTER_COMMIT --name-only 2>/dev/null | grep -q "^backend/"; then
    echo "   🔨 Rebuilding backend..."
    docker-compose -f docker-compose.prod.yml build backend
fi

if [ "$REBUILD_ALL" = true ] || git diff $BEFORE_COMMIT $AFTER_COMMIT --name-only 2>/dev/null | grep -q "^frontend/"; then
    echo "   🔨 Rebuilding frontend..."
    docker-compose -f docker-compose.prod.yml build frontend
fi

# Stop and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

echo -e "${GREEN}✅ Containers updated${NC}"
echo ""

# 8. Wait and verify
echo -e "${YELLOW}📍 Step 8/8: Waiting for services...${NC}"
echo "   Waiting 20 seconds..."
sleep 20

# Verify health
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Final Status${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📝 Useful commands:"
echo "   Logs backend:  docker logs -f surfcamp_backend"
echo "   Logs nginx:    docker logs -f surfcamp_nginx"
echo "   All logs:      docker-compose -f docker-compose.prod.yml logs -f"
echo "   Status:        docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "🌐 Access: http://146.190.31.111:8080"
echo ""
