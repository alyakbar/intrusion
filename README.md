# Network Anomaly Detection System

A comprehensive **Machine Learning-based Network Intrusion Detection System (NIDS)** with real-time monitoring, active port scanning, and an interactive Next.js dashboard for visualizing network threats.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0-black.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Features

### Core Detection Capabilities
- **Real-time Network Traffic Analysis** - Monitor live network packets using Scapy/PyShark
- **ML-Powered Anomaly Detection** - Random Forest classifier with 99.95% accuracy
- **8 Attack Type Classifications**:
  - DoS/DDoS Attacks
  - Port Scanning
  - Brute Force Attacks
  - SQL Injection & XSS
  - Backdoor/Botnet Activity
  - Data Exfiltration
  - Man-in-the-Middle (MITM)
  - Zero-Day Exploits

### Port Scanning & Analysis
- **Active Port Scanner** - Discover open ports on hosts/networks
- **Port Traffic Analysis** - Identify targeted ports and scanning activity
- **Service Detection** - Automatic service identification for common ports
- **Threat Level Assessment** - Risk scoring for port-based attacks

### Modern Web Dashboard
- **Next.js Frontend** - Real-time visualization with auto-refresh
- **Interactive Charts** - Timeline graphs, attack type grids, threat sources
- **Port Monitor Page** - Dedicated `/ports` route (removed from main dashboard for clarity)
- **Responsive Design** - Dark theme optimized for security operations

### Additional Features
- SQLite persistence for detection history
- REST API for data access
- Synthetic anomaly injection for testing
- Multiple ML models (Random Forest, SVM, Isolation Forest, Autoencoder)
- Configurable detection thresholds
- Background monitoring mode

