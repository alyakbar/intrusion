# Port and Protocol Display Documentation

## Overview
This document details how ports and protocols are displayed throughout the Network Anomaly Detection system, showing accurate real-time data from the database.

## Database Schema
The `detections` table stores complete port and protocol information:
```sql
- source_port: INTEGER (ephemeral port from source)
- dest_port: INTEGER (target service port)
- protocol: TEXT (TCP, UDP, ICMP)
```

## Display Components

### 1. **Recent Detections Table** (`/frontend/components/RecentDetections.tsx`)
**Location**: Main dashboard bottom section

**Displays**:
- **Ports Column**: Shows source → destination port mapping
  - Format: `54321 → 443` (source port → dest port)
  - Destination ports highlighted in orange
  - Missing ports shown as `-`
  
- **Protocol Column**: Blue badge with protocol name
  - Background: `bg-blue-500/20`
  - Border: `border-blue-500/40`
  - Text: `text-blue-400 font-semibold`
  - Shows: TCP, UDP, ICMP

**Example Data**:
```
Time      | Source IP       | Dest IP        | Ports        | Protocol | Score
10:30:45  | 192.168.0.60   | 192.168.1.44   | 58375 → 1521 | [TCP]    | 91.5%
10:30:44  | 192.168.0.60   | 192.168.1.32   | 41864 → 3306 | [TCP]    | 90.8%
```

---

### 2. **Live Packet Capture** (`/frontend/components/LivePacketCapture.tsx`)
**Location**: Main dashboard top section

**Displays**:
- Protocol badge (blue theme)
- Port number when available
- Format: `[TCP] • Port 443 • Score: 0.915`

**Real-time Updates**: Every 2 seconds

---

### 3. **Port Activity Dashboard** (`/frontend/components/PortActivityDashboard.tsx`)
**Location**: Main dashboard and `/ports` page

**Three Main Sections**:

#### A. Most Targeted Ports
Shows ports under attack with:
- Large port number display
- Protocol badge (blue) next to port
- Threat level badge (color-coded)
- Statistics: Total hits, anomalies, avg score

**Example**:
```
Port 3306  [TCP]  [HIGH]
Total: 334 • Anomalies: 298 • Avg Score: 89.3%
```

#### B. Likely Open Ports
Shows active services:
- Port number
- Protocol badge (blue)
- Service name (SSH, HTTP, MySQL, RDP, etc.)
- Confidence bar
- Connection count

**Example**:
```
Port 443  [TCP]  HTTPS    95% [========] 310 connections
```

#### C. Port Scanners Table
Comprehensive scanner detection:
- Columns: Source IP | **Protocol** | Ports Targeted | Total Packets | Scan Type | Duration
- Protocol shown in dedicated column with blue TCP badge
- Scan types: Full Scan, Range Scan, Targeted Scan, Probe

**Example**:
```
Source IP        | Protocol | Ports Targeted | Total Packets | Scan Type
192.168.0.61    | [TCP]    | 32 ports      | 542          | Targeted Scan
```

---

### 4. **Attack Detail Pages** (`/frontend/app/attacks/[type]/page.tsx`)
**Location**: `/attacks/port_scan`, `/attacks/dos_ddos`, etc.

**Port Scan Specific Features**:
- Target Port column with:
  - Orange badge showing port number
  - Service name below (SSH, HTTP, MySQL, RDP, etc.)
  - Format: `[Port 3389]` with `RDP` label

- Protocol column with blue badge
- SYN flag indicator for TCP scans

**Detection Table Columns**:
```
Timestamp | Source IP | Dest IP | Target Port | Protocol | Anomaly Score | Severity
```

**Service Name Mapping**: 25+ common services
- Port 22: SSH
- Port 80: HTTP
- Port 443: HTTPS
- Port 3306: MySQL
- Port 3389: RDP
- Port 5432: PostgreSQL
- And more...

---

## API Endpoints

### `/api/detections/recent`
Returns packet data with ports:
```json
{
  "id": 14187,
  "timestamp": "2025-11-22T11:57:02.092311",
  "source_ip": "192.168.0.60",
  "dest_ip": "192.168.1.44",
  "source_port": 58375,
  "dest_port": 1521,
  "protocol": "TCP",
  "anomaly_score": 0.9145,
  "is_anomaly": true,
  "severity": "high"
}
```

### `/api/ports/targeted`
Most attacked ports:
```json
{
  "port": 3306,
  "protocol": "TCP",
  "total_hits": 334,
  "anomaly_hits": 298,
  "avg_anomaly_score": 0.8930,
  "threat_level": "high"
}
```

### `/api/ports/scanners`
Active port scanners:
```json
{
  "source_ip": "192.168.0.61",
  "ports_targeted": 32,
  "total_packets": 542,
  "first_seen": "2025-11-22T11:30:15",
  "last_seen": "2025-11-22T11:57:02",
  "scan_type": "Targeted Scan"
}
```

