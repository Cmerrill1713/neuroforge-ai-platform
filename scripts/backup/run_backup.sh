#!/bin/bash
# ============================================================================
# NeuroForge Automated Backup Script - Phase 5
# Comprehensive backup solution for production data
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKUP_ROOT="/app/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="neuroforge_backup_${TIMESTAMP}"
BACKUP_DIR="${BACKUP_ROOT}/${BACKUP_NAME}"

# Database configuration
DB_HOST=${DB_HOST:-"neuroforge-postgres"}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-neuroforge}
DB_USER=${DB_USER:-neuroforge}
DB_PASSWORD=${POSTGRES_PASSWORD}

# S3 configuration
S3_BUCKET=${BACKUP_S3_BUCKET}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-1}

# Retention
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

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

# Create backup directory
create_backup_dir() {
    log_info "Creating backup directory: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/configs"
    mkdir -p "$BACKUP_DIR/uploads"
    mkdir -p "$BACKUP_DIR/knowledge_base"
}

# Backup PostgreSQL database
backup_database() {
    log_info "Backing up PostgreSQL database..."

    export PGPASSWORD="$DB_PASSWORD"

    # Create database dump
    pg_dump \
        --host="$DB_HOST" \
        --port="$DB_PORT" \
        --username="$DB_USER" \
        --dbname="$DB_NAME" \
        --format=custom \
        --compress=9 \
        --verbose \
        --file="$BACKUP_DIR/database/neuroforge.sql"

    log_success "Database backup completed"
}

# Backup Redis data
backup_redis() {
    log_info "Backing up Redis data..."

    # Use redis-cli to save RDB file
    docker exec neuroforge-redis redis-cli SAVE

    # Copy RDB file from container
    docker cp neuroforge-redis:/data/dump.rdb "$BACKUP_DIR/redis_dump.rdb"

    log_success "Redis backup completed"
}

# Backup Weaviate data
backup_weaviate() {
    log_info "Backing up Weaviate data..."

    # Copy Weaviate data directory
    if docker ps -q -f name=neuroforge-weaviate | grep -q .; then
        docker cp neuroforge-weaviate:/var/lib/weaviate "$BACKUP_DIR/weaviate_data"
        log_success "Weaviate backup completed"
    else
        log_warn "Weaviate container not running, skipping backup"
    fi
}

# Backup application data
backup_application_data() {
    log_info "Backing up application data..."

    # Knowledge base
    if [[ -d "/app/knowledge_base" ]]; then
        cp -r /app/knowledge_base "$BACKUP_DIR/"
        log_info "Knowledge base backed up"
    fi

    # Uploads directory
    if [[ -d "/app/uploads" ]]; then
        cp -r /app/uploads "$BACKUP_DIR/"
        log_info "Uploads directory backed up"
    fi

    # Configs
    if [[ -d "/app/configs" ]]; then
        cp -r /app/configs "$BACKUP_DIR/"
        log_info "Configuration files backed up"
    fi
}

# Backup Docker volumes
backup_volumes() {
    log_info "Backing up Docker volumes..."

    # List of volumes to backup
    VOLUMES=("postgres_data" "redis_data" "weaviate_data")

    for volume in "${VOLUMES[@]}"; do
        if docker volume ls -q | grep -q "^neuroforge_$volume$"; then
            log_info "Backing up volume: $volume"
            docker run --rm \
                -v "neuroforge_$volume:/source" \
                -v "$BACKUP_DIR:/backup" \
                alpine:latest \
                tar czf "/backup/${volume}.tar.gz" -C /source .
        fi
    done

    log_success "Volume backups completed"
}

# Create backup manifest
create_manifest() {
    log_info "Creating backup manifest..."

    MANIFEST_FILE="$BACKUP_DIR/manifest.json"

    cat << EOF > "$MANIFEST_FILE"
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$TIMESTAMP",
  "created_at": "$(date -Iseconds)",
  "version": "1.0",
  "components": {
    "database": {
      "type": "postgresql",
      "host": "$DB_HOST",
      "database": "$DB_NAME",
      "size": "$(du -sh "$BACKUP_DIR/database" 2>/dev/null | cut -f1 || echo "unknown")"
    },
    "redis": {
      "type": "redis",
      "size": "$(du -sh "$BACKUP_DIR/redis_dump.rdb" 2>/dev/null | cut -f1 || echo "unknown")"
    },
    "weaviate": {
      "type": "weaviate",
      "size": "$(du -sh "$BACKUP_DIR/weaviate_data" 2>/dev/null | cut -f1 || echo "unknown")"
    },
    "knowledge_base": {
      "size": "$(du -sh "$BACKUP_DIR/knowledge_base" 2>/dev/null | cut -f1 || echo "unknown")"
    },
    "uploads": {
      "size": "$(du -sh "$BACKUP_DIR/uploads" 2>/dev/null | cut -f1 || echo "unknown")"
    },
    "configs": {
      "size": "$(du -sh "$BACKUP_DIR/configs" 2>/dev/null | cut -f1 || echo "unknown")"
    }
  },
  "total_size": "$(du -sh "$BACKUP_DIR" | cut -f1)",
  "retention_days": $RETENTION_DAYS
}
EOF

    log_success "Backup manifest created"
}

