# MCP System Docker Deployment Guide

## Overview

This guide provides complete instructions for deploying the MCP System using Docker and Docker Compose following best practices for production environments.

## 🚀 Quick Start

### Development Deployment

```bash
# Clone the repository
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Validate configuration
./validate.sh

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps
```

### Production Deployment

```bash
# Prepare environment
cp .env.prod.example .env.prod
# Edit .env.prod with your configuration

# Generate SSL certificates (or provide your own)
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/mcp.key -out ssl/mcp.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# Deploy with automation script
./deploy.sh

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ RAM
- 10GB+ disk space
- SSL certificates (for production)

## 🏗️ Architecture

### Services

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| mcp-system | Main MCP server management | 8050-8060 | `/health` |
| postgres | Database for persistent data | 5432 | `pg_isready` |
| redis | Caching and session storage | 6379 | `redis-cli ping` |
| nginx | Reverse proxy and SSL termination | 80, 443 | `nginx -t` |
| prometheus | Metrics collection | 9090 | `/api/v1/status` |
| grafana | Monitoring dashboard | 3000 | `/api/health` |

### Data Flow

```
Internet → Nginx → MCP System ↔ Redis
                      ↓
                  PostgreSQL
                      ↓
                  Prometheus ← Grafana
```

## 🔧 Configuration

### Environment Variables

#### Core Settings
```bash
MCP_ENV=production
MCP_DEBUG=false
MCP_AUTO_DISCOVERY=true
MCP_SAFE_MODE=true
MCP_LOG_LEVEL=warning
```

#### Database
```bash
DATABASE_URL=postgresql://mcpuser:${DB_PASSWORD}@postgres:5432/mcpsystem
REDIS_URL=redis://redis:6379/0
```

#### Security
```bash
MCP_REQUIRE_AUTH=true
MCP_RATE_LIMIT=true
MCP_HTTPS_ONLY=true
JWT_SECRET_KEY=your-secret-key
```

#### Monitoring
```bash
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
METRICS_ENABLED=true
```

### SSL/TLS Configuration

For production, you need valid SSL certificates:

```bash
# Option 1: Let's Encrypt (recommended)
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/mcp.crt
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/mcp.key

# Option 2: Self-signed (development only)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/mcp.key -out ssl/mcp.crt
```

## 🛡️ Security Best Practices

### Network Security
- All services run in isolated Docker network
- Only necessary ports exposed
- SSL/TLS encryption for all external traffic
- Rate limiting on API endpoints

### Container Security
- Non-root user for all services
- Multi-stage builds for minimal attack surface
- Security scanning with Trivy
- Regular base image updates

### Data Security
- Encrypted database connections
- Secure secret management
- Regular automated backups
- Access logging and monitoring

## 📊 Monitoring and Observability

### Metrics Available
- MCP server performance metrics
- Database connection pools
- Redis cache hit rates
- HTTP request rates and latencies
- System resource utilization

### Grafana Dashboards
Access at `https://yourdomain.com/grafana`

Default dashboards:
- MCP System Overview
- Infrastructure Monitoring
- Application Performance
- Security Events

### Alerting Rules
Prometheus alerting for:
- Service downtime
- High error rates
- Resource exhaustion
- Security incidents

## 🔄 Backup and Recovery

### Automated Backups

```bash
# Manual backup
docker-compose -f docker-compose.prod.yml run --rm backup

# Scheduled backups (add to crontab)
0 2 * * * cd /path/to/mcp-system && docker-compose -f docker-compose.prod.yml run --rm backup
```

### Backup Contents
- PostgreSQL database dump
- MCP system configuration
- Application data
- Docker compose configurations

### Recovery Process

```bash
# Stop services
docker-compose -f docker-compose.prod.yml down

# Restore database
gunzip -c backup/database_YYYYMMDD_HHMMSS.sql.gz | \
    docker-compose -f docker-compose.prod.yml exec -T postgres psql -U mcpuser -d mcpsystem

# Restore application data
tar -xzf backup/mcp_data_YYYYMMDD_HHMMSS.tar.gz -C /

# Restart services
docker-compose -f docker-compose.prod.yml up -d
```

## 🚀 Deployment Strategies

### Rolling Updates

```bash
# Update application
docker-compose -f docker-compose.prod.yml build mcp-system
docker-compose -f docker-compose.prod.yml up -d --no-deps mcp-system

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale mcp-system=3
```

### Blue-Green Deployment

```bash
# Deploy new version to staging
docker-compose -f docker-compose.staging.yml up -d

# Test new version
curl -f https://staging.yourdomain.com/health

# Switch traffic (update load balancer)
# Shutdown old version
```

## 🔍 Troubleshooting

### Common Issues

#### Service Won't Start
```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs mcp-system

# Check health status
docker-compose -f docker-compose.prod.yml ps

# Debug container
docker-compose -f docker-compose.prod.yml exec mcp-system bash
```

#### Database Connection Issues
```bash
# Test database connectivity
docker-compose -f docker-compose.prod.yml exec postgres psql -U mcpuser -d mcpsystem

# Check database logs
docker-compose -f docker-compose.prod.yml logs postgres
```

#### SSL Certificate Issues
```bash
# Verify certificate
openssl x509 -in ssl/mcp.crt -text -noout

# Test SSL configuration
curl -I https://yourdomain.com
```

### Performance Tuning

#### Database Optimization
```bash
# Increase connection pool
# In docker-compose.prod.yml:
environment:
  - POSTGRES_MAX_CONNECTIONS=200
```

#### Redis Configuration
```bash
# Increase memory limit
# In docker-compose.prod.yml:
command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

#### Nginx Optimization
```bash
# Increase worker processes
# In nginx.conf:
worker_processes auto;
worker_connections 2048;
```

## 📝 Maintenance

### Regular Tasks
- [ ] Update base images monthly
- [ ] Review security logs weekly
- [ ] Test backup/recovery quarterly
- [ ] Update SSL certificates before expiry
- [ ] Monitor resource usage trends

### Health Checks
```bash
# System health overview
./validate.sh

# Service status
docker-compose -f docker-compose.prod.yml ps

# Resource usage
docker stats

# Application health
curl -f https://yourdomain.com/health
```

## 🔗 Integration

### Claude Code Integration
The system automatically integrates with Claude Code when deployed. Configuration is managed in:
- `~/.claude/claude_desktop_config.json`

### CI/CD Integration
GitHub Actions workflows available in `.github/workflows/`:
- Development testing
- Security scanning
- Production deployment

### API Integration
RESTful API available at:
- `GET /api/health` - Health check
- `GET /api/servers` - List MCP servers
- `POST /api/servers` - Create new server
- `GET /metrics` - Prometheus metrics

## 📞 Support

### Documentation
- [MCP Protocol Documentation](https://modelcontextprotocol.io)
- [Docker Best Practices](https://docs.docker.com/develop/best-practices/)
- [Production Checklist](./PRODUCTION_CHECKLIST.md)

### Community
- GitHub Issues: Report bugs and feature requests
- Discussions: Community support and questions

---

## 🎯 Quick Reference

### Essential Commands
```bash
# Start production stack
./deploy.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale mcp-system=3

# Backup data
docker-compose -f docker-compose.prod.yml run --rm backup

# Update services
docker-compose -f docker-compose.prod.yml pull && \
docker-compose -f docker-compose.prod.yml up -d
```

### Service URLs
- **MCP System**: https://yourdomain.com
- **Grafana**: https://yourdomain.com/grafana
- **Prometheus**: https://yourdomain.com/prometheus (internal only)

This deployment follows Docker and Anthropic MCP best practices for security, scalability, and maintainability.