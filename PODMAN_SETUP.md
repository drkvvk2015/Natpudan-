# Podman Configuration for Natpudan AI Medical Assistant

## Overview
This guide configures Podman as a drop-in Docker replacement for the Natpudan project.

## Prerequisites

1. **Install Podman** (Windows):
   ```powershell
   # Via Chocolatey
   choco install podman -y
   
   # Or via Scoop
   scoop install podman
   
   # Or download from: https://podman.io/docs/installation/windows
   ```

2. **Verify Podman Installation**:
   ```powershell
   podman --version
   podman info
   ```

3. **Install Podman Compose** (required for docker-compose.yml compatibility):
   ```powershell
   # Via pip
   pip install podman-compose
   
   # Verify installation
   podman-compose --version
   ```

4. **Start Podman Machine** (required on Windows/Mac):
   ```powershell
   podman machine init
   podman machine start
   
   # Verify it's running
   podman machine list
   ```

## Key Configuration Files

### 1. docker-compose.yml
✅ **NO CHANGES NEEDED** - Podman is fully compatible with standard docker-compose syntax.

The existing `docker-compose.yml` works as-is with:
- Named networks (`physician-ai-network`)
- Health checks
- Volume mounts
- Environment variables
- Service dependencies

### 2. Dockerfile (Backend & Frontend)
✅ **NO CHANGES NEEDED** - Podman uses standard Dockerfile format.

## Usage Commands

### Basic Operations

```powershell
# Start all services
podman-compose up -d

# Stop all services
podman-compose down

# View logs
podman-compose logs -f backend
podman-compose logs -f frontend
podman-compose logs -f db

# List running containers
podman-compose ps

# Execute command in container
podman-compose exec backend python -m pytest tests/

# Rebuild images
podman-compose build --no-cache
```

### Container Management

```powershell
# View all containers (running + stopped)
podman ps -a

# Remove unused resources
podman system prune -a

# Check Podman machine status
podman machine list
podman machine inspect

# Podman machine logs
podman machine info
```

## Deployment Scripts

Use the provided Podman deployment scripts:

### start-podman-compose.ps1
Starts the full stack with Podman Compose:
```powershell
.\start-podman-compose.ps1
```

### deploy-podman-production.ps1
Production deployment with Podman:
```powershell
.\deploy-podman-production.ps1 -EnvFile .env
```

### migrate-from-docker.ps1
Migrates from Docker to Podman:
```powershell
.\migrate-from-docker.ps1
```

## Networking

Podman automatically handles networking for your setup:

- **Container-to-container**: Use service names (e.g., `db`, `redis`, `backend`)
- **Host access**: Services accessible on `127.0.0.1:<port>` or your machine IP
- **DNS**: Podman's internal DNS resolves container names

### Network Inspection

```powershell
# List networks
podman network ls

# Inspect network
podman network inspect physician-ai-network

# Test connectivity between containers
podman-compose exec backend ping db
```

## Volume Management

Podman uses the same volume syntax as Docker:

```powershell
# List volumes
podman volume ls

# Inspect volume
podman volume inspect postgres_data

# Remove unused volumes
podman volume prune
```

## Troubleshooting

### Issue: Podman machine not running
```powershell
podman machine start
podman machine status
```

### Issue: Port conflicts
```powershell
# Find what's using a port
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
Get-Process -PID <PID>
```

### Issue: Volume mount problems on Windows
Podman automatically converts Windows paths to Linux paths in the VM. If you encounter issues:
```powershell
# Use absolute paths in docker-compose.yml
# Podman will handle the conversion automatically

# Verify mount in container
podman-compose exec backend ls -la /app/data
```

### Issue: Database connection failures
```powershell
# Check container logs
podman-compose logs db

# Verify network
podman network inspect physician-ai-network

# Test DNS from container
podman-compose exec backend nslookup db
```

### View Podman machine logs
```powershell
podman machine inspect --format='{{.ID}}'
```

## Performance Optimization

### 1. Resource Allocation
Configure Podman machine resources:
```powershell
podman machine init --cpus 4 --memory 4096
```

### 2. Volume Performance
Use `cached` option for macOS (not needed on Windows):
```yaml
# In docker-compose.yml volumes
volumes:
  - ./backend/data:/app/data:cached  # For read-heavy operations
```

### 3. Image Caching
Keep images fresh but use caching:
```powershell
# Check image age
podman images --no-trunc

# Pull latest without rebuilding
podman-compose pull
```

## Security Considerations

### Rootless Mode (Default)
Podman runs rootless by default, which is more secure than Docker:
- ✅ No root privileges needed
- ✅ Better isolation between containers
- ⚠️ Some port bindings require ports > 1024 (or use sudo)

### Port Binding for Privileged Ports
If binding to ports < 1024:
```powershell
# Run with escalation (not recommended for production)
podman machine start --rootful  # Requires auth

# Better: Use ports > 1024
# E.g., 8000 instead of 80, 443 instead of 443
```

## Environment Variables

Your `.env` file works as-is with Podman:

```bash
# .env
OPENAI_API_KEY=your_key_here
POSTGRES_USER=physician_user
POSTGRES_PASSWORD=secure_password
```

Use the same `.env` file:
```powershell
podman-compose --env-file .env up -d
```

## Comparison: Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| Docker Compose | ✅ Docker Desktop | ✅ podman-compose |
| Dockerfile | ✅ | ✅ |
| Container format | ✅ | ✅ (OCI-compliant) |
| Rootless mode | ❌ Complex | ✅ Default |
| Daemon required | ✅ Always | ✅ Or daemonless |
| Resource overhead | Higher | Lower |
| Socket location | `/var/run/docker.sock` | `/run/podman/podman.sock` |

## Next Steps

1. ✅ Verify Podman is installed and running:
   ```powershell
   podman machine start
   podman info
   ```

2. ✅ Start your application:
   ```powershell
   cd d:\Users\CNSHO\Documents\GitHub\Natpudan-
   podman-compose up -d
   ```

3. ✅ Monitor services:
   ```powershell
   podman-compose logs -f
   ```

4. ✅ Access services:
   - Backend API: http://127.0.0.1:8000
   - Frontend: http://127.0.0.1:3000
   - PostgreSQL: 127.0.0.1:5432
   - Redis: 127.0.0.1:6379

## References

- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose on GitHub](https://github.com/containers/podman-compose)
- [OCI Container Specification](https://opencontainers.org/)
