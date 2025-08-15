# MCP System Deployment Guide

This guide covers deployment strategies for MCP System across different environments and use cases.

## 🚀 Deployment Overview

MCP System supports multiple deployment scenarios:

- **Development**: Local development with hot-reloading
- **Production**: Stable deployment with monitoring
- **Container**: Docker-based deployments
- **CI/CD**: Automated testing and deployment
- **Multi-user**: Team and organization deployments

## 🏠 Local Development Deployment

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system

# Setup development environment
./scripts/setup_dev.sh

# Activate development environment
source venv/bin/activate
export PATH="$HOME/bin:$PATH"
```

### Development Configuration

Create `.env.dev`:
```bash
# Development environment
MCP_ENV=development
MCP_DEBUG=true
MCP_AUTO_RELOAD=true
MCP_LOG_LEVEL=debug

# Development paths
MCP_SYSTEM_PATH="$HOME/.mcp-system-dev"
MCP_AUTO_DISCOVERY=true
MCP_SAFE_MODE=false

# Development servers
DEFAULT_PORT_START=8050
DEFAULT_TEMPLATE=python-fastmcp
```

### Hot-Reloading Development

```bash
# Start with auto-reload
MCP_AUTO_RELOAD=true mcp-universal create dev-server --template python-fastmcp

# Monitor changes
mcp-universal dev-server logs --follow

# Test changes automatically
mcp-universal test dev-server --watch
```

## 🏭 Production Deployment

### Production Prerequisites

```bash
# System dependencies
sudo apt update
sudo apt install -y python3.12 python3-pip git nodejs npm
sudo apt install -y postgresql redis-server nginx supervisor

# Security tools
sudo apt install -y fail2ban ufw
```

### Production Installation

```bash
# Create production user
sudo useradd -m -s /bin/bash mcpsystem
sudo usermod -aG docker mcpsystem

# Install as production user
sudo -u mcpsystem bash << 'EOF'
cd /home/mcpsystem
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system
./install.sh
EOF
```

### Production Configuration

Create `/home/mcpsystem/.mcp-system/.env.prod`:
```bash
# Production environment
MCP_ENV=production
MCP_DEBUG=false
MCP_AUTO_RELOAD=false
MCP_LOG_LEVEL=warning
MCP_SAFE_MODE=true

# Production paths
MCP_SYSTEM_PATH="/home/mcpsystem/.mcp-system"
MCP_DATA_PATH="/var/lib/mcp-system"
MCP_LOG_PATH="/var/log/mcp-system"

# Security
MCP_REQUIRE_AUTH=true
MCP_RATE_LIMIT=true
MCP_HTTPS_ONLY=true

# Database
DATABASE_URL=postgresql://mcpuser:password@localhost:5432/mcpsystem
REDIS_URL=redis://localhost:6379/0

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
LOG_TO_SYSLOG=true
```

### Systemd Service Configuration

Create `/etc/systemd/system/mcp-system.service`:
```ini
[Unit]
Description=MCP System Universal Launcher
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=forking
User=mcpsystem
Group=mcpsystem
WorkingDirectory=/home/mcpsystem
Environment=PATH=/home/mcpsystem/bin:/usr/local/bin:/usr/bin:/bin
Environment=MCP_ENV=production
EnvironmentFile=/home/mcpsystem/.mcp-system/.env.prod
ExecStart=/home/mcpsystem/bin/mcp-universal all start --daemon
ExecStop=/home/mcpsystem/bin/mcp-universal all stop
ExecReload=/home/mcpsystem/bin/mcp-universal all restart
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Nginx Configuration

Create `/etc/nginx/sites-available/mcp-system`:
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name mcp.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name mcp.yourdomain.com;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/mcp.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.yourdomain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=mcp:10m rate=10r/s;
    limit_req zone=mcp burst=20 nodelay;
    
    # MCP Server proxying
    location /api/ {
        proxy_pass http://localhost:8050/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8050/health;
        access_log off;
    }
    
    # Metrics endpoint (restricted)
    location /metrics {
        proxy_pass http://localhost:9090/metrics;
        allow 10.0.0.0/8;
        allow 172.16.0.0/12;
        allow 192.168.0.0/16;
        deny all;
    }
}
```

### SSL Certificate Setup

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d mcp.yourdomain.com

# Setup auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Start Production Services

```bash
# Enable and start services
sudo systemctl enable mcp-system
sudo systemctl start mcp-system

# Enable Nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status mcp-system
sudo systemctl status nginx
```

## 🐳 Docker Deployment

### Single Container Deployment

#### Build Custom Image

```dockerfile
# Dockerfile.production
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -m -u 1000 mcpuser
WORKDIR /app
USER mcpuser

# Copy and install application
COPY --chown=mcpuser:mcpuser . .
RUN pip install --user -r requirements.txt
RUN ./install.sh

# Set environment
ENV PATH="/home/mcpuser/.local/bin:/home/mcpuser/bin:$PATH"
ENV MCP_SYSTEM_PATH="/home/mcpuser/.mcp-system"
ENV MCP_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD mcp-universal status || exit 1