# Compress backup
compress_backup() {
    log_info "Compressing backup..."

    ARCHIVE_NAME="${BACKUP_NAME}.tar.gz"
    ARCHIVE_PATH="${BACKUP_ROOT}/${ARCHIVE_NAME}"

    # Create compressed archive
    tar -czf "$ARCHIVE_PATH" -C "$BACKUP_ROOT" "$BACKUP_NAME"

    # Calculate checksum
    sha256sum "$ARCHIVE_PATH" > "${ARCHIVE_PATH}.sha256"

    # Remove uncompressed backup
    rm -rf "$BACKUP_DIR"

    log_success "Backup compressed: $ARCHIVE_NAME ($(du -sh "$ARCHIVE_PATH" | cut -f1))"
}

# Upload to S3
upload_to_s3() {
    if [[ -n "$S3_BUCKET" && -n "$AWS_ACCESS_KEY_ID" ]]; then
        log_info "Uploading backup to S3..."

        ARCHIVE_NAME="${BACKUP_NAME}.tar.gz"
        ARCHIVE_PATH="${BACKUP_ROOT}/${ARCHIVE_NAME}"

        # Upload archive
        aws s3 cp "$ARCHIVE_PATH" "s3://$S3_BUCKET/backups/$ARCHIVE_NAME" --region "$AWS_DEFAULT_REGION"

        # Upload checksum
        aws s3 cp "${ARCHIVE_PATH}.sha256" "s3://$S3_BUCKET/backups/${ARCHIVE_NAME}.sha256" --region "$AWS_DEFAULT_REGION"

        log_success "Backup uploaded to S3: s3://$S3_BUCKET/backups/$ARCHIVE_NAME"
    else
        log_warn "S3 configuration not provided, skipping upload"
    fi
}

# Cleanup old backups
cleanup_old_backups() {
    log_info "Cleaning up old backups (retention: $RETENTION_DAYS days)..."

    # Local cleanup
    find "$BACKUP_ROOT" -name "neuroforge_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_ROOT" -name "*.sha256" -mtime +$RETENTION_DAYS -delete

    # S3 cleanup (if configured)
    if [[ -n "$S3_BUCKET" && -n "$AWS_ACCESS_KEY_ID" ]]; then
        log_info "Cleaning up old S3 backups..."
        aws s3 rm "s3://$S3_BUCKET/backups/" \
            --recursive \
            --exclude "*" \
            --include "neuroforge_backup_*.tar.gz" \
            --include "*.sha256" \
            --region "$AWS_DEFAULT_REGION"
    fi

    log_success "Old backup cleanup completed"
}

# Send notification
send_notification() {
    local status="$1"
    local message="$2"

    log_info "Sending backup notification..."

    # Slack notification
    if [[ -n "$SLACK_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"NeuroForge Backup $status: $message\"}" \
            "$SLACK_WEBHOOK_URL" || true
    fi

    # Discord notification
    if [[ -n "$DISCORD_WEBHOOK_URL" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"content\":\"NeuroForge Backup $status: $message\"}" \
            "$DISCORD_WEBHOOK_URL" || true
    fi
}

# Main backup function
perform_backup() {
    log_info "🚀 Starting NeuroForge Backup Process"

    # Create backup directory
    create_backup_dir

    # Perform backups
    backup_database
    backup_redis
    backup_weaviate
    backup_application_data
    backup_volumes

    # Create manifest
    create_manifest

    # Compress
    compress_backup

    # Upload to cloud
    upload_to_s3

    # Cleanup
    cleanup_old_backups

    # Calculate backup size
    ARCHIVE_SIZE=$(du -sh "${BACKUP_ROOT}/${BACKUP_NAME}.tar.gz" | cut -f1)

    log_success "🎉 NeuroForge backup completed successfully!"
    log_info "Backup size: $ARCHIVE_SIZE"
    log_info "Backup location: ${BACKUP_ROOT}/${BACKUP_NAME}.tar.gz"

    # Send success notification
    send_notification "SUCCESS" "Backup completed - Size: $ARCHIVE_SIZE"
}

# Verify backup integrity
verify_backup() {
    log_info "Verifying backup integrity..."

    ARCHIVE_NAME="${BACKUP_NAME}.tar.gz"
    ARCHIVE_PATH="${BACKUP_ROOT}/${ARCHIVE_NAME}"

    # Verify checksum
    if [[ -f "${ARCHIVE_PATH}.sha256" ]]; then
        if sha256sum -c "${ARCHIVE_PATH}.sha256"; then
            log_success "Backup integrity verified"
            return 0
        else
            log_error "Backup integrity check failed!"
            return 1
        fi
    else
        log_warn "Checksum file not found, skipping integrity check"
        return 0
    fi
}

# Main execution
main() {
    # Trap errors
    trap 'send_notification "FAILED" "Backup process failed at $(date)"' ERR

    # Run backup
    perform_backup

    # Verify backup
    if verify_backup; then
        log_success "Backup verification passed"
    else
        log_error "Backup verification failed"
        exit 1
    fi

    log_info "NeuroForge backup process completed successfully"
}

# Run main function
main "$@"
