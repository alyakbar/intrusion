# Advanced Features Guide

This guide covers the advanced features added to the Network Anomaly Detection System.

## Table of Contents

1. [PCAP File Analysis](#pcap-file-analysis)
2. [Packet Filtering](#packet-filtering)
3. [Email & Webhook Alerting](#email--webhook-alerting)
4. [Multi-Interface Monitoring](#multi-interface-monitoring)
5. [Report Export (PDF/CSV)](#report-export-pdfcsv)
6. [Threat Intelligence Integration](#threat-intelligence-integration)

---

## PCAP File Analysis

Analyze previously captured network traffic from PCAP files for offline anomaly detection.

### Usage

```bash
python anomaly_detection/main.py \
  --mode pcap \
  --pcap-file /path/to/capture.pcap \
  --model random_forest \
  --packet-filter "tcp port 80"
```

### Parameters

- `--pcap-file`: Path to PCAP file
- `--packet-filter`: Optional BPF-style filter (see below)
- `--backend`: Choose 'scapy' or 'pyshark' (default: scapy)

### Features

- Batch processing of captured packets
- Same anomaly detection as live capture
- Supports both Scapy and PyShark backends
- Progress tracking for large files
- Database persistence of findings
- Alert generation for detected anomalies

### Example

```bash
# Analyze SSH traffic in a capture file
python anomaly_detection/main.py \
  --mode pcap \
  --pcap-file ~/captures/network_traffic.pcap \
  --packet-filter "tcp port 22" \
  --model random_forest
```

---

## Packet Filtering

Apply BPF-style filters to focus detection on specific traffic patterns.

### Supported Filters

#### Protocol Filters
```
tcp           # TCP packets only
udp           # UDP packets only
icmp          # ICMP packets only
```

#### Port Filters
```
port 80       # Traffic on port 80
port 443      # HTTPS traffic
port 22       # SSH traffic
```

#### Host Filters
```
host 192.168.1.1        # Specific host
src host 10.0.0.5       # Source host
dst host 8.8.8.8        # Destination host
```

#### Network Filters
```
net 192.168.0.0/24      # Entire subnet
```

#### Length Filters
```
length > 1000           # Packets larger than 1000 bytes
length < 100            # Small packets
```

#### Compound Filters
```
tcp and port 80         # TCP on port 80
tcp and port 443        # HTTPS
host 192.168.1.1 or host 10.0.0.1    # Multiple hosts
tcp and not port 22     # TCP except SSH
```

### Filter Presets

Use built-in presets for common scenarios:

```python
from anomaly_detection.analysis.packet_filter import FilterPreset

# Web traffic (HTTP/HTTPS)
filter = FilterPreset.web_traffic()

# DNS queries
filter = FilterPreset.dns_traffic()

# SSH connections
filter = FilterPreset.ssh_traffic()

# Database traffic
filter = FilterPreset.database_traffic()

# Port scan detection
filter = FilterPreset.scan_detection()
```

### CLI Usage

```bash
# Filter web traffic
python anomaly_detection/main.py --mode detect \
  --interface wlo1 \
  --packet-filter "tcp and (port 80 or port 443)"

# Filter specific subnet
python anomaly_detection/main.py --mode pcap \
  --pcap-file capture.pcap \
  --packet-filter "net 192.168.1.0/24"
```

---

## Email & Webhook Alerting

Send alerts via email (SMTP) or webhooks (HTTP POST) when anomalies are detected.

### Email Configuration

Edit `configs/config.yaml`:

```yaml
alerts:
  notification_methods:
    - email  # Add email to notification methods
  
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender_email: "your-email@gmail.com"
    sender_password: "your-app-password"
    recipients:
      - "security-team@example.com"
      - "admin@example.com"
```

#### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password in the config (not your regular password)

### Webhook Configuration

```yaml
alerts:
  notification_methods:
    - webhook  # Add webhook to notification methods
  
  webhook:
    enabled: true
    url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    headers:
      Content-Type: "application/json"
    timeout: 10
```

### Webhook Payload Format

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "severity": "high",
  "anomaly_score": 0.95,
  "threat_score": 87.5,
  "description": "Anomaly detected with score 0.9500, threat score 87.5",
  "packet_data": {
    "src_ip": "192.168.1.100",
    "dst_ip": "203.0.113.42",
    "protocol": "TCP"
  }
}
```

### Integrations

#### Slack

Use a Slack Incoming Webhook:
1. Create webhook: https://api.slack.com/messaging/webhooks
2. Set webhook URL in config

#### Discord

Use a Discord Webhook:
1. Create webhook in channel settings
2. Set webhook URL in config

#### Microsoft Teams

1. Add Incoming Webhook connector to channel
2. Set webhook URL in config

---

## Multi-Interface Monitoring

Monitor multiple network interfaces simultaneously.

### Usage

```bash
python anomaly_detection/main.py \
  --mode detect \
  --interfaces "wlo1,enp0s25,eth0" \
  --backend pyshark \
  --inject-rate 0
```

### Parameters

- `--interfaces`: Comma-separated list of interfaces
- All other parameters apply to all interfaces

### Features

- Parallel capture across multiple interfaces
- Per-interface statistics tracking
- Aggregated anomaly detection metrics
- Interface labels on all detections
- Unified alerting across interfaces

### Example Output

```
Multi-Interface Monitoring Statistics
======================================
Total Packets Processed: 15423
Total Anomalies Detected: 87
Total Alerts Generated: 87
Overall Anomaly Rate: 0.56%
Runtime: 0:05:23

--------------------------------------
Per-Interface Statistics:
--------------------------------------

  Interface: wlo1
    Status: completed
    Packets: 12890
    Anomalies: 73
    Anomaly Rate: 0.57%

  Interface: enp0s25
    Status: completed
    Packets: 2533
    Anomalies: 14
    Anomaly Rate: 0.55%
```

---

## Report Export (PDF/CSV)

Generate detection reports for analysis and compliance.

### API Endpoint

```
GET /api/reports/generate?format=pdf&start_date=2024-01-01&end_date=2024-01-31
```

### Parameters

- `format`: 'pdf' or 'csv'
- `start_date`: ISO format (YYYY-MM-DD)
- `end_date`: ISO format (YYYY-MM-DD)
- `include_charts`: 'true' or 'false' (PDF only)

### PDF Report Contents

1. **Report Metadata**
   - Generation timestamp
   - Date range
   - Total detections
   - Unique source IPs
   - Overall anomaly rate

2. **Summary Statistics**
   - Detections by severity (high/medium/low)
   - Top attack types
   - Top source IPs
   - Protocol distribution

3. **Visualizations** (optional)
   - Timeline chart
   - Attack type distribution
   - Geographic distribution (if available)

4. **Detection Details**
   - Recent 50 detections
   - Timestamp, source, destination, protocol, severity

### CSV Report Format

```csv
id,timestamp,source_ip,dest_ip,source_port,dest_port,protocol,anomaly_score,severity,threat_score
1,2024-01-15 10:30:45,192.168.1.100,203.0.113.42,54321,80,TCP,0.95,high,87.5
```

### Programmatic Usage

```python
from anomaly_detection.reporting.report_generator import ReportGenerator
from anomaly_detection.utils.config import load_config
from datetime import datetime, timedelta

config = load_config('configs/config.yaml')
generator = ReportGenerator(config)

# Generate PDF report
result = generator.generate_report(
    output_path='detection_report.pdf',
    format='pdf',
    start_date=datetime.now() - timedelta(days=7),
    end_date=datetime.now(),
    include_charts=True
)

# Generate CSV report
result = generator.generate_report(
    output_path='detection_report.csv',
    format='csv',
    start_date=datetime.now() - timedelta(days=30)
)
```

### Installation

Install reportlab for PDF generation:

```bash
pip install reportlab
```

---

## Threat Intelligence Integration

Enrich detections with threat reputation data from external sources.

### Supported Providers

1. **AbuseIPDB** - IP reputation and abuse reports
2. **VirusTotal** - Malware and malicious activity detection

### Configuration

Edit `configs/config.yaml`:

```yaml
threat_intel:
  enabled: true
  
  abuseipdb:
    enabled: true
    api_key: "your-abuseipdb-api-key"
    max_age_days: 90
    timeout: 10
    cache_ttl: 3600
  
  virustotal:
    enabled: true
    api_key: "your-virustotal-api-key"
    timeout: 10
    cache_ttl: 3600
```

### Getting API Keys

#### AbuseIPDB

1. Register: https://www.abuseipdb.com/register
2. Get API key: https://www.abuseipdb.com/account/api
3. Free tier: 1,000 checks/day

#### VirusTotal

1. Register: https://www.virustotal.com/gui/join-us
2. Get API key: https://www.virustotal.com/gui/my-apikey
3. Free tier: 500 requests/day

### Enriched Detection Data

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "src_ip": "203.0.113.42",
  "anomaly_score": 0.95,
  "threat_score": 87.5,
  "threat_intel": {
    "src_threat_intel": {
      "abuseipdb": {
        "abuse_confidence_score": 85,
        "country_code": "CN",
        "usage_type": "Data Center/Web Hosting/Transit",
        "total_reports": 147,
        "is_whitelisted": false
      },
      "virustotal": {
        "malicious": 8,
        "suspicious": 2,
        "harmless": 45,
        "reputation": -67,
        "country": "CN",
        "asn": "AS4134"
      }
    }
  }
}
```

### Threat Score Calculation

The system calculates a combined threat score (0-100):

- **AbuseIPDB**: Uses abuse confidence score directly
- **VirusTotal**: Malicious detections × 10 + Suspicious × 5
- **Combined**: (Anomaly Score × 0.6) + (Threat Score/100 × 0.4)

### Severity Adjustment

Severity levels are automatically adjusted based on threat intelligence:

- **High**: Combined score ≥ 0.9 OR threat score ≥ 75
- **Medium**: Combined score ≥ 0.7 OR threat score ≥ 50
- **Low**: Below medium thresholds

### Caching

Results are cached for 1 hour (configurable) to avoid rate limits and improve performance.

### Usage Example

Threat intel enrichment happens automatically when enabled. No code changes needed:

```bash
# Just run detection normally
python anomaly_detection/main.py \
  --mode detect \
  --interface wlo1 \
  --backend pyshark \
  --inject-rate 0
```

Alerts will automatically include threat intelligence data.

---

## Installation

Install all dependencies for advanced features:

```bash
# Update packages
pip install -r requirements.txt

# For PDF reports
pip install reportlab

# For threat intelligence
pip install requests

# Already included: matplotlib (for charts)
```

## Testing Features

### Test PCAP Analysis

```bash
# Create test capture
sudo tcpdump -i wlo1 -c 100 -w test_capture.pcap

# Analyze it
python anomaly_detection/main.py \
  --mode pcap \
  --pcap-file test_capture.pcap \
  --model random_forest
```

### Test Multi-Interface

```bash
# List available interfaces
ip link show

# Monitor multiple
python anomaly_detection/main.py \
  --mode detect \
  --interfaces "wlo1,lo" \
  --backend pyshark \
  --duration 30
```

### Test Report Generation

```bash
curl "http://localhost:5000/api/reports/generate?format=pdf" -o report.pdf
curl "http://localhost:5000/api/reports/generate?format=csv" -o report.csv
```

### Test Threat Intelligence

Enable in config and run detection - threat data will appear in logs and alerts.

---

## Troubleshooting

### PCAP Analysis Fails

- Check PCAP file path is correct
- Verify read permissions
- Try alternate backend (--backend pyshark)

### Email Not Sending

- Verify SMTP credentials
- Check firewall allows port 587
- For Gmail, use app-specific password
- Check recipients list format

### Webhook Fails

- Verify URL is correct and accessible
- Check webhook endpoint logs
- Verify headers (especially Content-Type)
- Test with curl first

### Multi-Interface Permissions

```bash
# Grant capture permissions
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
```

### Report Generation Errors

- Install reportlab: `pip install reportlab`
- Check database has detections
- Verify date range contains data

### Threat Intel Quota Exceeded

- Check API key is valid
- Monitor free tier limits (1000/day for AbuseIPDB)
- Increase cache_ttl to reduce requests
- Consider upgrading API plan

---

## Performance Tips

1. **PCAP Analysis**: Use packet filters to process only relevant traffic
2. **Multi-Interface**: Monitor only necessary interfaces to reduce load
3. **Threat Intel**: Increase cache_ttl to minimize API calls
4. **Reports**: Generate during off-peak hours for large datasets
5. **Alerts**: Use alert_cooldown to prevent notification spam

---

## Next Steps

- Configure alerting channels (email/webhook)
- Set up threat intelligence API keys
- Create custom packet filters for your environment
- Schedule automated report generation
- Monitor threat scores to identify targeted attacks
