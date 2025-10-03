#!/bin/bash
# Health Check Script for AI Assistant Platform

echo "🏥 Running health checks..."

# Check API health
echo "🔌 Checking API health..."
if curl -f http://localhost:8004/api/system/health > /dev/null 2>&1; then
    echo "✅ API is healthy"
else
    echo "❌ API is not responding"
    exit 1
fi

# Check frontend health
echo "📱 Checking frontend health..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is not responding"
    exit 1
fi

# Check performance metrics
echo "📊 Checking performance metrics..."
if curl -f http://localhost:8004/api/system/performance-report > /dev/null 2>&1; then
    echo "✅ Performance metrics available"
else
    echo "⚠️ Performance metrics not available"
fi

echo "🎉 All health checks passed!"
