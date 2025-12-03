# 🚀 Advanced Features - Quick Start Guide

All advanced features are now integrated into both **backend** and **frontend**!

## 🎯 Access the Features

### Frontend Dashboard
```bash
# Start everything
./start_advanced.sh

# Then visit:
# Main Dashboard:    http://localhost:3000
# Advanced Features: http://localhost:3000/advanced
```

### Command Line
```bash
# See all available options
python anomaly_detection/main.py --help
```

---

## 🌟 Feature Overview

### 1. 🛡️ Threat Intelligence
**What it does:** Enriches detections with IP reputation data from AbuseIPDB and VirusTotal

**Frontend:** Real-time threat scores, abuse confidence, malicious detections  
**Location:** http://localhost:3000/advanced

**Setup:**
```yaml
# Edit configs/config.yaml
threat_intel:
  enabled: true
  abuseipdb:
    enabled: true
    api_key: "your-key-here"
  virustotal:
    enabled: true
    api_key: "your-key-here"
```

**Get API Keys:**
- AbuseIPDB: https://www.abuseipdb.com/account/api (1000 checks/day free)
- VirusTotal: https://www.virustotal.com/gui/my-apikey (500 checks/day free)

---

### 2. 📊 Report Export (PDF/CSV)
**What it does:** Generate professional reports with statistics and visualizations

**Frontend:** Interactive report generator with date filtering  
**Location:** http://localhost:3000/advanced

**Usage:**
1. Click Report Exporter card
2. Choose PDF or CSV
3. Select date range (optional)
4. Click "Generate Report"
5. Report downloads automatically

**API:**
```bash
curl "http://localhost:5000/api/reports/generate?format=pdf" -o report.pdf
curl "http://localhost:5000/api/reports/generate?format=csv" -o report.csv
```

---

### 3. 🔍 Packet Filtering
**What it does:** Focus detection on specific traffic using BPF-style filters

**Frontend:** Filter builder with presets and custom syntax  
**Location:** http://localhost:3000/advanced

**CLI Usage:**
```bash
# Web traffic only
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --packet-filter "tcp and (port 80 or port 443)"

# SSH connections
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --packet-filter "tcp port 22"

# Specific host
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --packet-filter "host 192.168.1.100"
```

**Filter Presets:**
- Web Traffic: `tcp and (port 80 or port 443)`
- DNS: `udp and port 53`
- SSH: `tcp and port 22`
- Database: `tcp and (port 3306 or port 5432)`
- Large Packets: `length > 1000`
- Local Network: `net 192.168.0.0/16`

---

### 4. 🔀 Multi-Interface Monitoring
**What it does:** Monitor multiple network interfaces simultaneously

**Frontend:** Per-interface statistics and status  
**Location:** http://localhost:3000/advanced

**CLI Usage:**
```bash
# Monitor WiFi and Ethernet
python anomaly_detection/main.py --mode detect \
  --interfaces "wlo1,enp0s25" \
  --backend pyshark \
  --inject-rate 0

# Monitor all interfaces
python anomaly_detection/main.py --mode detect \
  --interfaces "wlo1,enp0s25,lo" \
  --duration 300
```

---

### 5. 📁 PCAP File Analysis
**What it does:** Analyze previously captured network traffic offline

**CLI Usage:**
```bash
# Basic analysis
python anomaly_detection/main.py --mode pcap \
  --pcap-file capture.pcap \
  --model random_forest

# With packet filter
python anomaly_detection/main.py --mode pcap \
  --pcap-file capture.pcap \
  --packet-filter "tcp port 80" \
  --model random_forest

# Capture traffic for later analysis
sudo tcpdump -i wlo1 -w capture.pcap -c 1000
```

---

### 6. 📧 Email Alerts
**What it does:** Send email notifications for high-severity anomalies

**Setup:**
```yaml
# Edit configs/config.yaml
alerts:
  notification_methods:
    - email
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your-email@gmail.com"
    sender_password: "your-app-password"
    recipients:
      - "security-team@example.com"
```

**Gmail Setup:**
1. Enable 2FA on Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use app password in config

---

### 7. 🔗 Webhook Alerts
**What it does:** Send HTTP POST notifications to webhooks (Slack, Discord, etc.)

**Setup:**
```yaml
# Edit configs/config.yaml
alerts:
  notification_methods:
    - webhook
  webhook:
    enabled: true
    url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    headers:
      Content-Type: "application/json"
```

**Slack Webhook:**
1. Create webhook: https://api.slack.com/messaging/webhooks
2. Copy webhook URL to config

---

## 🏃 Quick Start Examples

