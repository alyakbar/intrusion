"""
Packet filtering module for network traffic analysis.
Supports BPF-style and custom filtering rules.
"""

from typing import Dict, Any, List, Optional, Callable
import re
from ..utils.logger import LoggerFactory


class PacketFilter:
    """Advanced packet filtering with BPF-style syntax and custom rules."""
    
    def __init__(self):
        """Initialize packet filter."""
        self.logger = LoggerFactory.get_logger('PacketFilter')
        self.rules = []
    
    def add_rule(self, rule: str):
        """
        Add a filtering rule.
        
        Args:
            rule: Filter rule string (BPF-style or custom)
        """
        self.rules.append(rule)
        self.logger.info(f"Added filter rule: {rule}")
    
    def clear_rules(self):
        """Clear all filtering rules."""
        self.rules = []
        self.logger.info("Cleared all filter rules")
    
    def matches(self, packet_data: Dict[str, Any]) -> bool:
        """
        Check if packet matches all filter rules.
        
        Args:
            packet_data: Packet data dictionary
            
        Returns:
            True if packet matches all rules, False otherwise
        """
        if not self.rules:
            return True  # No filters = accept all
        
        for rule in self.rules:
            if not self._evaluate_rule(rule, packet_data):
                return False
        
        return True
    
    def _evaluate_rule(self, rule: str, packet_data: Dict[str, Any]) -> bool:
        """Evaluate a single filter rule."""
        rule = rule.lower().strip()
        
        # Protocol filters
        if rule == 'tcp':
            return packet_data.get('protocol', '').upper() == 'TCP'
        if rule == 'udp':
            return packet_data.get('protocol', '').upper() == 'UDP'
        if rule == 'icmp':
            return packet_data.get('protocol', '').upper() == 'ICMP'
        
        # Port filters
        if 'port' in rule:
            match = re.search(r'port\s+(\d+)', rule)
            if match:
                port = int(match.group(1))
                src_port = packet_data.get('src_port', 0)
                dst_port = packet_data.get('dst_port', 0)
                
                if 'src' in rule:
                    return src_port == port
                elif 'dst' in rule:
                    return dst_port == port
                else:
                    return src_port == port or dst_port == port
        
        # Port range filters
        if 'portrange' in rule:
            match = re.search(r'portrange\s+(\d+)-(\d+)', rule)
            if match:
                port_min = int(match.group(1))
                port_max = int(match.group(2))
                src_port = packet_data.get('src_port', 0)
                dst_port = packet_data.get('dst_port', 0)
                
                return (port_min <= src_port <= port_max) or (port_min <= dst_port <= port_max)
        
        # Host/IP filters
        if 'host' in rule:
            match = re.search(r'host\s+([\d\.]+)', rule)
            if match:
                ip = match.group(1)
                src_ip = packet_data.get('src_ip', '')
                dst_ip = packet_data.get('dst_ip', '')
                
                if 'src' in rule:
                    return src_ip == ip
                elif 'dst' in rule:
                    return dst_ip == ip
                else:
                    return src_ip == ip or dst_ip == ip
        
        # Network/subnet filters
        if 'net' in rule:
            match = re.search(r'net\s+([\d\.]+/\d+)', rule)
            if match:
                network = match.group(1)
                # Simplified subnet matching (can be enhanced with ipaddress module)
                src_ip = packet_data.get('src_ip', '')
                dst_ip = packet_data.get('dst_ip', '')
                network_prefix = network.split('/')[0].rsplit('.', 1)[0]
                
                return src_ip.startswith(network_prefix) or dst_ip.startswith(network_prefix)
        
        # Length filters
        if 'len' in rule or 'length' in rule:
            match = re.search(r'(?:len|length)\s*([<>=]+)\s*(\d+)', rule)
            if match:
                operator = match.group(1)
                threshold = int(match.group(2))
                packet_len = packet_data.get('packet_length', 0)
                
                if operator == '>':
                    return packet_len > threshold
                elif operator == '<':
                    return packet_len < threshold
                elif operator == '>=':
                    return packet_len >= threshold
                elif operator == '<=':
                    return packet_len <= threshold
                elif operator == '==':
                    return packet_len == threshold
        
        # Compound rules (AND, OR)
        if ' and ' in rule:
            parts = rule.split(' and ')
            return all(self._evaluate_rule(part.strip(), packet_data) for part in parts)
        
        if ' or ' in rule:
            parts = rule.split(' or ')
            return any(self._evaluate_rule(part.strip(), packet_data) for part in parts)
        
        # Negation
        if rule.startswith('not '):
            inner_rule = rule[4:].strip()
            return not self._evaluate_rule(inner_rule, packet_data)
        
        return True  # Unknown rule = accept


class FilterPreset:
    """Predefined filter presets for common use cases."""
    
    @staticmethod
    def web_traffic() -> List[str]:
        """Filter for HTTP/HTTPS traffic."""
        return ['tcp', 'port 80 or port 443']
    
    @staticmethod
    def dns_traffic() -> List[str]:
        """Filter for DNS traffic."""
        return ['udp', 'port 53']
    
    @staticmethod
    def ssh_traffic() -> List[str]:
        """Filter for SSH traffic."""
        return ['tcp', 'port 22']
    
    @staticmethod
    def database_traffic() -> List[str]:
        """Filter for common database ports."""
        return ['tcp', 'port 3306 or port 5432 or port 27017 or port 6379']
    
    @staticmethod
    def high_ports() -> List[str]:
        """Filter for high/ephemeral ports."""
        return ['portrange 49152-65535']
    
    @staticmethod
    def large_packets() -> List[str]:
        """Filter for large packets (>1000 bytes)."""
        return ['length > 1000']
    
    @staticmethod
    def local_network(subnet: str = '192.168.0.0/16') -> List[str]:
        """Filter for local network traffic."""
        return [f'net {subnet}']
    
    @staticmethod
    def scan_detection() -> List[str]:
        """Filter for potential port scanning activity."""
        return ['tcp', 'portrange 1-1024']