---

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
  - [Network Detection](#1-network-detection)
  - [Port Scanning](#2-port-scanning)
  - [Dashboard](#3-dashboard)
- [Architecture](#-architecture)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)
- [Performance](#-performance)

---

## 🛠 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+ and npm
- Linux/macOS (Windows with WSL2)
- Root/sudo access for packet capture

### 1. Clone Repository
```bash
git clone <repository-url>
cd network-anomaly-project
```

### 2. Python Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python verify_installation.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cd ..
```

### 4. Dataset Download (Optional)
The system includes pre-trained models. To retrain:
```bash
# Download NSL-KDD dataset
mkdir -p data/raw/nsl-kdd
cd data/raw/nsl-kdd
wget https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt
wget https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt
cd ../../..
```

---

## ⚡ Quick Start

### Option 1: Launch All Components (Recommended)
```bash
chmod +x start_all.sh
./start_all.sh
```

This starts:
1. Flask API server (port 5000)
2. Real-time detection with synthetic anomalies
3. Next.js dashboard (port 3000)

### Option 2: Manual Launch

**Terminal 1 - API Server:**
```bash
source venv/bin/activate
python api_server.py
```

**Terminal 2 - Detection System:**
```bash
source venv/bin/activate
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --inject-rate 0.2 --synthetic-delay 0.05
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access Dashboard:** http://localhost:3000

---

## 📖 Usage Guide

### 1. Network Detection

#### Basic Detection
```bash
# Monitor loopback interface for 60 seconds
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --duration 60
```

#### With Synthetic Anomalies (for testing)
```bash
# Inject 30% anomalies with 50ms delay between packets
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --inject-rate 0.3 --synthetic-delay 0.05
```

#### Capture Specific Packet Count
```bash
# Capture exactly 500 packets
python anomaly_detection/main.py --mode detect --model random_forest \
  --interface lo --packet-count 500
```

#### Available CLI Options
```
--mode detect          # Real-time detection mode
--model MODEL          # ML model: random_forest, svm, isolation_forest, autoencoder
--interface IFACE      # Network interface (eth0, wlan0, lo)
--duration SECONDS     # Capture duration
--packet-count N       # Number of packets to capture
--inject-rate 0.0-1.0  # Synthetic anomaly injection rate
--synthetic-delay SEC  # Delay between synthetic packets
--backend scapy|pyshark # Packet capture backend
```

### 2. Port Scanning

#### Quick Scan (Common Ports)
```bash
python scan_ports.py --host 192.168.1.1 --quick
```

#### Scan Specific Ports
```bash
python scan_ports.py --host example.com --ports 80,443,8080,3000
```

#### Scan Port Range
```bash
python scan_ports.py --host 192.168.1.1 --range 1-1000
```

#### Network Range Scan
```bash
python scan_ports.py --network 192.168.1.0/24 --quick
```

#### Full Port Scan (Slow!)
```bash
python scan_ports.py --host 192.168.1.1 --full
```

#### Advanced Options
```bash
python scan_ports.py --host 192.168.1.1 --ports 1-65535 \
  --timeout 0.5 --workers 200 --json > results.json
```

### 3. Dashboard

#### Overview Tab
- **Stats Cards**: Total packets, anomalies, detection rate, recent activity
- **Attack Type Grid**: 8 attack categories with live counts
- **Timeline Chart**: 24-hour activity graph
- **Top Threat Sources**: IPs generating most anomalies
- **Recent Detections**: Real-time detection feed

#### Port Activity Tab
- **Targeted Ports**: Most attacked ports with threat levels
- **Port Scanners**: Suspected scanning activity
- **Open Ports**: Likely open ports based on traffic
- **Service Distribution**: Traffic breakdown by service type

##### Port & Protocol Display Clarification
The detection feed now labels ports explicitly:

```
SRC 54434 → DST 110
POP3
```

Explanation:
- **SRC <ephemeral>**: High-number client port chosen by OS (commonly 32768–60999 or 49152–65535 depending on system).
- **DST <service>**: Well-known / registered service port (22 SSH, 443 HTTPS, 3306 MySQL, etc.).
- **Service Name Line**: Added for quick recognition of the destination service.
- **ICMP Packets**: Show `N/A (ICMP)` because ICMP (Layer 3) does not use ports.
- **Protocol Badges**: Blue themed for consistency across TCP/UDP/ICMP.
- **Filtering**: ICMP excluded from targeted/open/scanner port statistics; ICMP anomalies mapped to DoS/DDoS category.

> Why you sometimes see numbers like 54434: that's an ephemeral source port, not a service; only the destination port identifies the application service.

---

## 🏗 Architecture

```
┌─────────────────┐
│  Next.js        │  Port 3000
│  Frontend       │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask API      │  Port 5000
│  Server         │
└────────┬────────┘
         │ SQL
         ▼
┌─────────────────┐
│  SQLite         │
│  Database       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐       ┌──────────────┐
│  ML Detection   │◄──────│ Port Scanner │
│  Engine         │       └──────────────┘
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Network        │
│  Traffic        │
└─────────────────┘
```

### Components

**Backend (Python):**
- `anomaly_detection/` - Core detection engine
- `anomaly_detection/scanning/` - Port scanner module
- `anomaly_detection/analysis/` - Traffic analysis
- `api_server.py` - REST API
- `scan_ports.py` - CLI port scanner

**Frontend (Next.js/TypeScript):**
- `frontend/app/` - Main pages
- `frontend/components/` - React components
- Auto-refresh every 5-10 seconds

**Database:**
- SQLite with detection history
- Schema: `id`, `timestamp`, `source_ip`, `dest_ip`, `dest_port`, `protocol`, `anomaly_score`, `is_anomaly`, `severity`

---

## 🔌 API Reference

### Base URL
`http://localhost:5000`

### Detection Endpoints

#### GET `/api/detections/stats`
Overall detection statistics
```json
{
  "total_packets": 279,
  "total_anomalies": 13,
  "anomaly_rate": 4.66,
  "severity_counts": {
    "high": 13,
    "medium": 0,
    "low": 0
  },
  "recent_activity": 279
}
```

#### GET `/api/detections/by-type`
Anomalies by attack type
```json
{
  "counts": {
    "dos_ddos": 0,
    "port_scan": 3,
    "brute_force": 0,
    "sql_xss": 0,
    "backdoor_botnet": 0,
    "data_exfiltration": 3,
    "mitm": 0,
    "zero_day": 6,
    "unknown": 1
  },
  "detections": { ... }
}
```

#### GET `/api/detections/timeline?hours=24`
24-hour activity timeline

#### GET `/api/detections/recent?limit=20`
Recent detections
Includes `source_port`, `dest_port`. ICMP packets have 0 values internally but are rendered as `N/A (ICMP)`.

#### GET `/api/detections/top-sources?limit=10`
Top threat sources

### Port Scanning Endpoints

#### GET `/api/ports/targeted?limit=50`
Most targeted ports
```json
[
  {
    "port": 443,
    "protocol": "TCP",
    "total_hits": 150,
    "anomaly_hits": 12,
    "avg_anomaly_score": 0.85,
    "threat_level": "high"
  }
]
```

#### GET `/api/ports/scanners`
Suspected port scanners
Excludes ICMP and ports <= 0; counts distinct TCP/UDP destination ports.

#### GET `/api/ports/open`
Likely open ports from traffic
Excludes ICMP and ports <= 0.

#### GET `/api/ports/distribution`
Service category distribution

---

## ⚙️ Configuration

### `configs/config.yaml`
```yaml
data:
  raw_dir: data/raw/nsl-kdd
  processed_dir: data/processed

models:
  save_dir: saved_models
  random_forest:
    n_estimators: 100
    max_depth: 20

detection:
  threshold: 0.85
  batch_size: 100

capture:
  interface: lo
  timeout: 60
```

### Environment Variables
Create `frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:5000
```

---

## 🐛 Troubleshooting

### Permission Denied (Packet Capture)
```bash
sudo python anomaly_detection/main.py --mode detect --model random_forest --interface eth0
```

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### No Data in Dashboard
1. Check API server: `curl http://localhost:5000/api/detections/stats`
2. Generate test data: `python anomaly_detection/main.py --mode detect --model random_forest --interface lo --inject-rate 0.3 --packet-count 100`
3. Restart frontend: `cd frontend && npm run dev`

### Database Locked
```bash
# Stop all Python processes
pkill -f python

# Restart API server
python api_server.py
```

---

## 📊 Performance

### Detection Accuracy
- **Random Forest**: 99.95% accuracy on NSL-KDD test set
- **SVM**: 98.2% accuracy
- **Isolation Forest**: 95.1% (unsupervised)
- **Autoencoder**: 96.8% (deep learning)

### Throughput
- Real-time detection: ~1000 packets/second
- Port scanner: 100-1000 ports/second (concurrent)
- Database writes: ~500 insertions/second

### Resource Usage
- CPU: 15-25% (detection)
- Memory: ~200MB (Python backend)
- Memory: ~150MB (Next.js frontend)

---

## 🤝 Contributing

## 🚀 Publishing to GitHub

Follow these steps to push this project publicly.

### 1. Initialize (if not already)
```bash
git init
git add .
git commit -m "Initial commit: Network Anomaly Detection System"
```

### 2. Add Remote & Push
```bash
git remote add origin https://github.com/<your-username>/network-anomaly-project.git
git branch -M main
git push -u origin main
```

### 3. Optional: Tag Release
```bash
git tag -a v0.1.0 -m "First public release"
git push origin v0.1.0
```

### 4. Pre-Publish Checklist
- No secrets / tokens in repo
- `.env` files ignored (confirmed in .gitignore)
- Large raw dataset excluded (`data/raw/*`)
- Decide whether to keep `saved_models/` (currently ignored except .gitkeep)
- README updated with port/protocol clarifications

### 5. Open Issues (Recommended)
Create GitHub issues for Roadmap items to invite collaboration.


1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🔗 Resources

- [NSL-KDD Dataset](https://www.unb.ca/cic/datasets/nsl.html)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

## 👨‍💻 Author

Built with ❤️ by the Network Security Team

For questions or issues, please open a GitHub issue.

---

## 🎯 Roadmap

- [ ] Add support for PCAP file analysis
- [ ] Implement packet filtering rules
- [ ] Add email/webhook alerting
- [ ] Support for multiple network interfaces
- [ ] Export detection reports (PDF/CSV)
- [ ] Integration with threat intelligence feeds
- [ ] Kubernetes deployment configuration
- [ ] Advanced visualization (3D network graphs)

---

**⚠️ Disclaimer**: This tool is for educational and authorized security testing only. Unauthorized network scanning or monitoring may be illegal. Always obtain proper authorization before using on networks you don't own.