### Real-Time Detection with All Features
```bash
# 1. Configure threat intelligence (edit configs/config.yaml)
# 2. Configure email/webhook alerts (edit configs/config.yaml)

# 3. Start detection
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --backend pyshark \
  --inject-rate 0 \
  --packet-filter "tcp" \
  --duration 999999
```

### Multi-Interface with Filtering
```bash
python anomaly_detection/main.py --mode detect \
  --interfaces "wlo1,enp0s25" \
  --backend pyshark \
  --packet-filter "tcp and not port 22" \
  --duration 3600
```

### PCAP Analysis with Reports
```bash
# 1. Analyze PCAP
python anomaly_detection/main.py --mode pcap \
  --pcap-file capture.pcap \
  --packet-filter "tcp port 80"

# 2. Generate report
curl "http://localhost:5000/api/reports/generate?format=pdf" -o analysis_report.pdf
```

---

## 🖥️ Frontend Features

### Advanced Features Page (`/advanced`)

**Threat Intelligence Card:**
- Real-time threat scores (0-100)
- AbuseIPDB: abuse confidence, country, reports
- VirusTotal: malicious detections, reputation
- Color-coded severity levels

**Report Exporter Card:**
- PDF with charts and statistics
- CSV with raw detection data
- Date range filtering
- One-click download

**Packet Filter Builder:**
- Quick filter presets
- Custom BPF syntax
- Live filter display
- Syntax examples

**Multi-Interface Monitor:**
- Per-interface packet counts
- Anomaly rates by interface
- Interface status indicators
- Traffic distribution bars

---

## 📦 Installation

### Backend Dependencies
```bash
pip install reportlab requests
# Or update all
pip install -r requirements.txt
```

### Frontend (Already Installed)
```bash
cd frontend
npm install
```

---

## 🧪 Testing Features

### Test Threat Intelligence
```bash
# 1. Add API keys to config.yaml
# 2. Enable threat_intel
# 3. Run detection
# 4. Check frontend at /advanced
```

### Test Report Generation
```bash
# Start API server
python api_server.py

# Generate PDF
curl "http://localhost:5000/api/reports/generate?format=pdf&start_date=2024-01-01" -o test.pdf

# Generate CSV
curl "http://localhost:5000/api/reports/generate?format=csv" -o test.csv
```

### Test Packet Filters
```bash
# Test web traffic filter
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --packet-filter "tcp port 80" \
  --duration 30
```

### Test Multi-Interface
```bash
# Monitor 2 interfaces for 1 minute
python anomaly_detection/main.py --mode detect \
  --interfaces "wlo1,lo" \
  --backend pyshark \
  --duration 60
```

---

## 📖 Documentation

- **ADVANCED_FEATURES.md** - Comprehensive feature documentation
- **FRONTEND_INTEGRATION.md** - Frontend component details
- **FEATURE_IMPLEMENTATION_SUMMARY.md** - Implementation overview

---

## 🎨 Frontend Screenshots

### Main Dashboard
- Stats cards with real-time metrics
- Attack type classification grid
- Detection timeline chart
- Recent detections table
- Link to Advanced Features

### Advanced Features Page
- Threat Intelligence panel (top-left)
- Report Exporter (top-right)
- Packet Filter Builder (bottom-left)
- Multi-Interface Monitor (bottom-right)

---

## ⚡ Performance Tips

1. **Threat Intelligence:** Increase `cache_ttl` to reduce API calls
2. **Multi-Interface:** Monitor only necessary interfaces
3. **Packet Filters:** Use filters to reduce processing load
4. **Reports:** Generate during off-peak hours for large datasets
5. **Alerts:** Set `alert_cooldown` to prevent notification spam

---

## 🐛 Troubleshooting

### Threat Intel Not Showing
- Check API keys in config.yaml
- Verify `threat_intel.enabled: true`
- Check API rate limits (1000/day AbuseIPDB, 500/day VirusTotal)
- Look for errors in logs/

### Report Generation Fails
- Install reportlab: `pip install reportlab`
- Check database has detections
- Verify date range contains data

### Frontend Not Updating
- Check API server is running: `curl http://localhost:5000/api/detections/stats`
- Check browser console for errors
- Clear browser cache and reload

### Multi-Interface Permission Errors
```bash
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
```

---

## 🎉 All Features Complete!

✅ Threat Intelligence (AbuseIPDB + VirusTotal)  
✅ Report Export (PDF + CSV)  
✅ Packet Filtering (BPF-style)  
✅ Multi-Interface Monitoring  
✅ PCAP Analysis  
✅ Email Alerts (SMTP)  
✅ Webhook Alerts (HTTP POST)  

**Frontend:** http://localhost:3000/advanced  
**API:** http://localhost:5000  

Enjoy your advanced network anomaly detection system! 🚀🛡️
