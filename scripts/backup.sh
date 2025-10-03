#!/bin/bash
# Backup Script for AI Assistant Platform

set -e

BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai_assistant_backup_${TIMESTAMP}"

echo "💾 Creating backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Backup knowledge base
if [ -d "knowledge_base" ]; then
    echo "📚 Backing up knowledge base..."
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_knowledge.tar.gz" knowledge_base/
fi

# Backup logs
if [ -d "logs" ]; then
    echo "📝 Backing up logs..."
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_logs.tar.gz" logs/
fi

# Backup configuration
echo "⚙️ Backing up configuration..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}_config.tar.gz"     docker-compose.yml     nginx.conf     .env.production     logging_config.json

echo "✅ Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}_*.tar.gz"
