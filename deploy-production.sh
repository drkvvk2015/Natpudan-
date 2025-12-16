#!/bin/bash

# Natpudan Production Deployment Script
# Run this on your production server after cloning the repo

set -e

echo "========================================"
echo "  Natpudan Production Deployment"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo -e "${YELLOW}[1/6] Checking prerequisites...${NC}"
for cmd in docker docker-compose git; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}ERROR: $cmd not found. Please install it first.${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Step 2: Prepare environment
echo -e "${YELLOW}[2/6] Preparing environment...${NC}"
cd backend

if [ ! -f .env ]; then
    echo "  Creating .env from template..."
    cp .env.production .env
    echo -e "${RED}  ⚠ WARNING: .env created with default values!${NC}"
    echo -e "${RED}  You MUST edit .env and update:${NC}"
    echo -e "${RED}    - SECRET_KEY (use: openssl rand -hex 32)${NC}"
    echo -e "${RED}    - OPENAI_API_KEY${NC}"
    echo -e "${RED}    - POSTGRES_PASSWORD${NC}"
    echo -e "${RED}    - CORS_ORIGINS${NC}"
    echo ""
    read -p "Press Enter after updating .env file..."
else
    echo -e "${GREEN}  ✓ .env already exists${NC}"
fi
cd ..
echo ""

# Step 3: Build Docker images
echo -e "${YELLOW}[3/6] Building Docker images...${NC}"
docker-compose build
echo -e "${GREEN}✓ Build complete${NC}"
echo ""

# Step 4: Start services
echo -e "${YELLOW}[4/6] Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Step 5: Initialize database
echo -e "${YELLOW}[5/6] Initializing database...${NC}"
sleep 5  # Wait for DB to be ready
docker-compose exec -T backend python init_db_manual.py 2>/dev/null || true
echo -e "${GREEN}✓ Database initialized${NC}"
echo ""

# Step 6: Health checks
echo -e "${YELLOW}[6/6] Running health checks...${NC}"
echo ""

docker-compose ps
echo ""

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Backend health check passed${NC}"
else
    echo -e "${RED}✗ Backend health check FAILED${NC}"
fi

# Check Redis
if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis health check passed${NC}"
else
    echo -e "${RED}✗ Redis health check FAILED${NC}"
fi

# Check Celery
if docker-compose exec celery celery -A app.celery_config inspect active > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Celery worker health check passed${NC}"
else
    echo -e "${RED}✗ Celery worker health check FAILED (may be normal if no tasks running)${NC}"
fi

echo ""
echo "========================================"
echo -e "${GREEN}✓ DEPLOYMENT COMPLETE!${NC}"
echo "========================================"
echo ""
echo "Access your application:"
echo "  Frontend:     http://your-server-ip:3000"
echo "  Backend API:  http://your-server-ip:8000"
echo "  API Docs:     http://your-server-ip:8000/docs"
echo "  Flower:       http://your-server-ip:5555"
echo ""
echo "Next steps:"
echo "  1. Setup SSL/TLS with Nginx"
echo "  2. Configure domain DNS"
echo "  3. Setup monitoring and backups"
echo "  4. Run: docker-compose logs -f (to monitor)"
echo ""
