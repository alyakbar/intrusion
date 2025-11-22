"""
Active Port Scanner
Discovers open ports on target hosts/networks
"""

import socket
import concurrent.futures
from typing import List, Dict, Tuple, Optional
import ipaddress
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PortScanner:
    """Network port scanner with concurrent scanning capabilities"""
    
    COMMON_PORTS = {
        20: 'FTP Data',
        21: 'FTP Control',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        445: 'SMB',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        5900: 'VNC',
        6379: 'Redis',
        8080: 'HTTP Proxy',
        8443: 'HTTPS Alt',
        27017: 'MongoDB',
        3000: 'Node.js',
        5000: 'Flask',
        8000: 'Django',
        9200: 'Elasticsearch'
    }
    
    def __init__(self, timeout: float = 1.0, max_workers: int = 100):
        """
        Initialize port scanner
        
        Args:
            timeout: Socket connection timeout in seconds
            max_workers: Maximum concurrent scanning threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
    
    def scan_port(self, host: str, port: int) -> Tuple[int, bool, Optional[str]]:
        """
        Scan a single port on a host
        
        Args:
            host: Target IP address or hostname
            port: Port number to scan
            
        Returns:
            Tuple of (port, is_open, service_name)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self.timeout)
                result = sock.connect_ex((host, port))
                
                if result == 0:
                    service = self.COMMON_PORTS.get(port, 'Unknown')
                    return (port, True, service)
                    
        except socket.gaierror:
            logger.error(f"Hostname {host} could not be resolved")
        except socket.error as e:
            logger.debug(f"Error scanning {host}:{port} - {e}")
        
        return (port, False, None)
    
    def scan_host(self, host: str, ports: List[int] = None) -> Dict:
        """
        Scan multiple ports on a single host
        
        Args:
            host: Target IP address or hostname
            ports: List of ports to scan (default: common ports)
            
        Returns:
            Dictionary with scan results
        """
        if ports is None:
            ports = list(self.COMMON_PORTS.keys())
        
        logger.info(f"Scanning {host} for {len(ports)} ports...")
        start_time = datetime.now()
        
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_port = {
                executor.submit(self.scan_port, host, port): port 
                for port in ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port, is_open, service = future.result()
                if is_open:
                    open_ports.append({
                        'port': port,
                        'service': service,
                        'state': 'open'
                    })
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'host': host,
            'timestamp': start_time.isoformat(),
            'duration': duration,
            'ports_scanned': len(ports),
            'open_ports': sorted(open_ports, key=lambda x: x['port']),
            'open_count': len(open_ports)
        }
    
    def scan_range(self, network: str, ports: List[int] = None) -> List[Dict]:
        """
        Scan a network range for open ports
        
        Args:
            network: Network in CIDR notation (e.g., '192.168.1.0/24')
            ports: List of ports to scan
            
        Returns:
            List of scan results for each host
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            hosts = [str(ip) for ip in net.hosts()]
            
            logger.info(f"Scanning {len(hosts)} hosts in {network}")
            
            results = []
            for host in hosts:
                result = self.scan_host(host, ports)
                if result['open_count'] > 0:
                    results.append(result)
            
            return results
            
        except ValueError as e:
            logger.error(f"Invalid network range: {e}")
            return []
    
    def scan_port_range(self, host: str, start_port: int, end_port: int) -> Dict:
        """
        Scan a range of ports on a host
        
        Args:
            host: Target IP address or hostname
            start_port: Starting port number
            end_port: Ending port number
            
        Returns:
            Dictionary with scan results
        """
        ports = list(range(start_port, end_port + 1))
        return self.scan_host(host, ports)
    
    def quick_scan(self, host: str) -> Dict:
        """
        Quick scan of most common ports
        
        Args:
            host: Target IP address or hostname
            
        Returns:
            Dictionary with scan results
        """
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]
        return self.scan_host(host, common_ports)
    
    def full_scan(self, host: str) -> Dict:
        """
        Full scan of all 65535 ports (slow!)
        
        Args:
            host: Target IP address or hostname
            
        Returns:
            Dictionary with scan results
        """
        ports = list(range(1, 65536))
        return self.scan_host(host, ports)
    
    def get_service_name(self, port: int) -> str:
        """Get service name for a port"""
        return self.COMMON_PORTS.get(port, 'Unknown')