### `/api/ports/open`
Likely open services:
```json
{
  "port": 443,
  "protocol": "TCP",
  "confidence": 95,
  "connections": 310,
  "service": "HTTPS"
}
```

---

## Current Data Statistics

Based on latest database query:

### Top Ports by Traffic:
1. **Port 0 (ICMP)**: 1,965 packets - Network diagnostics
2. **Port 3306 (TCP)**: 334 packets - MySQL database scans
3. **Port 25 (TCP)**: 323 packets - SMTP email server
4. **Port 443 (TCP)**: 310 packets - HTTPS web traffic
5. **Port 8080 (TCP)**: 305 packets - HTTP alternate
6. **Port 22 (TCP)**: 304 packets - SSH remote access
7. **Port 80 (TCP)**: 300 packets - HTTP web traffic
8. **Port 110 (TCP)**: 295 packets - POP3 email
9. **Port 143 (TCP)**: 285 packets - IMAP email
10. **Port 67 (UDP)**: 269 packets - DHCP

### Protocol Distribution:
- **TCP**: ~60% (Web, Database, Email, Remote Access)
- **UDP**: ~25% (DNS, DHCP, NTP, SNMP, Syslog)
- **ICMP**: ~15% (Ping, Network diagnostics)

### Active Scanners:
- **192.168.0.61**: 32 unique ports scanned
- **192.168.0.75**: 31 unique ports scanned
- **192.168.0.64**: 30 unique ports scanned

---

## Visual Theme

### Protocol Badges (Blue Theme - All Components)
```css
background: bg-blue-500/20
border: border-blue-500/40
text: text-blue-400
font-weight: font-semibold
```

### Port Number Highlights
- **Destination Ports**: Orange (`text-orange-400`)
- **Source Ports**: Gray (`text-gray-300`)
- **Port in Badges**: Orange background with border

### Threat Level Colors
- **Critical**: Red (`text-red-400 bg-red-500/10`)
- **High**: Orange (`text-orange-400 bg-orange-500/10`)
- **Medium**: Yellow (`text-yellow-400 bg-yellow-500/10`)
- **Low**: Blue (`text-blue-400 bg-blue-500/10`)

---

## Real-Time Updates

All components refresh automatically:
- **Live Packet Capture**: 2 seconds
- **Recent Detections**: 5 seconds
- **Port Activity Dashboard**: 10 seconds
- **Attack Detail Pages**: 5 seconds

---

## Service Name Resolution

The system recognizes 26 common services by port number:

| Port  | Service       | Port  | Service      | Port  | Service      |
|-------|---------------|-------|--------------|-------|--------------|
| 20    | FTP Data      | 443   | HTTPS        | 3306  | MySQL        |
| 21    | FTP           | 445   | SMB          | 3389  | RDP          |
| 22    | SSH           | 993   | IMAPS        | 5432  | PostgreSQL   |
| 23    | Telnet        | 995   | POP3S        | 5900  | VNC          |
| 25    | SMTP          | 1433  | MSSQL        | 6379  | Redis        |
| 53    | DNS           | 1521  | Oracle       | 8080  | HTTP-Alt     |
| 80    | HTTP          | 111   | RPC          | 8443  | HTTPS-Alt    |
| 110   | POP3          | 135   | MSRPC        | 27017 | MongoDB      |
| 143   | IMAP          | 139   | NetBIOS      |       |              |

---

## Testing & Verification

To verify port/protocol display:

1. **Check Database**:
```bash
python -c "
import sqlite3
conn = sqlite3.connect('data/detections.db')
cursor = conn.cursor()
cursor.execute('SELECT dest_port, protocol, COUNT(*) FROM detections GROUP BY dest_port, protocol LIMIT 10')
for row in cursor.fetchall():
    print(f'Port {row[0]} | {row[1]} | {row[2]} packets')
"
```

2. **Test API**:
```bash
curl http://localhost:5000/api/detections/recent?limit=3 | python -m json.tool
```

3. **View Frontend**:
- Main Dashboard: http://localhost:3000
- Port Monitor: http://localhost:3000/ports
- Attack Details: http://localhost:3000/attacks/port_scan

---

## Summary

✅ **All components show accurate port numbers** from database  
✅ **Protocols displayed with consistent blue badges** throughout UI  
✅ **Source and destination ports** clearly distinguished  
✅ **Service names** resolved for 26+ common ports  
✅ **Real-time updates** ensure current information  
✅ **Color-coded threat levels** for quick assessment  
✅ **Scanner detection** identifies IPs scanning multiple ports  
✅ **Complete data flow** from packet capture → database → API → frontend

The system provides comprehensive port and protocol visibility for effective network security monitoring.
