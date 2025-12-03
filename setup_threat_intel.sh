#!/bin/bash
# Enable Threat Intelligence - Quick Setup Guide

echo "🔐 Threat Intelligence Setup"
echo "============================="
echo ""
echo "To enable threat intelligence features, you need API keys from:"
echo ""
echo "1. AbuseIPDB (Free - 1000 requests/day)"
echo "   - Sign up: https://www.abuseipdb.com/register"
echo "   - Get API key: https://www.abuseipdb.com/account/api"
echo ""
echo "2. VirusTotal (Free - 500 requests/day)"
echo "   - Sign up: https://www.virustotal.com/gui/join-us"
echo "   - Get API key: https://www.virustotal.com/gui/user/[your-user]/apikey"
echo ""
echo "============================="
echo ""

# Check current config
CONFIG_FILE="configs/config.yaml"

if [ -f "$CONFIG_FILE" ]; then
    echo "Current threat_intel status:"
    grep -A 15 "threat_intel:" "$CONFIG_FILE" | head -16
    echo ""
    echo "============================="
    echo ""
    echo "To enable:"
    echo "1. Edit: nano configs/config.yaml"
    echo "2. Find the 'threat_intel:' section"
    echo "3. Change 'enabled: false' to 'enabled: true'"
    echo "4. Add your API keys"
    echo ""
    echo "Example:"
    echo "--------"
    cat << 'EOF'
threat_intel:
  enabled: true  # Change this to true
  
  abuseipdb:
    enabled: true  # Change this to true
    api_key: "YOUR_ABUSEIPDB_KEY_HERE"  # Paste your key
    max_age_days: 90
    timeout: 10
    cache_ttl: 3600
  
  virustotal:
    enabled: true  # Change this to true
    api_key: "YOUR_VIRUSTOTAL_KEY_HERE"  # Paste your key
    timeout: 10
    cache_ttl: 3600
EOF
    echo ""
    echo "============================="
    echo ""
    echo "Quick commands:"
    echo "  - Edit config: nano configs/config.yaml"
    echo "  - Or run this to enable (without API keys):"
    echo "    sed -i 's/enabled: false  # Set to true/enabled: true  # Set to true/' configs/config.yaml"
    echo ""
    echo "⚠️  Note: Without API keys, it will be enabled but not functional"
    echo "   You need to add real API keys for it to work!"
    echo ""
else
    echo "❌ Config file not found: $CONFIG_FILE"
fi
