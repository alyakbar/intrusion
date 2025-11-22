"""
Port Traffic Analyzer
Analyzes captured traffic to identify port activity and patterns
"""

import sqlite3
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class PortAnalyzer:
    """Analyzes network traffic for port-related patterns"""
    
    def __init__(self, db_path: str):
        """
        Initialize port analyzer
        
        Args:
            db_path: Path to detections database
        """
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_targeted_ports(self, limit: int = 50) -> List[Dict]:
        """
        Get ports that are being targeted in attacks
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of port activity with counts
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                dest_port,
                COUNT(*) as hit_count,
                COUNT(CASE WHEN is_anomaly = 1 THEN 1 END) as anomaly_count,
                AVG(CASE WHEN is_anomaly = 1 THEN anomaly_score ELSE 0 END) as avg_score,
                protocol
            FROM detections
            WHERE dest_port IS NOT NULL
            GROUP BY dest_port, protocol
            ORDER BY anomaly_count DESC, hit_count DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'port': row['dest_port'],
                'protocol': row['protocol'],
                'total_hits': row['hit_count'],
                'anomaly_hits': row['anomaly_count'],
                'avg_anomaly_score': round(row['avg_score'], 4),
                'threat_level': self._calculate_threat_level(
                    row['anomaly_count'], 
                    row['hit_count'],
                    row['avg_score']
                )
            })
        
        conn.close()
        return results
    
    def get_port_scan_activity(self) -> Dict:
        """
        Detect potential port scanning activity
        
        Returns:
            Dictionary with port scan statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find IPs scanning multiple ports
        cursor.execute("""
            SELECT 
                source_ip,
                COUNT(DISTINCT dest_port) as unique_ports,
                COUNT(*) as total_packets,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM detections
            WHERE dest_port IS NOT NULL
            GROUP BY source_ip
            HAVING unique_ports > 5
            ORDER BY unique_ports DESC
            LIMIT 20
        """)
        
        scanners = []
        for row in cursor.fetchall():
            scanners.append({
                'source_ip': row['source_ip'],
                'ports_targeted': row['unique_ports'],
                'total_packets': row['total_packets'],
                'first_seen': row['first_seen'],
                'last_seen': row['last_seen'],
                'scan_type': self._classify_scan_type(row['unique_ports'], row['total_packets'])
            })
        
        conn.close()
        return {
            'suspected_scanners': scanners,
            'total_scanners': len(scanners)
        }
    
    def get_port_timeline(self, port: int, hours: int = 24) -> List[Dict]:
        """
        Get activity timeline for a specific port
        
        Args:
            port: Port number
            hours: Time window in hours
            
        Returns:
            List of hourly activity
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT 
                strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                COUNT(*) as total,
                COUNT(CASE WHEN is_anomaly = 1 THEN 1 END) as anomalies,
                protocol
            FROM detections
            WHERE dest_port = ? 
                AND datetime(timestamp) > datetime('now', '-{hours} hours')
            GROUP BY hour, protocol
            ORDER BY hour ASC
        """, (port,))
        
        timeline = []
        for row in cursor.fetchall():
            timeline.append({
                'timestamp': row['hour'],
                'port': port,
                'protocol': row['protocol'],
                'total': row['total'],
                'anomalies': row['anomalies']
            })
        
        conn.close()
        return timeline
    
    def get_service_distribution(self) -> Dict[str, int]:
        """
        Get distribution of common services being accessed
        
        Returns:
            Dictionary mapping port ranges to service categories
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT dest_port, COUNT(*) as count
            FROM detections
            WHERE dest_port IS NOT NULL
            GROUP BY dest_port
        """)
        
        categories = defaultdict(int)
        
        for row in cursor.fetchall():
            port = row['dest_port']
            count = row['count']
            
            # Categorize by port range/service
            if port in [80, 443, 8080, 8443]:
                categories['Web (HTTP/HTTPS)'] += count
            elif port in [20, 21, 22, 23]:
                categories['Remote Access (FTP/SSH/Telnet)'] += count
            elif port in [25, 110, 143, 587, 993, 995]:
                categories['Email (SMTP/POP3/IMAP)'] += count
            elif port in [53]:
                categories['DNS'] += count
            elif port in [3306, 5432, 1433, 27017, 6379]:
                categories['Database'] += count
            elif port in [445, 139, 135]:
                categories['Windows Services (SMB/NetBIOS)'] += count
            elif port in [3389, 5900]:
                categories['Remote Desktop (RDP/VNC)'] += count
            elif 1024 <= port <= 49151:
                categories['Registered Ports'] += count
            elif port > 49151:
                categories['Dynamic/Private Ports'] += count
            else:
                categories['Other'] += count
        
        conn.close()
        return dict(categories)
    
    def get_open_ports_from_traffic(self) -> List[Dict]:
        """
        Infer likely open ports based on successful traffic patterns
        
        Returns:
            List of likely open ports
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ports with consistent bidirectional traffic (likely open)
        cursor.execute("""
            SELECT 
                dest_port,
                protocol,
                COUNT(*) as connection_attempts,
                COUNT(CASE WHEN is_anomaly = 0 THEN 1 END) as normal_traffic
            FROM detections
            WHERE dest_port IS NOT NULL
            GROUP BY dest_port, protocol
            HAVING normal_traffic > 5
            ORDER BY normal_traffic DESC
            LIMIT 30
        """)
        
        open_ports = []
        for row in cursor.fetchall():
            open_ports.append({
                'port': row['dest_port'],
                'protocol': row['protocol'],
                'confidence': min(100, int(row['normal_traffic'] / row['connection_attempts'] * 100)),
                'connections': row['connection_attempts'],
                'service': self._guess_service(row['dest_port'])
            })
        
        conn.close()
        return open_ports
    
    def _calculate_threat_level(self, anomaly_count: int, total_count: int, avg_score: float) -> str:
        """Calculate threat level for a port"""
        anomaly_rate = anomaly_count / total_count if total_count > 0 else 0
        
        if anomaly_rate > 0.7 and avg_score > 0.8:
            return 'critical'
        elif anomaly_rate > 0.5 or avg_score > 0.7:
            return 'high'
        elif anomaly_rate > 0.3 or avg_score > 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _classify_scan_type(self, unique_ports: int, total_packets: int) -> str:
        """Classify type of port scan"""
        if unique_ports > 1000:
            return 'Full Scan'
        elif unique_ports > 100:
            return 'Range Scan'
        elif unique_ports > 20:
            return 'Targeted Scan'
        else:
            return 'Probe'
    
    def _guess_service(self, port: int) -> str:
        """Guess service name from port number"""
        services = {
            20: 'FTP Data', 21: 'FTP', 22: 'SSH', 23: 'Telnet',
            25: 'SMTP', 53: 'DNS', 80: 'HTTP', 110: 'POP3',
            143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 3306: 'MySQL',
            3389: 'RDP', 5432: 'PostgreSQL', 5900: 'VNC',
            6379: 'Redis', 8080: 'HTTP-Alt', 27017: 'MongoDB'
        }
        return services.get(port, 'Unknown')
