"""
Flask API server for Network Anomaly Detection Frontend
Provides REST endpoints to query detection data from SQLite database
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
from typing import Dict, List, Any
import tempfile
import socket
import threading

app = Flask(__name__)
CORS(app)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'detections.db')

# Hostname cache
_hostname_cache = {}
_hostname_cache_lock = threading.Lock()


def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_hostname(ip: str, timeout: float = 0.3) -> str:
    """
    Get hostname for an IP address with caching
    Returns hostname or None if not found
    """
    if not ip or ip == 'N/A':
        return None
    
    # Skip private/local IPs - they rarely have meaningful hostnames
    if ip.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.', 
                      '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                      '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.',
                      '127.', 'localhost', '::1', 'fe80:')):
        return None
    
    # Check cache first
    with _hostname_cache_lock:
        if ip in _hostname_cache:
            return _hostname_cache[ip]
    
    # Try to resolve with timeout using threading
    hostname_result = [None]
    
    def resolve():
        try:
            hostname_result[0] = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror, socket.timeout, OSError):
            hostname_result[0] = None
    
    resolve_thread = threading.Thread(target=resolve, daemon=True)
    resolve_thread.start()
    resolve_thread.join(timeout=timeout)
    
    hostname = hostname_result[0]
    
    if hostname and hostname != ip:
        # Clean up hostname
        # Extract domain name (e.g., github.com from lb-140-82-112-21-iad.github.com)
        parts = hostname.split('.')
        if len(parts) >= 2:
            # Common patterns: service.domain.com, subdomain.domain.com
            if any(known in hostname.lower() for known in ['google', 'github', 'microsoft', 'azure', 'amazon', 'cloudflare']):
                # Extract main domain
                for i in range(len(parts) - 1):
                    test_domain = '.'.join(parts[i:])
                    if any(known in test_domain.lower() for known in ['google.com', 'github.com', 'microsoft.com', 'azure.com', 'amazonaws.com', 'cloudflare.com']):
                        hostname = test_domain
                        break
        
        # Cache the result
        with _hostname_cache_lock:
            _hostname_cache[ip] = hostname
        return hostname
    
    # Cache negative result
    with _hostname_cache_lock:
        _hostname_cache[ip] = None
    return None


def classify_attack_type(packet_data: str, protocol: str, anomaly_score: float) -> str:
    """
    Classify attack type based on packet characteristics
    In production, this would use more sophisticated pattern matching
    """
    packet_lower = (packet_data or '').lower()
    protocol_lower = (protocol or '').lower()
    
    # DoS/DDoS detection (including ICMP floods)
    if 'syn' in packet_lower or 'flood' in packet_lower:
        return 'dos_ddos'
    
    # ICMP should be classified as dos_ddos (ping floods) not port scanning
    if protocol_lower == 'icmp':
        return 'dos_ddos'
    
    # Port scanning (TCP/UDP only, not ICMP)
    if 'scan' in packet_lower or protocol_lower == 'syn':
        return 'port_scan'
    
    # Brute force
    if 'auth' in packet_lower or 'login' in packet_lower or 'ssh' in packet_lower:
        return 'brute_force'
    
    # SQL Injection & XSS
    if 'sql' in packet_lower or 'script' in packet_lower or 'select' in packet_lower:
        return 'sql_xss'
    
    # Backdoor/Botnet (command patterns)
    if 'cmd' in packet_lower or 'exec' in packet_lower or 'shell' in packet_lower:
        return 'backdoor_botnet'
    
    # Data exfiltration (large transfers)
    if 'upload' in packet_lower or 'download' in packet_lower or anomaly_score > 0.95:
        return 'data_exfiltration'
    
    # MITM attacks
    if 'arp' in packet_lower or 'dns' in packet_lower or 'spoof' in packet_lower:
        return 'mitm'
    
    # Zero-day (high anomaly score with no clear pattern)
    if anomaly_score > 0.9:
        return 'zero_day'
    
    return 'unknown'


@app.route('/api/detections/stats', methods=['GET'])
def get_stats():
    """Get overall detection statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total detections
        cursor.execute('SELECT COUNT(*) as total FROM detections')
        total = cursor.fetchone()['total']
        
        # Anomalies
        cursor.execute('SELECT COUNT(*) as anomalies FROM detections WHERE is_anomaly = 1')
        anomalies = cursor.fetchone()['anomalies']
        
        # By severity
        cursor.execute('''
            SELECT severity, COUNT(*) as count 
            FROM detections 
            WHERE is_anomaly = 1 AND severity IS NOT NULL
            GROUP BY severity
        ''')
        severity_counts = {row['severity']: row['count'] for row in cursor.fetchall()}
        
        # Recent activity (last hour) - use local time comparison
        from datetime import datetime, timedelta
        threshold_1h = (datetime.now() - timedelta(hours=1)).isoformat()
        cursor.execute('''
            SELECT COUNT(*) as recent 
            FROM detections 
            WHERE timestamp > ?
        ''', (threshold_1h,))
        recent = cursor.fetchone()['recent']
        
        conn.close()
        
        return jsonify({
            'total_packets': total,
            'total_anomalies': anomalies,
            'anomaly_rate': round((anomalies / total * 100) if total > 0 else 0, 2),
            'severity_counts': {
                'high': severity_counts.get('high', 0),
                'medium': severity_counts.get('medium', 0),
                'low': severity_counts.get('low', 0)
            },
            'recent_activity': recent
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detections/by-type', methods=['GET'])
def get_detections_by_type():
    """Get anomalies categorized by attack type"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, source_ip, dest_ip, source_port, dest_port, 
                   protocol, anomaly_score, severity, raw_packet
            FROM detections 
            WHERE is_anomaly = 1
            ORDER BY timestamp DESC
            LIMIT 500
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Classify each detection
        attack_types = {
            'dos_ddos': [],
            'port_scan': [],
            'brute_force': [],
            'sql_xss': [],
            'backdoor_botnet': [],
            'data_exfiltration': [],
            'mitm': [],
            'zero_day': [],
            'unknown': []
        }
        
        for row in rows:
            attack_type = classify_attack_type(
                row['raw_packet'], 
                row['protocol'], 
                row['anomaly_score']
            )
            
            attack_types[attack_type].append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'source_ip': row['source_ip'],
                'dest_ip': row['dest_ip'],
                'source_port': row['source_port'],
                'dest_port': row['dest_port'],
                'protocol': row['protocol'],
                'anomaly_score': row['anomaly_score'],
                'severity': row['severity']
            })
        
        # Get counts
        type_counts = {k: len(v) for k, v in attack_types.items()}
        
        return jsonify({
            'counts': type_counts,
            'detections': attack_types
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detections/timeline', methods=['GET'])
def get_timeline():
    """Get detection timeline for charts"""
    try:
        hours = int(request.args.get('hours', 24))
        from datetime import datetime, timedelta
        threshold = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as total,
                SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomalies
            FROM detections
            WHERE timestamp > ?
            GROUP BY hour
            ORDER BY hour ASC
        ''', (threshold,))
        
        rows = cursor.fetchall()
        conn.close()
        
        timeline = [
            {
                'timestamp': row['hour'],
                'total': row['total'],
                'anomalies': row['anomalies']
            }
            for row in rows
        ]
        
        return jsonify(timeline)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detections/recent', methods=['GET'])
def get_recent():
    """Get most recent detections"""
    try:
        limit = int(request.args.get('limit', 50))
        # Cap at 100 to prevent performance issues
        limit = min(limit, 100)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT id, timestamp, source_ip, dest_ip, source_port, dest_port, 
                   protocol, anomaly_score, is_anomaly, severity, threat_score
            FROM detections
            ORDER BY id DESC
            LIMIT {limit}
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        detections = []
        # Only resolve hostnames for first 20 records to avoid blocking
        for idx, row in enumerate(rows):
            # Skip hostname resolution for older records to prevent API hang
            if idx < 20:
                source_hostname = get_hostname(row['source_ip'])
                dest_hostname = get_hostname(row['dest_ip'])
            else:
                source_hostname = None
                dest_hostname = None
            
            detections.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'source_ip': row['source_ip'],
                'source_hostname': source_hostname,
                'dest_ip': row['dest_ip'],
                'dest_hostname': dest_hostname,
                'source_port': row['source_port'],
                'dest_port': row['dest_port'],
                'protocol': row['protocol'],
                'anomaly_score': row['anomaly_score'],
                'is_anomaly': bool(row['is_anomaly']),
                'severity': row['severity'],
                'threat_score': row['threat_score'] if row['threat_score'] is not None else 0.0
            })
        
        return jsonify(detections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/detections/top-sources', methods=['GET'])
def get_top_sources():
    """Get top source IPs with anomalies"""
    try:
        limit = int(request.args.get('limit', 10))
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(f'''
            SELECT source_ip, COUNT(*) as count,
                   AVG(anomaly_score) as avg_score
            FROM detections
            WHERE is_anomaly = 1 AND source_ip IS NOT NULL
            GROUP BY source_ip
            ORDER BY count DESC
            LIMIT {limit}
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        sources = [
            {
                'ip': row['source_ip'],
                'count': row['count'],
                'avg_score': round(row['avg_score'], 4)
            }
            for row in rows
        ]
        
        return jsonify(sources)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})


@app.route('/api/capture/status', methods=['GET'])
def get_capture_status():
    """Get real-time capture status and statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for recent activity (last 10 seconds)
        cursor.execute('''
            SELECT COUNT(*) as recent_count
            FROM detections
            WHERE datetime(timestamp) > datetime('now', '-10 seconds')
        ''')
        recent_count = cursor.fetchone()['recent_count']
        is_active = recent_count > 0
        
        # Get last packet timestamp
        cursor.execute('SELECT timestamp FROM detections ORDER BY id DESC LIMIT 1')
        last_row = cursor.fetchone()
        last_packet_time = last_row['timestamp'] if last_row else None
        
        # Get rate stats (packets per minute in last 5 minutes)
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM detections
            WHERE datetime(timestamp) > datetime('now', '-5 minutes')
        ''')
        last_5min = cursor.fetchone()['count']
        packets_per_minute = last_5min / 5.0 if last_5min > 0 else 0
        
        # Get anomaly rate in last minute
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_anomaly = 1 THEN 1 ELSE 0 END) as anomalies
            FROM detections
            WHERE datetime(timestamp) > datetime('now', '-1 minute')
        ''')
        last_min = cursor.fetchone()
        recent_anomaly_rate = (last_min['anomalies'] / last_min['total'] * 100) if last_min['total'] > 0 else 0
        
        conn.close()
        
        return jsonify({
            'is_active': is_active,
            'last_packet_time': last_packet_time,
            'recent_packet_count': recent_count,
            'packets_per_minute': round(packets_per_minute, 2),
            'recent_anomaly_rate': round(recent_anomaly_rate, 2),
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'is_active': False,
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


@app.route('/api/ports/targeted', methods=['GET'])
def get_targeted_ports():
    """Get ports being targeted in attacks"""
    try:
        limit = int(request.args.get('limit', 50))
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                dest_port,
                COUNT(*) as hit_count,
                COUNT(CASE WHEN is_anomaly = 1 THEN 1 END) as anomaly_count,
                AVG(CASE WHEN is_anomaly = 1 THEN anomaly_score ELSE 0 END) as avg_score,
                protocol
            FROM detections
            WHERE dest_port IS NOT NULL AND dest_port > 0 AND protocol != 'ICMP'
            GROUP BY dest_port, protocol
            ORDER BY anomaly_count DESC, hit_count DESC
            LIMIT ?
        """, (limit,))
        
        ports = []
        for row in cursor.fetchall():
            anomaly_rate = row['anomaly_count'] / row['hit_count'] if row['hit_count'] > 0 else 0
            
            # Calculate threat level
            if anomaly_rate > 0.7 and row['avg_score'] > 0.8:
                threat_level = 'critical'
            elif anomaly_rate > 0.5 or row['avg_score'] > 0.7:
                threat_level = 'high'
            elif anomaly_rate > 0.3 or row['avg_score'] > 0.5:
                threat_level = 'medium'
            else:
                threat_level = 'low'
            
            ports.append({
                'port': row['dest_port'],
                'protocol': row['protocol'],
                'total_hits': row['hit_count'],
                'anomaly_hits': row['anomaly_count'],
                'avg_anomaly_score': round(row['avg_score'], 4),
                'threat_level': threat_level
            })
        
        conn.close()
        return jsonify(ports)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ports/scanners', methods=['GET'])
def get_port_scanners():
    """Detect potential port scanning activity"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find IPs scanning multiple ports (exclude ICMP)
        cursor.execute("""
            SELECT 
                source_ip,
                COUNT(DISTINCT dest_port) as unique_ports,
                COUNT(*) as total_packets,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM detections
            WHERE dest_port IS NOT NULL AND dest_port > 0 AND protocol != 'ICMP'
            GROUP BY source_ip
            HAVING unique_ports > 5
            ORDER BY unique_ports DESC
            LIMIT 20
        """)
        
        scanners = []
        for row in cursor.fetchall():
            unique_ports = row['unique_ports']
            total_packets = row['total_packets']
            
            # Classify scan type
            if unique_ports > 1000:
                scan_type = 'Full Scan'
            elif unique_ports > 100:
                scan_type = 'Range Scan'
            elif unique_ports > 20:
                scan_type = 'Targeted Scan'
            else:
                scan_type = 'Probe'
            
            scanners.append({
                'source_ip': row['source_ip'],
                'ports_targeted': unique_ports,
                'total_packets': total_packets,
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'scan_type': scan_type
            })
        
        conn.close()
        return jsonify({
            'suspected_scanners': scanners,
            'total_scanners': len(scanners)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ports/open', methods=['GET'])
def get_open_ports():
    """Infer likely open ports from traffic patterns"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Ports with consistent bidirectional traffic (likely open, exclude ICMP)
        cursor.execute("""
            SELECT 
                dest_port,
                protocol,
                COUNT(*) as connection_attempts,
                COUNT(CASE WHEN is_anomaly = 0 THEN 1 END) as normal_traffic
            FROM detections
            WHERE dest_port IS NOT NULL AND dest_port > 0 AND protocol != 'ICMP'
            GROUP BY dest_port, protocol
            HAVING normal_traffic > 5
            ORDER BY normal_traffic DESC
            LIMIT 30
        """)
        
        services = {
            20: 'FTP Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
            25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
            143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
            3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC',
            6379: 'Redis', 8080: 'HTTP-Alt', 27017: 'MongoDB',
            5000: 'Flask', 3000: 'Node.js', 8443: 'HTTPS-Alt'
        }
        
        open_ports = []
        for row in cursor.fetchall():
            confidence = min(100, int(row['normal_traffic'] / row['connection_attempts'] * 100))
            
            open_ports.append({
                'port': row['dest_port'],
                'protocol': row['protocol'],
                'confidence': confidence,
                'connections': row['connection_attempts'],
                'service': services.get(row['dest_port'], 'Unknown')
            })
        
        conn.close()
        return jsonify(open_ports)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ports/distribution', methods=['GET'])
def get_port_distribution():
    """Get distribution of service categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dest_port, COUNT(*) as count
            FROM detections
            WHERE dest_port IS NOT NULL
            GROUP BY dest_port
        """)
        
        categories = {
            'Web (HTTP/HTTPS)': 0,
            'Remote Access': 0,
            'Email': 0,
            'DNS': 0,
            'Database': 0,
            'Windows Services': 0,
            'Remote Desktop': 0,
            'Registered Ports': 0,
            'Dynamic/Private': 0,
            'Other': 0
        }
        
        for row in cursor.fetchall():
            port = row['dest_port']
            count = row['count']
            
            if port in [80, 443, 8080, 8443]:
                categories['Web (HTTP/HTTPS)'] += count
            elif port in [20, 21, 22, 23]:
                categories['Remote Access'] += count
            elif port in [25, 110, 143, 587, 993, 995]:
                categories['Email'] += count
            elif port == 53:
                categories['DNS'] += count
            elif port in [3306, 5432, 1433, 27017, 6379]:
                categories['Database'] += count
            elif port in [445, 139, 135]:
                categories['Windows Services'] += count
            elif port in [3389, 5900]:
                categories['Remote Desktop'] += count
            elif 1024 <= port <= 49151:
                categories['Registered Ports'] += count
            elif port > 49151:
                categories['Dynamic/Private'] += count
            else:
                categories['Other'] += count
        
        conn.close()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/generate', methods=['GET'])
def generate_report():
    """Generate detection report in specified format"""
    try:
        from anomaly_detection.utils.config import load_config
        from anomaly_detection.reporting.report_generator import ReportGenerator
        
        # Get parameters
        report_format = request.args.get('format', 'pdf').lower()
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        include_charts = request.args.get('include_charts', 'true').lower() == 'true'
        
        # Parse dates
        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
        
        # Load config
        config = load_config('configs/config.yaml')
        
        # Generate report
        generator = ReportGenerator(config)
        
        # Create temp file
        suffix = '.pdf' if report_format == 'pdf' else '.csv'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            output_path = tmp_file.name
        
        result = generator.generate_report(
            output_path=output_path,
            format=report_format,
            start_date=start_date,
            end_date=end_date,
            include_charts=include_charts
        )
        
        if result['status'] == 'success':
            # Return file
            mimetype = 'application/pdf' if report_format == 'pdf' else 'text/csv'
            filename = f"detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}{suffix}"
            
            return send_file(
                output_path,
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Check if detection process is actually running"""
    try:
        import subprocess
        import psutil
        
        # Check for running detection process
        detection_running = False
        detection_pid = None
        detection_info = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if cmdline and 'python' in cmdline[0].lower():
                    # Check if it's running anomaly detection
                    cmdline_str = ' '.join(cmdline)
                    if 'anomaly_detection/main.py' in cmdline_str and '--mode detect' in cmdline_str:
                        detection_running = True
                        detection_pid = proc.info['pid']
                        
                        # Extract parameters
                        detection_info = {
                            'pid': detection_pid,
                            'interface': None,
                            'backend': None,
                            'inject_rate': None
                        }
                        
                        # Parse command line arguments
                        for i, arg in enumerate(cmdline):
                            if arg == '--interface' and i + 1 < len(cmdline):
                                detection_info['interface'] = cmdline[i + 1]
                            elif arg == '--backend' and i + 1 < len(cmdline):
                                detection_info['backend'] = cmdline[i + 1]
                            elif arg == '--inject-rate' and i + 1 < len(cmdline):
                                detection_info['inject_rate'] = float(cmdline[i + 1])
                        
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Check database for recent activity (last 30 seconds)
        # Handle timezone: database uses local time, compare with local time
        from datetime import datetime, timedelta
        now_local = datetime.now()
        threshold = (now_local - timedelta(seconds=30)).isoformat()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) as recent_count, MAX(timestamp) as latest
            FROM detections
            WHERE timestamp > ?
        ''', (threshold,))
        row = cursor.fetchone()
        recent_count = row['recent_count']
        latest_timestamp = row['latest']
        conn.close()
        
        # Check network interface status
        interface_up = False
        interface_info = {}
        if detection_running and detection_info.get('interface'):
            try:
                iface = detection_info['interface']
                result = subprocess.run(
                    ['ip', 'addr', 'show', iface],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                if result.returncode == 0:
                    output = result.stdout
                    interface_up = 'state UP' in output and 'inet ' in output
                    
                    # Extract IP address
                    if 'inet ' in output:
                        for line in output.split('\n'):
                            if 'inet ' in line:
                                ip_addr = line.strip().split()[1]
                                interface_info = {
                                    'name': iface,
                                    'status': 'up' if interface_up else 'down',
                                    'ip': ip_addr if interface_up else None
                                }
                                break
            except Exception:
                pass
        
        # Determine actual status
        is_capturing = detection_running and recent_count > 0
        
        # Determine status message
        if not detection_running:
            status = 'stopped'
            status_message = 'Detection process not running'
        elif not interface_up and detection_info.get('interface'):
            status = 'waiting'
            status_message = f"Waiting for interface {detection_info['interface']} to come up"
        elif is_capturing:
            status = 'active'
            status_message = 'Actively capturing packets'
        else:
            status = 'idle'
            status_message = 'Running but no recent packets'
        
        return jsonify({
            'detection_process_running': detection_running,
            'is_capturing_packets': is_capturing,
            'recent_packets_30s': recent_count,
            'latest_packet_time': latest_timestamp,
            'process_info': detection_info if detection_running else None,
            'interface_info': interface_info if interface_info else None,
            'status': status,
            'status_message': status_message
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Disable debug mode to prevent reload issues
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