# Expose ports
EXPOSE 8050-8060

# Start command
CMD ["mcp-universal", "all", "start", "--foreground"]
```

#### Build and Run

```bash
# Build image
docker build -f Dockerfile.production -t mcp-system:production .

# Run container
docker run -d \
    --name mcp-system \
    --restart unless-stopped \
    -p 8050-8060:8050-8060 \
    -v mcp_data:/home/mcpuser/.mcp-system \
    -v mcp_logs:/var/log/mcp-system \
    -e MCP_ENV=production \
    mcp-system:production
```

### Docker Compose Deployment

#### Production Stack

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  mcp-system:
    build:
      context: .
      dockerfile: Dockerfile.production
    restart: unless-stopped
    ports:
      - "8050-8060:8050-8060"
    environment:
      - MCP_ENV=production
      - DATABASE_URL=postgresql://mcpuser:${DB_PASSWORD}@postgres:5432/mcpsystem
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - mcp_data:/home/mcpuser/.mcp-system
      - mcp_logs:/var/log/mcp-system
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "mcp-universal", "status"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=mcpsystem
      - POSTGRES_USER=mcpuser
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcpuser"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/ssl/certs:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - mcp-system

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  mcp_data:
  mcp_logs:
  postgres_data:
  redis_data:
  nginx_logs:
  prometheus_data:
  grafana_data:
```

#### Environment Configuration

Create `.env.prod`:
```bash
# Database
DB_PASSWORD=your_secure_db_password

# Grafana
GRAFANA_PASSWORD=your_secure_grafana_password

# SSL/TLS
SSL_CERT_PATH=/etc/ssl/certs/mcp.crt
SSL_KEY_PATH=/etc/ssl/private/mcp.key
```

#### Deploy Stack

```bash
# Deploy production stack
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f mcp-system
```

## ☸️ Kubernetes Deployment

### Namespace and ConfigMap

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-system
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
  namespace: mcp-system
data:
  MCP_ENV: "production"
  MCP_SAFE_MODE: "true"
  MCP_AUTO_DISCOVERY: "true"
  DEFAULT_PORT_START: "8050"
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-system
  namespace: mcp-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-system
  template:
    metadata:
      labels:
        app: mcp-system
    spec:
      containers:
      - name: mcp-system
        image: dezocode/mcp-system:latest
        ports:
        - containerPort: 8050
        - containerPort: 9090
        envFrom:
        - configMapRef:
            name: mcp-config
        - secretRef:
            name: mcp-secrets
        volumeMounts:
        - name: mcp-data
          mountPath: /home/mcpuser/.mcp-system
        livenessProbe:
          exec:
            command:
            - mcp-universal
            - status
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8050
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: mcp-data
        persistentVolumeClaim:
          claimName: mcp-data-pvc
```

### Service and Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-system-service
  namespace: mcp-system
spec:
  selector:
    app: mcp-system
  ports:
  - name: http
    port: 80
    targetPort: 8050
  - name: metrics
    port: 9090
    targetPort: 9090
  type: ClusterIP
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-system-ingress
  namespace: mcp-system
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - mcp.yourdomain.com
    secretName: mcp-tls
  rules:
  - host: mcp.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-system-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f pvc.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check deployment
kubectl get pods -n mcp-system
kubectl logs -f deployment/mcp-system -n mcp-system
```

## 🔄 CI/CD Deployment

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy MCP System

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        ./install.sh
    - name: Run tests
      run: |
        python scripts/test_installation.py

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build Docker image
      run: |
        docker build -t ${{ secrets.REGISTRY }}/mcp-system:${{ github.sha }} .
        docker build -t ${{ secrets.REGISTRY }}/mcp-system:latest .
    - name: Push to registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login ${{ secrets.REGISTRY }} -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
        docker push ${{ secrets.REGISTRY }}/mcp-system:${{ github.sha }}
        docker push ${{ secrets.REGISTRY }}/mcp-system:latest

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        kubectl set image deployment/mcp-system mcp-system=${{ secrets.REGISTRY }}/mcp-system:${{ github.sha }} -n mcp-staging

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    steps:
    - name: Deploy to production
      run: |
        # Deploy to production environment
        kubectl set image deployment/mcp-system mcp-system=${{ secrets.REGISTRY }}/mcp-system:${{ github.sha }} -n mcp-production
```

### GitLab CI/CD Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"

test:
  stage: test
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - ./install.sh
    - python scripts/test_installation.py

build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE:latest .
    - echo $CI_REGISTRY_PASSWORD | docker login $CI_REGISTRY -u $CI_REGISTRY_USER --password-stdin
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE:latest

deploy-staging:
  stage: deploy
  environment: staging
  script:
    - kubectl set image deployment/mcp-system mcp-system=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n mcp-staging
  only:
    - main

deploy-production:
  stage: deploy
  environment: production
  script:
    - kubectl set image deployment/mcp-system mcp-system=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA -n mcp-production
  only:
    - tags
  when: manual
```

