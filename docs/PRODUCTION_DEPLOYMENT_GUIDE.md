# MCP System Production Deployment Guide

This guide provides step-by-step instructions for deploying MCP System in production with security best practices and proper connection validation.

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Clone the repository
git clone https://github.com/Dezocode/mcp-system.git
cd mcp-system

# Check prerequisites
./scripts/validate-connections.sh report

# Setup production secrets
./deploy.sh setup-secrets

# Review and customize configuration
cp .env.prod .env.prod.local
# Edit .env.prod.local with your values
```

### 2. Configure Secrets

**Important**: Use Docker secrets for all sensitive data in production.

```bash
# Method 1: Automated setup (recommended)
export DB_PASSWORD="your_secure_database_password"
export GRAFANA_PASSWORD="your_secure_grafana_password"
./scripts/setup-secrets.sh

# Method 2: Manual setup
mkdir -p ./secrets
echo "your_secure_database_password" > ./secrets/db_password.txt
echo "your_secure_grafana_password" > ./secrets/grafana_password.txt
openssl rand -base64 32 > ./secrets/jwt_secret.txt
chmod 600 ./secrets/*.txt
```

### 3. Deploy

```bash
# Full deployment with validation
./deploy.sh

# Check deployment status
./deploy.sh status

# Validate all connections
./deploy.sh validate
```

## 🔧 Configuration

### Port Configuration

All ports are configurable through environment variables in `.env.prod`:

```bash
# MCP System Ports
MCP_HTTP_PORT=8050          # Main HTTP API
MCP_WEBSOCKET_PORT=8051     # WebSocket transport  
MCP_PIPELINE_PORT=8052      # Pipeline MCP server
MCP_HEALTH_PORT=9000        # Health checks

# Infrastructure Ports
POSTGRES_PORT=5432          # Database
REDIS_PORT=6379             # Cache
NGINX_HTTP_PORT=80          # Web proxy
NGINX_HTTPS_PORT=443        # Secure web proxy
PROMETHEUS_PORT=9090        # Metrics
GRAFANA_PORT=3000           # Monitoring dashboard
```

### Security Configuration

```bash
# Security Settings
MCP_REQUIRE_AUTH=true
MCP_RATE_LIMIT=true
MCP_HTTPS_ONLY=true

# Performance Tuning
PIPELINE_MAX_SESSIONS=50
PIPELINE_SESSION_TIMEOUT=3600
POSTGRES_MAX_CONNECTIONS=100
REDIS_MAXMEMORY=512mb
```

## 🛡️ Security Best Practices

### 1. Docker Secrets (Required)

- ✅ **Database passwords** stored in `secrets/db_password.txt`
- ✅ **Grafana passwords** stored in `secrets/grafana_password.txt`
- ✅ **JWT secrets** stored in `secrets/jwt_secret.txt`
- ✅ **File permissions** set to `600`
- ✅ **Secrets directory** excluded from version control

### 2. SSL/TLS Configuration

```bash
# Production certificates
mkdir -p ssl
cp your-domain.crt ssl/mcp.crt
cp your-domain.key ssl/mcp.key

# Development (self-signed)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/mcp.key -out ssl/mcp.crt
```

### 3. Network Security

- All services communicate through internal Docker network
- Only necessary ports exposed externally
- HTTPS enforced for external access
- Rate limiting enabled

## 📊 Connection Validation

The system includes comprehensive connection validation to ensure all services are properly connected:

### Automated Validation

```bash
# Full validation (recommended)
./deploy.sh validate

# Quick check of core services
./scripts/validate-connections.sh quick

# Generate status report
./scripts/validate-connections.sh report
```

### Manual Validation

```bash
# Check service health
docker compose -f docker-compose.prod.yml ps

# Test database connection
psql -h localhost -p 5432 -U mcpuser -d mcpsystem

# Test Redis connection
redis-cli -h localhost -p 6379 ping

# Test API endpoints
curl -f http://localhost:9000/health
curl -f http://localhost:8050/api/servers
```

## 🔄 Operational Commands

### Deployment Management

```bash
# Deploy/update system
./deploy.sh deploy

# Stop system
./deploy.sh stop

# View logs
./deploy.sh logs [service-name]

# Check status
./deploy.sh status
```

### Backup and Recovery

```bash
# Create backup
./deploy.sh backup

# Scheduled backups (add to crontab)
0 2 * * * cd /path/to/mcp-system && ./deploy.sh backup
```

### Monitoring

```bash
# Access monitoring dashboards
open http://localhost:3000    # Grafana
open http://localhost:9090    # Prometheus

# View metrics
curl http://localhost:9000/metrics
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Secret Configuration Issues

```bash
# Check secret files exist
ls -la secrets/
# Expected: db_password.txt, grafana_password.txt, jwt_secret.txt

# Check permissions
stat -c "%a %n" secrets/*.txt
# Expected: 600 for all files

# Regenerate secrets
./scripts/setup-secrets.sh
```

#### 2. Connection Issues

```bash
# Run full connection validation
./deploy.sh validate

# Check specific services
docker compose -f docker-compose.prod.yml logs postgres
docker compose -f docker-compose.prod.yml logs redis
docker compose -f docker-compose.prod.yml logs mcp-system
```

#### 3. Port Conflicts

```bash
# Check what's using ports
netstat -tulpn | grep :8050
netstat -tulpn | grep :5432

# Customize ports in .env.prod
MCP_HTTP_PORT=8060
POSTGRES_PORT=5433
```

### Health Check Endpoints

| Service | Endpoint | Expected Response |
|---------|----------|------------------|
| MCP System | `http://localhost:9000/health` | `200 OK` |
| PostgreSQL | `pg_isready -h localhost -p 5432` | `accepting connections` |
| Redis | `redis-cli -h localhost -p 6379 ping` | `PONG` |
| Prometheus | `http://localhost:9090/-/healthy` | `200 OK` |
| Grafana | `http://localhost:3000/api/health` | `200 OK` |

## 📋 Production Checklist

Before going live, ensure all items are checked:

### Pre-Deployment
- [ ] Docker secrets configured for all sensitive data
- [ ] SSL certificates installed and valid
- [ ] Port configuration reviewed and customized
- [ ] `.env.prod` configured with production values
- [ ] Secrets directory added to `.gitignore`
- [ ] Backup storage configured

### Security
- [ ] No secrets in environment variables
- [ ] Secret files have restricted permissions (600)
- [ ] SSL/TLS enabled for external access
- [ ] Rate limiting configured
- [ ] Authentication enabled

### Testing
- [ ] All services start successfully
- [ ] Connection validation passes
- [ ] Health checks respond correctly
- [ ] Database connections work
- [ ] API endpoints accessible
- [ ] Monitoring dashboards functional

### Operational
- [ ] Backup schedule configured
- [ ] Log aggregation configured
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team training completed

## 🎯 Next Steps

After successful deployment:

1. **Monitor** system performance and logs
2. **Test** backup and recovery procedures
3. **Configure** alerting for critical issues
4. **Schedule** regular security updates
5. **Document** any customizations

## 📞 Support

- **Documentation**: [MCP Protocol](https://modelcontextprotocol.io)
- **Issues**: GitHub Issues for bug reports
- **Security**: Report security issues privately

---

This deployment follows Docker and Anthropic MCP best practices for security, scalability, and maintainability.