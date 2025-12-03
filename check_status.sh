#!/bin/bash
# Quick status check
echo "📊 Current System Status"
echo "======================="
STATUS=$(curl -s http://localhost:5000/api/system/status)
echo "$STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Status: {d['status'].upper()} - {d['status_message']}\")
if d['interface_info']:
    print(f\"Interface: {d['interface_info']['name']} ({d['interface_info']['status']}) - IP: {d['interface_info'].get('ip', 'None')}\")
print(f\"Capturing: {'YES' if d['is_capturing_packets'] else 'NO'}\")
print(f\"Recent packets (30s): {d['recent_packets_30s']}\")
if d['process_info']:
    print(f\"Backend: {d['process_info']['backend']}\")
    print(f\"Inject rate: {d['process_info']['inject_rate']} (0.0 = real packets)\")
"
