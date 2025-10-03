#!/bin/bash
# ============================================================================
# NeuroForge SSL Certificate Setup Script - Phase 5
# Automated SSL certificate management with Let's Encrypt
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN=${DOMAIN:-"neuroforge.yourdomain.com"}
EMAIL=${EMAIL:-"admin@yourdomain.com"}
STAGING=${STAGING:-false}

# Logging functions
log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARN: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

# Pre-flight checks
preflight_checks() {
    log_info "Running SSL setup pre-flight checks..."

    # Check if running as root or has sudo
    if [[ $EUID -eq 0 ]]; then
        SUDO=""
    elif sudo -n true 2>/dev/null; then
        SUDO="sudo"
    else
        log_error "This script requires root privileges or passwordless sudo"
        exit 1
    fi

    # Check if certbot is installed
    if ! command -v certbot &> /dev/null; then
        log_info "Installing certbot..."
        if [[ -f /etc/debian_version ]]; then
            $SUDO apt-get update
            $SUDO apt-get install -y certbot python3-certbot-nginx
        elif [[ -f /etc/redhat-release ]]; then
            $SUDO yum install -y certbot python3-certbot-nginx
        else
            log_error "Unsupported OS. Please install certbot manually."
            exit 1
        fi
    fi

    # Check domain configuration
    if [[ "$DOMAIN" == "neuroforge.yourdomain.com" ]]; then
        log_warn "Using default domain. Set DOMAIN environment variable for production."
    fi

    # Check if domain resolves
    if ! host "$DOMAIN" &> /dev/null; then
        log_error "Domain $DOMAIN does not resolve. Please configure DNS first."
        exit 1
    fi

    log_success "Pre-flight checks passed"
}

# Create SSL directory structure
create_ssl_structure() {
    log_info "Creating SSL directory structure..."

    $SUDO mkdir -p /etc/ssl/certs
    $SUDO mkdir -p /etc/ssl/private
    $SUDO mkdir -p /var/www/html/.well-known/acme-challenge

    # Set proper permissions
    $SUDO chmod 755 /etc/ssl/certs
    $SUDO chmod 700 /etc/ssl/private

    log_success "SSL directory structure created"
}

# Generate self-signed certificate for initial setup
generate_self_signed() {
    log_info "Generating self-signed certificate for initial setup..."

    $SUDO openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/ssl/private/neuroforge-selfsigned.key \
        -out /etc/ssl/certs/neuroforge-selfsigned.crt \
        -subj "/C=US/ST=State/L=City/O=NeuroForge/CN=$DOMAIN"

    log_success "Self-signed certificate generated"
}

# Obtain Let's Encrypt certificate
obtain_letsencrypt_cert() {
    log_info "Obtaining Let's Encrypt SSL certificate..."

    # Determine certbot command
    CERTBOT_CMD="certbot"

    if [[ "$STAGING" == "true" ]]; then
        CERTBOT_CMD="$CERTBOT_CMD --staging"
        log_warn "Using Let's Encrypt STAGING environment"
    fi

    # Stop nginx temporarily for standalone mode
    if systemctl is-active --quiet nginx; then
        log_info "Stopping nginx for certificate validation..."
        $SUDO systemctl stop nginx
    fi

    # Obtain certificate
    $SUDO $CERTBOT_CMD certonly --standalone \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        --domain "$DOMAIN" \
        --preferred-challenges http-01

    # Start nginx again
    if systemctl is-active --quiet nginx || systemctl is-enabled --quiet nginx; then
        log_info "Starting nginx..."
        $SUDO systemctl start nginx
    fi

    if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
        log_success "Let's Encrypt certificate obtained successfully"
    else
        log_error "Failed to obtain Let's Encrypt certificate"
        exit 1
    fi
}

