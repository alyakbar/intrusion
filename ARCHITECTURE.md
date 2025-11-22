# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                                     │
│                     http://localhost:3000                               │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP Requests
                                 │ (Auto-refresh every 5s)
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   NEXT.JS FRONTEND (Port 3000)                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  React Components:                                               │  │
│  │  • AttackTypeGrid    → Shows 8 attack types with counts         │  │
│  │  • StatsCards        → Total packets, anomalies, detection rate │  │
│  │  • TimelineChart     → Hourly activity graph (Recharts)         │  │
│  │  • TopSources        → Top threat IP addresses                  │  │
│  │  • RecentDetections  → Real-time detection table               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ REST API Calls
                                 │ GET /api/detections/*
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   FLASK API SERVER (Port 5000)                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Endpoints:                                                      │  │
│  │  • /api/detections/stats        → Overall statistics            │  │
│  │  • /api/detections/by-type      → Attack classification         │  │
│  │  • /api/detections/timeline     → Hourly aggregated data        │  │
│  │  • /api/detections/recent       → Latest 50 detections          │  │
│  │  • /api/detections/top-sources  → Top 10 threat IPs             │  │
│  │  • /health                      → Health check                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Classification Logic:                                           │  │
│  │  classify_attack_type(packet_data, protocol, score)             │  │
│  │    → Analyzes patterns to determine attack type                 │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ SQL Queries
                                 │ SELECT * FROM detections
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  SQLite DATABASE (data/detections.db)                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Table: detections                                               │  │
│  │  ├─ id (PRIMARY KEY)                                             │  │
│  │  ├─ timestamp                                                    │  │
│  │  ├─ source_ip                                                    │  │
│  │  ├─ dest_ip                                                      │  │
│  │  ├─ protocol                                                     │  │
│  │  ├─ anomaly_score (REAL)                                         │  │
│  │  ├─ is_anomaly (BOOLEAN)                                         │  │
│  │  ├─ severity (TEXT: high/medium/low)                            │  │
│  │  └─ raw_packet (TEXT)                                            │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────▲────────────────────────────────────────┘
                                 │
                                 │ INSERT INTO detections
                                 │ (writes via DatabaseManager)
                                 │
┌─────────────────────────────────────────────────────────────────────────┐
│              DETECTION SYSTEM (anomaly_detection/main.py)               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  RealtimeDetector                                                │  │
│  │  ├─ start_packet_capture()                                       │  │
│  │  │  ├─ Backend: Scapy or PyShark                                 │  │
│  │  │  ├─ Interface: eth0, lo, wlan0                                │  │
│  │  │  └─ Fallback: Synthetic packet generation                     │  │
│  │  │                                                               │  │
│  │  ├─ process_packet(packet_data)                                  │  │
│  │  │  ├─ Extract features (IP, protocol, length, etc.)            │  │
│  │  │  ├─ Preprocessor.transform(features)                          │  │
│  │  │  └─ Model.predict_proba(features) → anomaly_score            │  │
│  │  │                                                               │  │
│  │  └─ _log_detection(result)                                       │  │
│  │     └─ DatabaseManager.log_detection() → SQLite                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Trained Model: random_forest.joblib                            │  │
│  │  • Accuracy: 99.95%                                              │  │
│  │  • Features: 42 (NSL-KDD processed)                              │  │
│  │  • Threshold: 0.85 (anomaly if score > 0.85)                    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ Captures from
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          NETWORK TRAFFIC                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Real Packets (requires sudo):                                   │  │
│  │  • Ethernet frames from eth0/wlan0                               │  │
│  │  • Parsed by Scapy/PyShark                                       │  │
│  │                                                                  │  │
│  │  Synthetic Packets (fallback):                                   │  │
│  │  • Random IPs: 192.168.0.x → 192.168.1.x                        │  │
│  │  • Protocols: TCP, UDP, ICMP                                     │  │
│  │  • Anomaly Injection: --inject-rate 0.2 (20% anomalies)         │  │
│  │  • Throttling: --synthetic-delay 0.1 (100ms between packets)    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW SUMMARY                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  1. Network Traffic → Detection System                                 │
│     • Packet capture (Scapy/PyShark or synthetic)                      │
│     • Feature extraction                                               │
│                                                                         │
│  2. Detection System → ML Model                                        │
│     • Preprocessing (scaling, encoding)                                │
│     • Random Forest prediction                                         │
│     • Anomaly score calculation                                        │
│                                                                         │
│  3. Detection System → Database                                        │
│     • Log all detections (normal + anomaly)                            │
│     • Store: timestamp, IPs, protocol, score, severity                 │
│                                                                         │
│  4. Database → API Server                                              │
│     • SQL queries for stats, timeline, recent, top sources             │
│     • Attack type classification                                       │
│                                                                         │
│  5. API Server → Frontend                                              │
│     • JSON responses via REST endpoints                                │
│     • Auto-refresh every 5-10 seconds                                  │
│                                                                         │
│  6. Frontend → User Browser                                            │
│     • React components render data                                     │
│     • Charts, tables, cards update in real-time                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    ATTACK TYPE CLASSIFICATION                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Pattern Matching in api_server.py:                                    │
│                                                                         │
│  if 'syn' in packet or 'flood' in packet:                              │
│      → DoS/DDoS Attack                                                 │
│                                                                         │
│  if 'scan' in packet or protocol == 'ICMP':                            │
│      → Port Scanning                                                   │
│                                                                         │
│  if 'auth' in packet or 'login' in packet:                             │
│      → Brute Force                                                     │
│                                                                         │
│  if 'sql' in packet or 'select' in packet:                             │
│      → SQL Injection & XSS                                             │
│                                                                         │
│  if 'cmd' in packet or 'exec' in packet:                               │
│      → Backdoor & Botnet                                               │
│                                                                         │
│  if anomaly_score > 0.95:                                              │
│      → Data Exfiltration                                               │
│                                                                         │
│  if 'arp' in packet or 'dns' in packet:                                │
│      → Man-in-the-Middle                                               │
│                                                                         │
│  if anomaly_score > 0.9 and no_pattern_match:                          │
│      → Zero-Day Attack                                                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                    SEVERITY CLASSIFICATION                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Based on anomaly_score:                                               │
│                                                                         │
│  • HIGH:   score >= 0.9   → Red badge, immediate alert                 │
│  • MEDIUM: score >= 0.7   → Yellow badge, monitor closely              │
│  • LOW:    score < 0.7    → Blue badge, log for review                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```
