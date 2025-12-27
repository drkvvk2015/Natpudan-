# Podman Quick Reference for Natpudan AI

## Installation (One-time setup)

```powershell
# 1. Install Podman
choco install podman -y
# OR use Scoop: scoop install podman

# 2. Install podman-compose
pip install podman-compose

# 3. Verify installation
podman --version
podman-compose --version

# 4. Initialize and start Podman Machine
podman machine init
podman machine start

# 5. Test connection
podman info
```

## Starting Your Application

### Option 1: Automated Script (Recommended)
```powershell
# Full startup with logs
.\start-podman-compose.ps1

# Production deployment
.\deploy-podman-production.ps1
```

### Option 2: Manual Commands
```powershell
# Start all services
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down
```

## Common Operations

### View Status
```powershell
# List running containers
podman-compose ps

# Get detailed container info
podman ps -a

# View system status
podman info

# Check Podman machine
podman machine list
```

### View Logs
```powershell
# All services
podman-compose logs -f

# Specific service
podman-compose logs -f backend
podman-compose logs -f db
podman-compose logs -f frontend
podman-compose logs -f celery

# Last N lines
podman-compose logs --tail 50 backend
```

### Execute Commands
```powershell
# Run command in container
podman-compose exec backend python -m pytest

# Open shell in container
podman-compose exec backend /bin/bash
podman-compose exec db psql -U physician_user

# One-off container
podman run -it python:3.11 python --version
```

### Database Operations
```powershell
# Backup database
podman-compose exec db pg_dump -U physician_user physician_ai > backup.sql

# Restore database
cat backup.sql | podman-compose exec -T db psql -U physician_user physician_ai

# Connect to database
podman-compose exec db psql -U physician_user -d physician_ai

# Run database migrations
podman-compose exec backend python -m alembic upgrade head
```

### Image Management
```powershell
# Pull latest images
podman-compose pull

# Rebuild images
podman-compose build

# Rebuild without cache
podman-compose build --no-cache

# View images
podman images

# Remove unused images
podman image prune -a
```

### Volume Management
```powershell
# List volumes
podman volume ls

# Inspect volume
podman volume inspect postgres_data

# Clean up unused volumes
podman volume prune

# Backup volume data
podman run --rm -v postgres_data:/data -v ./backup:/backup alpine tar czf /backup/postgres_data.tar.gz -C /data .
```

### Container Management
```powershell
# Restart container
podman-compose restart backend

# Remove containers
podman-compose down

# Remove containers and volumes
podman-compose down -v

# Stop specific container
podman-compose stop backend

# Start specific container
podman-compose start backend
```

### System Cleanup
```powershell
# Remove unused containers, images, networks
podman system prune -a

# Remove everything including volumes (careful!)
podman system prune -a --volumes

# Check resource usage
podman stats

# Show system info
podman system info
```

## Podman Machine Management

```powershell
# List machines
podman machine list

# Create machine (if needed)
podman machine init --cpus 4 --memory 4096

# Start machine
podman machine start

# Stop machine
podman machine stop

# SSH into machine
podman machine ssh

# Remove machine
podman machine remove
```

## Troubleshooting

### Podman Machine Not Starting
```powershell
# Check status
podman machine list

# Force start
podman machine start --force

# Restart machine
podman machine stop
podman machine start
```

### Port Conflicts
```powershell
# Find what's using a port
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Get process details
Get-Process -PID <PID>

# Change port in docker-compose.yml or:
podman-compose down
# Kill the blocking process or wait for it to finish
podman-compose up -d
```

### Volume Mount Issues
```powershell
# Check volumes
podman volume ls

# Inspect mount point
podman volume inspect postgres_data

# Verify file permissions in container
podman-compose exec backend ls -la /app/data

# Remount volume
podman-compose down
podman volume prune
podman-compose up -d
```

### Container Not Responding
```powershell
# Check logs
podman-compose logs backend

# Restart container
podman-compose restart backend

# Hard restart
podman-compose down
podman-compose up -d

# Check resource limits
podman stats
```

### Network Issues
```powershell
# Check networks
podman network ls

# Inspect network
podman network inspect physician-ai-network

# Test DNS from container
podman-compose exec backend nslookup db

# Ping between containers
podman-compose exec backend ping -c 4 db

# Check port forwarding
podman ps --no-truncate
```

## Performance Tips

1. **Allocate Resources**: 
   ```powershell
   podman machine init --cpus 4 --memory 4096
   ```

2. **Use Volumes Efficiently**: Avoid large files in bind mounts

3. **Cache Docker Layers**: Podman automatically caches layers

4. **Monitor Resource Usage**:
   ```powershell
   podman stats
   ```

## Environment Variables

Your `.env` file works as-is:
```bash
OPENAI_API_KEY=your_key
POSTGRES_USER=physician_user
POSTGRES_PASSWORD=secure_password
ENVIRONMENT=production
DEBUG=False
```

Use it:
```powershell
podman-compose --env-file .env up -d
```

## Service Access

| Service | URL/Address |
|---------|-------------|
| Backend API | http://127.0.0.1:8000 |
| Frontend | http://127.0.0.1:3000 |
| PostgreSQL | 127.0.0.1:5432 |
| Redis | 127.0.0.1:6379 |
| Flower (Tasks) | http://127.0.0.1:5555 |

## Useful Aliases

Add to PowerShell profile (`$PROFILE`):
```powershell
Set-Alias -Name dc -Value podman-compose
Set-Alias -Name podman-logs -Value "podman-compose logs -f"
Set-Alias -Name podman-ps -Value "podman-compose ps"
```

Then use:
```powershell
dc up -d          # Start services
dc down           # Stop services
podman-logs       # View logs
podman-ps         # List containers
```

## Resources

- [Podman Docs](https://docs.podman.io/)
- [Podman Compose GitHub](https://github.com/containers/podman-compose)
- [Natpudan Setup Guide](./PODMAN_SETUP.md)
- [Project Architecture](./ARCHITECTURE_DIAGRAMS.md)