## 👥 Multi-User Deployment

### Team Configuration

```bash
# Create team configuration
sudo mkdir -p /etc/mcp-system/teams
sudo tee /etc/mcp-system/teams/team-config.yaml << 'EOF'
teams:
  development:
    members: ["dev1", "dev2", "dev3"]
    servers: ["dev-api", "test-tools"]
    permissions: ["create", "test", "upgrade"]
    
  production:
    members: ["ops1", "ops2"]
    servers: ["prod-api"]
    permissions: ["deploy", "monitor"]
    
  qa:
    members: ["qa1", "qa2"]
    servers: ["qa-api", "test-api"]
    permissions: ["test", "monitor"]
EOF
```

### User Management

```bash
# Create team users
for user in dev1 dev2 dev3 qa1 qa2 ops1 ops2; do
    sudo useradd -m -s /bin/bash $user
    sudo usermod -aG mcp-users $user
done

# Install for each user
for user in dev1 dev2 dev3 qa1 qa2 ops1 ops2; do
    sudo -u $user bash << 'EOF'
cd ~
git clone https://github.com/dezocode/mcp-system.git
cd mcp-system
./install.sh
EOF
done
```

### Access Control

```bash
# Setup team-based access control
sudo tee /etc/mcp-system/access-control.yaml << 'EOF'
access_control:
  enabled: true
  default_permissions: ["read"]
  
  team_permissions:
    development:
      - read
      - write
      - test
      - create_server
      - upgrade_server
    
    production:
      - read
      - deploy
      - monitor
      - emergency_stop
    
    qa:
      - read
      - test
      - monitor
EOF
```

## 📊 Monitoring and Logging

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'mcp-system'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'mcp-servers'
    static_configs:
      - targets: ['localhost:8050', 'localhost:8051', 'localhost:8052']
    scrape_interval: 30s
    metrics_path: /metrics

rule_files:
  - "mcp_alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "MCP System Dashboard",
    "panels": [
      {
        "title": "Active Servers",
        "type": "stat",
        "targets": [
          {
            "expr": "mcp_servers_active",
            "legendFormat": "Active Servers"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mcp_requests_total[5m])",
            "legendFormat": "{{server}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(mcp_errors_total[5m])",
            "legendFormat": "{{server}}"
          }
        ]
      }
    ]
  }
}
```

### Log Aggregation

```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/mcp-system/*.log
  fields:
    service: mcp-system
  multiline.pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
  multiline.negate: true
  multiline.match: after

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "mcp-system-%{+yyyy.MM.dd}"

logging.level: info
```

## 🔒 Security Hardening

### Firewall Configuration

```bash
# UFW configuration
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from 10.0.0.0/8 to any port 9090  # Prometheus
sudo ufw enable
```

### Security Scanning

```bash
# Vulnerability scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image dezocode/mcp-system:latest

# Security benchmarks
docker run --rm --net host --pid host --userns host --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /etc:/etc:ro \
  -v /usr/bin/containerd:/usr/bin/containerd:ro \
  -v /usr/bin/runc:/usr/bin/runc:ro \
  -v /usr/lib/systemd:/usr/lib/systemd:ro \
  -v /var/lib:/var/lib:ro \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  --label docker_bench_security \
  docker/docker-bench-security
```

## 🚨 Disaster Recovery

### Backup Strategy

```bash
#!/bin/bash
# backup-mcp-system.sh

BACKUP_DIR="/backups/mcp-system/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r /home/mcpsystem/.mcp-system "$BACKUP_DIR/config"

# Backup databases
pg_dump mcpsystem > "$BACKUP_DIR/database.sql"

# Backup Redis data
redis-cli --rdb "$BACKUP_DIR/redis.rdb"

# Backup logs
cp -r /var/log/mcp-system "$BACKUP_DIR/logs"

# Create archive
tar -czf "$BACKUP_DIR.tar.gz" -C "$BACKUP_DIR" .
rm -rf "$BACKUP_DIR"

echo "Backup completed: $BACKUP_DIR.tar.gz"
```

### Recovery Procedures

```bash
#!/bin/bash
# restore-mcp-system.sh

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/mcp-restore"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.tar.gz>"
    exit 1
fi

# Extract backup
mkdir -p "$RESTORE_DIR"
tar -xzf "$BACKUP_FILE" -C "$RESTORE_DIR"

# Stop services
sudo systemctl stop mcp-system

# Restore configuration
sudo cp -r "$RESTORE_DIR/config" /home/mcpsystem/.mcp-system

# Restore database
psql mcpsystem < "$RESTORE_DIR/database.sql"

# Restore Redis data
sudo systemctl stop redis
sudo cp "$RESTORE_DIR/redis.rdb" /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb
sudo systemctl start redis

# Start services
sudo systemctl start mcp-system

echo "Restore completed from: $BACKUP_FILE"
```

---

This deployment guide provides comprehensive coverage for deploying MCP System across different environments. Choose the deployment strategy that best fits your needs and scale requirements.