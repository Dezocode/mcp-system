# 🐳 Windows Docker Desktop Deployment Plan

## Architecture Overview
```
┌─────────────────┐    ┌─────────────────┐
│    WSL2 Linux   │    │  Windows Host   │
│  ┌───────────┐  │    │  ┌───────────┐  │
│  │MCP System │  │━━━━│━━│Docker     │  │
│  │Source Code│  │    │  │Desktop    │  │
│  └───────────┘  │    │  └───────────┘  │
└─────────────────┘    └─────────────────┘
```

## Current Status ✅
- **Environment**: WSL2 Ubuntu on Windows 11/10
- **Docker**: Docker Desktop installed on Windows host
- **MCP System**: Fully containerized and standardized
- **Services**: 7-container production stack ready

## Production Stack Components

### Core Services
1. **mcp-system** - Main application server (ports 8050-8060)
2. **postgres** - Database with health checks (port 5432)
3. **redis** - Cache and session store (port 6379)
4. **nginx** - Reverse proxy and SSL termination (ports 80, 443)

### Monitoring Stack
5. **prometheus** - Metrics collection (port 9090)
6. **grafana** - Dashboards and visualization (port 3000)
7. **backup** - Automated database backups

## 🚀 Deployment Commands

### Step 1: Environment Setup
```bash
# Create environment file
cat > .env << EOF
DB_PASSWORD=your_secure_db_password
GRAFANA_PASSWORD=your_grafana_admin_password
EOF

# Ensure Docker Desktop is running
docker --version
docker-compose --version
```

### Step 2: Build Production Images
```bash
# Build main application
docker build -f Dockerfile.production -t mcp-system:latest .

# Verify build
docker images | grep mcp-system
```

### Step 3: Full Stack Deployment
```bash
# Deploy complete production stack
docker-compose -f docker-compose.prod.yml up -d

# Monitor deployment
docker-compose -f docker-compose.prod.yml logs -f
```

### Step 4: Health Verification
```bash
# Check all services status
docker-compose -f docker-compose.prod.yml ps

# Verify health checks
docker-compose -f docker-compose.prod.yml exec mcp-system mcp-universal status
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U mcpuser
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
```

## 🌐 Service Access Points

| Service | Internal Port | External Access | Health Check |
|---------|---------------|-----------------|--------------|
| MCP System | 8050-8060 | http://localhost:8050 | `/health` |
| PostgreSQL | 5432 | localhost:5432 | `pg_isready` |
| Redis | 6379 | localhost:6379 | `redis-cli ping` |
| Nginx | 80/443 | http://localhost | `nginx -t` |
| Prometheus | 9090 | http://localhost:9090 | `/-/healthy` |
| Grafana | 3000 | http://localhost:3000 | `/api/health` |

## 📊 Monitoring Dashboard Access

### Prometheus Metrics
- **URL**: http://localhost:9090
- **Targets**: All service health endpoints
- **Retention**: 30 days of metrics data

### Grafana Analytics
- **URL**: http://localhost:3000
- **Login**: admin / ${GRAFANA_PASSWORD}
- **Pre-installed plugins**: Clock panel, Simple JSON datasource

## 🔒 Security Configuration

### SSL/TLS Setup (Optional)
```bash
# Create SSL certificates directory
mkdir -p ssl

# Generate self-signed certificates (development)
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes

# Update nginx.conf for HTTPS
# Add ssl_certificate and ssl_certificate_key directives
```

### Network Security
- **Isolated Bridge Network**: 172.20.0.0/16 subnet
- **Internal Service Communication**: Container-to-container only
- **External Access**: Only through nginx proxy
- **Database Security**: Password-protected with environment variables

## 💾 Data Persistence

### Volume Mapping
```yaml
volumes:
  mcp_data: /home/mcpuser/.mcp-system          # Application data
  mcp_logs: /var/log/mcp-system                # Application logs  
  postgres_data: /var/lib/postgresql/data      # Database persistence
  redis_data: /data                            # Cache persistence
  nginx_logs: /var/log/nginx                   # Web server logs
  prometheus_data: /prometheus                 # Metrics storage
  grafana_data: /var/lib/grafana              # Dashboard configs
  mcp_backups: /backups                        # Database backups
```

### Backup Strategy
```bash
# Manual backup
docker-compose -f docker-compose.prod.yml run --rm backup

# Automated backups (add to crontab)
0 2 * * * cd /home/dezocode/mcp-system && docker-compose -f docker-compose.prod.yml run --rm backup
```

## 🔧 Development vs Production

### Development Mode
```bash
# Use standard Dockerfile with hot reload
docker-compose -f docker-compose.yml up -d
```

### Production Mode  
```bash
# Use optimized production build
docker-compose -f docker-compose.prod.yml up -d
```

## 📈 Scaling Configuration

### Horizontal Scaling
```bash
# Scale MCP system instances
docker-compose -f docker-compose.prod.yml up -d --scale mcp-system=3

# Load balancer will distribute across instances
```

### Resource Limits (Add to docker-compose.prod.yml)
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'  
      memory: 2G
```

## 🐛 Troubleshooting

### Common Issues
1. **Port Conflicts**: Check if ports 80, 443, 3000, 5432, 6379, 8050-8060, 9090 are free
2. **WSL Docker Integration**: Ensure Docker Desktop has WSL2 integration enabled
3. **Memory Issues**: Increase Docker Desktop memory allocation (8GB recommended)
4. **File Permissions**: Use `docker-compose down -v && docker-compose up -d` to reset volumes

### Debug Commands
```bash
# Container logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# Execute commands in containers
docker-compose -f docker-compose.prod.yml exec mcp-system bash

# Resource usage
docker stats

# Network inspection
docker network inspect mcp-system_default
```

## 🎯 Success Criteria

### Deployment Complete When:
- ✅ All 7 services running and healthy
- ✅ MCP system accessible at http://localhost:8050
- ✅ Database accepting connections
- ✅ Monitoring dashboards operational
- ✅ SSL certificates configured (if using HTTPS)
- ✅ Backup system operational
- ✅ All health checks passing

### Performance Targets:
- **Response Time**: < 200ms for API calls
- **Uptime**: > 99.9% availability
- **Resource Usage**: < 4GB RAM, < 2 CPU cores
- **Storage Growth**: < 1GB per month

---

**Ready for Windows Docker Desktop deployment from WSL environment! 🚀**