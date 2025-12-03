#!/bin/bash
# Quick guide to restart detection after WiFi issues

echo "🔄 Detection Restart Guide"
echo "=========================="
echo ""
echo "If detection stops capturing after WiFi toggling, restart it:"
echo ""
echo "1. Stop current detection (in Terminal where it's running):"
echo "   Press Ctrl+C"
echo ""
echo "2. Restart detection:"
echo "   ./start_realtime_detection.sh"
echo ""
echo "3. The new version has improved recovery that should handle"
echo "   WiFi toggling better by automatically recreating the capture."
echo ""
echo "=========================="
echo ""
echo "Current status:"
./check_status.sh
