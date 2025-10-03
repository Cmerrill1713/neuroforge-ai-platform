#!/bin/bash

# Home Assistant Local Setup Script
# This script automatically sets up Home Assistant using Docker

set -e

echo "🏠 HOME ASSISTANT LOCAL SETUP"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_status "Docker is running"
}

# Create necessary directories
create_directories() {
    print_info "Creating directories..."
    
    mkdir -p config
    mkdir -p mosquitto/config
    mkdir -p mosquitto/data
    mkdir -p mosquitto/log
    mkdir -p influxdb
    mkdir -p grafana
    
    print_status "Directories created"
}

# Set proper permissions
set_permissions() {
    print_info "Setting permissions..."
    
    # Make sure Home Assistant can write to config directory
    chmod 755 config
    chmod 755 mosquitto
    chmod 755 influxdb
    chmod 755 grafana
    
    print_status "Permissions set"
}

# Start Home Assistant
start_homeassistant() {
    print_info "Starting Home Assistant..."
    
    # Pull the latest image
    docker-compose pull homeassistant
    
    # Start the services
    docker-compose up -d homeassistant
    
    print_status "Home Assistant is starting..."
    print_info "This may take a few minutes on first startup"
}

# Start additional services
start_services() {
    print_info "Starting additional services..."
    
    # Start MQTT broker
    docker-compose up -d mosquitto
    print_status "Mosquitto MQTT broker started"
    
    # Start InfluxDB
    docker-compose up -d influxdb
    print_status "InfluxDB started"
    
    # Start Grafana
    docker-compose up -d grafana
    print_status "Grafana started"
}

# Wait for services to be ready
wait_for_services() {
    print_info "Waiting for services to be ready..."
    
    # Wait for Home Assistant
    echo "Waiting for Home Assistant to be ready..."
    timeout=300  # 5 minutes
    counter=0
    
    while [ $counter -lt $timeout ]; do
        if curl -s http://localhost:8123 > /dev/null 2>&1; then
            print_status "Home Assistant is ready!"
            break
        fi
        
        echo -n "."
        sleep 5
        counter=$((counter + 5))
    done
    
    if [ $counter -ge $timeout ]; then
        print_warning "Home Assistant took longer than expected to start"
        print_info "Check logs with: docker-compose logs homeassistant"
    fi
}

# Display access information
show_access_info() {
    echo ""
    echo "🎉 HOME ASSISTANT SETUP COMPLETE!"
    echo "================================="
    echo ""
    echo "📱 Access URLs:"
    echo "   Home Assistant: http://localhost:8123"
    echo "   Grafana:        http://localhost:3001"
    echo "   InfluxDB:       http://localhost:8086"
    echo ""
    echo "🔧 MQTT Broker:"
    echo "   Host: localhost"
    echo "   Port: 1883"
    echo "   WebSocket: ws://localhost:9001"
    echo ""
    echo "📊 Default Credentials:"
    echo "   Grafana: admin / homeassistant123"
    echo "   InfluxDB: admin / homeassistant123"
    echo ""
    echo "🛠️  Management Commands:"
    echo "   Start:   docker-compose up -d"
    echo "   Stop:    docker-compose down"
    echo "   Logs:    docker-compose logs -f homeassistant"
    echo "   Restart: docker-compose restart homeassistant"
    echo ""
    echo "📁 Configuration:"
    echo "   Home Assistant config: ./config/"
    echo "   MQTT config:           ./mosquitto/config/"
    echo ""
    print_info "First-time setup: Visit http://localhost:8123 to complete the initial configuration"
}

# Main execution
main() {
    echo "Starting Home Assistant setup..."
    
    check_docker
    create_directories
    set_permissions
    start_homeassistant
    start_services
    wait_for_services
    show_access_info
    
    print_status "Setup complete! Home Assistant is ready to use."
}

# Run main function
main "$@"