# Configure automatic renewal
setup_auto_renewal() {
    log_info "Setting up automatic certificate renewal..."

    # Create renewal script
    cat << 'EOF' | $SUDO tee /etc/cron.daily/certbot-renew > /dev/null
#!/bin/bash
# NeuroForge SSL Certificate Renewal Script

# Renew certificates
certbot renew --quiet

# Reload nginx if certificates were renewed
if [[ -f /etc/letsencrypt/live/neuroforge.yourdomain.com/fullchain.pem ]]; then
    systemctl reload nginx
fi
EOF

    $SUDO chmod +x /etc/cron.daily/certbot-renew

    # Test renewal
    log_info "Testing certificate renewal..."
    $SUDO certbot renew --dry-run

    log_success "Automatic renewal configured"
}

# Update NGINX configuration
update_nginx_config() {
    log_info "Updating NGINX configuration for SSL..."

    # Check if we have Let's Encrypt cert
    if [[ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]]; then
        SSL_CERT="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
        SSL_KEY="/etc/letsencrypt/live/$DOMAIN/privkey.pem"
        log_info "Using Let's Encrypt certificate"
    else
        SSL_CERT="/etc/ssl/certs/neuroforge-selfsigned.crt"
        SSL_KEY="/etc/ssl/private/neuroforge-selfsigned.key"
        log_warn "Using self-signed certificate"
    fi

    # Update nginx configuration
    NGINX_CONF="/etc/nginx/sites-available/neuroforge"

    cat << EOF | $SUDO tee "$NGINX_CONF" > /dev/null
# NeuroForge SSL Configuration
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;

    # SSL Configuration
    ssl_certificate $SSL_CERT;
    ssl_certificate_key $SSL_KEY;

    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # HSTS (only enable after thorough testing)
    # add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Rate Limiting
    limit_req zone=api burst=20 nodelay;
    limit_req zone=frontend burst=50 nodelay;

    # Upstream backends
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;

        proxy_connect_timeout 10s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # ACME challenge for Let's Encrypt
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        try_files \$uri =404;
    }
}
EOF

    # Enable site
    $SUDO ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/

    # Test configuration
    log_info "Testing NGINX configuration..."
    $SUDO nginx -t

    # Reload nginx
    log_info "Reloading NGINX..."
    $SUDO systemctl reload nginx

    log_success "NGINX SSL configuration updated"
}

# Main setup function
setup_ssl() {
    log_info "🚀 Starting NeuroForge SSL Certificate Setup"
    log_info "Domain: $DOMAIN"
    log_info "Email: $EMAIL"
    log_info "Staging: $STAGING"

    preflight_checks
    create_ssl_structure
    generate_self_signed

    if [[ "$STAGING" != "true" ]]; then
        obtain_letsencrypt_cert
        setup_auto_renewal
    else
        log_warn "Skipping Let's Encrypt (staging mode)"
    fi

    update_nginx_config

    log_success "🎉 SSL setup completed!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Update your DNS to point $DOMAIN to this server"
    log_info "2. Test SSL: https://$DOMAIN/health"
    log_info "3. Configure firewall to allow ports 80, 443"
    if [[ "$STAGING" == "true" ]]; then
        log_info "4. Run again with STAGING=false for production certificates"
    fi
}

# Show usage
usage() {
    echo "NeuroForge SSL Certificate Setup Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -d, --domain DOMAIN    Domain name (default: neuroforge.yourdomain.com)"
    echo "  -e, --email EMAIL      Email for Let's Encrypt (default: admin@yourdomain.com)"
    echo "  -s, --staging          Use Let's Encrypt staging environment"
    echo "  -h, --help            Show this help"
    echo ""
    echo "Environment Variables:"
    echo "  DOMAIN                Domain name"
    echo "  EMAIL                 Email address"
    echo "  STAGING               Set to 'true' for staging certificates"
    echo ""
    echo "Examples:"
    echo "  $0 --domain neuroforge.example.com --email admin@example.com"
    echo "  $0 --staging  # For testing"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -s|--staging)
            STAGING=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Run setup
setup_ssl
