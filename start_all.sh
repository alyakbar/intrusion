#!/bin/bash

# Network Anomaly Detection System - Full Stack Launcher
# This script starts all components in separate terminal windows

PROJECT_ROOT="/home/non/Desktop/New Folder/khan/network-anomaly-project"
cd "$PROJECT_ROOT"

echo "🚀 Starting Network Anomaly Detection System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Function to open terminal and run command
run_in_new_terminal() {
    local title="$1"
    local command="$2"
    
    # Try gnome-terminal first (Ubuntu/Debian)
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal --title="$title" -- bash -c "$command; exec bash"
    # Try xterm as fallback
    elif command -v xterm &> /dev/null; then
        xterm -title "$title" -e "$command; bash" &
    # Try konsole (KDE)
    elif command -v konsole &> /dev/null; then
        konsole --new-tab -e bash -c "$command; exec bash" &
    else
        echo "⚠️  Could not find terminal emulator. Please run commands manually."
        echo "Command: $command"
    fi
}

echo "1️⃣  Starting API Server..."
run_in_new_terminal "API Server (Port 5000)" \
    "cd '$PROJECT_ROOT' && source venv/bin/activate && echo '🌐 API Server starting on http://localhost:5000' && python api_server.py"

sleep 2

echo "2️⃣  Starting Detection System..."
run_in_new_terminal "Detection System" \
    "cd '$PROJECT_ROOT' && source venv/bin/activate && echo '🔍 Starting real-time detection with 20% anomalies...' && python anomaly_detection/main.py --mode detect --model random_forest --interface lo --inject-rate 0.2 --synthetic-delay 0.1"

sleep 2

echo "3️⃣  Starting Frontend Dashboard..."
run_in_new_terminal "Next.js Frontend (Port 3000)" \
    "cd '$PROJECT_ROOT/frontend' && echo '🎨 Frontend starting on http://localhost:3000' && npm run dev"

sleep 3

echo ""
echo "✅ All components started!"
echo ""
echo "📊 Access Points:"
echo "   • Next.js Dashboard: http://localhost:3000"
echo "   • Flask API:         http://localhost:5000"
echo "   • API Health Check:  http://localhost:5000/health"
echo ""
echo "💡 Wait 30 seconds for detection data to populate, then refresh the dashboard."
echo ""
echo "🛑 To stop: Close the terminal windows or press Ctrl+C in each"
echo ""

# Wait for user
read -p "Press Enter to test API connection..."

echo ""
echo "Testing API..."
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ API is responding"
    curl -s http://localhost:5000/api/detections/stats | python -m json.tool 2>/dev/null || echo "No data yet - run detection for 30 seconds"
else
    echo "⚠️  API not responding yet. Wait a moment and try: curl http://localhost:5000/health"
fi

echo ""
echo "🎉 System is running! Check the dashboard at http://localhost:3000"
