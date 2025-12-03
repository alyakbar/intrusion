"""
PCAP file analysis module for offline network traffic analysis.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from ..utils.logger import LoggerFactory
from ..persistence.db import DatabaseManager
from ..inference.alert_manager import AlertManager

try:
    from scapy.all import rdpcap, IP, TCP, UDP, ICMP
    _SCAPY_AVAILABLE = True
except Exception:
    _SCAPY_AVAILABLE = False

try:
    import pyshark
    _PYSHARK_AVAILABLE = True
except Exception:
    _PYSHARK_AVAILABLE = False


class PcapAnalyzer:
    """Analyze PCAP files for anomaly detection."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        model,
        preprocessor,
        alert_manager: Optional[AlertManager] = None,
        backend: str = 'scapy'
    ):
        """
        Initialize PCAP analyzer.
        
        Args:
            config: Configuration dictionary
            model: Trained detection model
            preprocessor: Data preprocessor
            alert_manager: Alert manager instance
            backend: Parser backend ('scapy' or 'pyshark')
        """
        self.config = config
        self.model = model
        self.preprocessor = preprocessor
        self.alert_manager = alert_manager or AlertManager(config)
        self.backend = backend
        self.logger = LoggerFactory.get_logger('PcapAnalyzer')
        self.db_manager = DatabaseManager(config)
        
        # Detection threshold
        rt_config = config.get('realtime', {})
        self.threshold = rt_config.get('threshold', 0.85)
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'anomalies_detected': 0,
            'alerts_generated': 0,
            'start_time': None,
            'end_time': None
        }
        
        # Validate backend
        if backend == 'scapy' and not _SCAPY_AVAILABLE:
            raise ImportError("Scapy not available. Install: pip install scapy")
        if backend == 'pyshark' and not _PYSHARK_AVAILABLE:
            raise ImportError("PyShark not available. Install: pip install pyshark")
    
    def analyze_pcap(self, pcap_path: str, packet_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a PCAP file for anomalies.
        
        Args:
            pcap_path: Path to PCAP file
            packet_filter: Optional BPF filter string
            
        Returns:
            Analysis results dictionary
        """
        pcap_file = Path(pcap_path)
        if not pcap_file.exists():
            raise FileNotFoundError(f"PCAP file not found: {pcap_path}")
        
        self.logger.info(f"Analyzing PCAP file: {pcap_path}")
        self.logger.info(f"Backend: {self.backend}, Filter: {packet_filter or 'None'}")
        
        self.stats['start_time'] = datetime.now()
        
        if self.backend == 'scapy':
            results = self._analyze_with_scapy(pcap_file, packet_filter)
        else:
            results = self._analyze_with_pyshark(pcap_file, packet_filter)
        
        self.stats['end_time'] = datetime.now()
        
        return results
    
    def _analyze_with_scapy(self, pcap_file: Path, packet_filter: Optional[str]) -> Dict[str, Any]:
        """Analyze PCAP using Scapy."""
        self.logger.info("Loading PCAP with Scapy...")
        
        try:
            # Load packets
            packets = rdpcap(str(pcap_file))
            self.logger.info(f"Loaded {len(packets)} packets")
            
            detections = []
            
            for pkt in packets:
                self.stats['total_packets'] += 1
                
                # Extract packet features
                packet_data = self._extract_scapy_features(pkt)
                
                if packet_data:
                    # Apply filter if specified
                    if packet_filter and not self._matches_filter(packet_data, packet_filter):
                        continue
                    
                    # Detect anomaly
                    result = self._process_packet(packet_data)
                    if result['is_anomaly']:
                        detections.append(result)
                
                # Progress logging
                if self.stats['total_packets'] % 1000 == 0:
                    self.logger.info(f"Processed {self.stats['total_packets']} packets...")
            
            return {
                'status': 'success',
                'detections': detections,
                'statistics': self.stats
            }
            
        except Exception as e:
            self.logger.error(f"Scapy analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'statistics': self.stats
            }
    
    def _analyze_with_pyshark(self, pcap_file: Path, packet_filter: Optional[str]) -> Dict[str, Any]:
        """Analyze PCAP using PyShark."""
        self.logger.info("Loading PCAP with PyShark...")
        
        try:
            # Open capture with optional filter
            cap = pyshark.FileCapture(
                str(pcap_file),
                display_filter=packet_filter,
                use_json=True,
                include_raw=True
            )
            
            detections = []
            
            for pkt in cap:
                self.stats['total_packets'] += 1
                
                # Extract packet features
                packet_data = self._extract_pyshark_features(pkt)
                
                if packet_data:
                    # Detect anomaly
                    result = self._process_packet(packet_data)
                    if result['is_anomaly']:
                        detections.append(result)
                
                # Progress logging
                if self.stats['total_packets'] % 1000 == 0:
                    self.logger.info(f"Processed {self.stats['total_packets']} packets...")
            
            cap.close()
            
            return {
                'status': 'success',
                'detections': detections,
                'statistics': self.stats
            }
            
        except Exception as e:
            self.logger.error(f"PyShark analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'statistics': self.stats
            }
    
    def _extract_scapy_features(self, pkt) -> Optional[Dict[str, Any]]:
        """Extract features from Scapy packet."""
        try:
            packet_data = {}
            
            if IP in pkt:
                packet_data['src_ip'] = pkt[IP].src
                packet_data['dst_ip'] = pkt[IP].dst
                packet_data['protocol'] = pkt[IP].proto
                
                if TCP in pkt:
                    packet_data['src_port'] = pkt[TCP].sport
                    packet_data['dst_port'] = pkt[TCP].dport
                    packet_data['protocol'] = 'TCP'
                elif UDP in pkt:
                    packet_data['src_port'] = pkt[UDP].sport
                    packet_data['dst_port'] = pkt[UDP].dport
                    packet_data['protocol'] = 'UDP'
                elif ICMP in pkt:
                    packet_data['src_port'] = 0
                    packet_data['dst_port'] = 0
                    packet_data['protocol'] = 'ICMP'
            
            packet_data['packet_length'] = len(pkt)
            packet_data['timestamp'] = datetime.now().isoformat()
            
            return packet_data if packet_data else None
            
        except Exception as e:
            self.logger.debug(f"Feature extraction failed: {e}")
            return None
    
    def _extract_pyshark_features(self, pkt) -> Optional[Dict[str, Any]]:
        """Extract features from PyShark packet."""
        try:
            packet_data = {}
            
            if hasattr(pkt, 'ip'):
                packet_data['src_ip'] = getattr(pkt.ip, 'src', None)
                packet_data['dst_ip'] = getattr(pkt.ip, 'dst', None)
                
                if hasattr(pkt, 'tcp'):
                    packet_data['src_port'] = int(getattr(pkt.tcp, 'srcport', 0))
                    packet_data['dst_port'] = int(getattr(pkt.tcp, 'dstport', 0))
                    packet_data['protocol'] = 'TCP'
                elif hasattr(pkt, 'udp'):
                    packet_data['src_port'] = int(getattr(pkt.udp, 'srcport', 0))
                    packet_data['dst_port'] = int(getattr(pkt.udp, 'dstport', 0))
                    packet_data['protocol'] = 'UDP'
                elif hasattr(pkt, 'icmp'):
                    packet_data['src_port'] = 0
                    packet_data['dst_port'] = 0
                    packet_data['protocol'] = 'ICMP'
            
            packet_data['packet_length'] = int(getattr(pkt, 'length', 0))
            packet_data['timestamp'] = datetime.now().isoformat()
            
            return packet_data if packet_data else None
            
        except Exception as e:
            self.logger.debug(f"Feature extraction failed: {e}")
            return None
    
    def _matches_filter(self, packet_data: Dict[str, Any], filter_str: str) -> bool:
        """Apply simple packet filter (basic BPF-like syntax)."""
        # Simple implementation - can be extended
        filter_lower = filter_str.lower()
        
        # Protocol filters
        if 'tcp' in filter_lower and packet_data.get('protocol') != 'TCP':
            return False
        if 'udp' in filter_lower and packet_data.get('protocol') != 'UDP':
            return False
        if 'icmp' in filter_lower and packet_data.get('protocol') != 'ICMP':
            return False
        
        # Port filters (e.g., "port 80")
        if 'port' in filter_lower:
            try:
                port_num = int(filter_lower.split('port')[1].strip())
                if packet_data.get('dst_port') != port_num and packet_data.get('src_port') != port_num:
                    return False
            except:
                pass
        
        return True
    
    def _process_packet(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process packet and detect anomaly."""
        try:
            # Create feature vector (simplified - matches training features)
            X = None
            if self.preprocessor and self.preprocessor.fitted:
                df = pd.DataFrame([packet_data])
                try:
                    X, _ = self.preprocessor.transform(df)
                except Exception:
                    # Fallback: create zero vector
                    feature_dim = getattr(self.model, 'n_features_in_', 42)
                    X = np.zeros((1, feature_dim), dtype=float)
            else:
                feature_dim = getattr(self.model, 'n_features_in_', 42)
                X = np.zeros((1, feature_dim), dtype=float)
            
            # Predict
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(X)
                if len(proba.shape) > 1 and proba.shape[1] > 1:
                    anomaly_score = float(proba[0, 1])
                else:
                    anomaly_score = float(proba[0])
                prediction = 1 if anomaly_score > self.threshold else 0
            else:
                pred = self.model.predict(X)[0]
                prediction = int(pred)
                anomaly_score = 1.0 if prediction == 1 else 0.0
            
            # Create result
            result = {
                'timestamp': datetime.now(),
                'is_anomaly': bool(prediction),
                'anomaly_score': float(anomaly_score),
                'packet_data': packet_data
            }
            
            # Handle anomaly
            if result['is_anomaly']:
                self.stats['anomalies_detected'] += 1
                self._handle_anomaly(result)
            
            # Log detection
            self._log_detection(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Packet processing failed: {e}")
            return {
                'timestamp': datetime.now(),
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'error': str(e)
            }
    
    def _handle_anomaly(self, result: Dict[str, Any]):
        """Handle detected anomaly."""
        score = result['anomaly_score']
        
        # Determine severity
        if score >= 0.9:
            severity = 'high'
        elif score >= 0.7:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Create alert
        alert_data = {
            'timestamp': result['timestamp'],
            'severity': severity,
            'anomaly_score': score,
            'description': f"Anomaly detected in PCAP with score {score:.4f}",
            'packet_data': result['packet_data']
        }
        
        if self.alert_manager:
            self.alert_manager.create_alert(alert_data)
            self.stats['alerts_generated'] += 1
    
    def _log_detection(self, result: Dict[str, Any]):
        """Log detection to database."""
        if not self.db_manager.enabled:
            return
        
        pkt = result.get('packet_data', {}) or {}
        record = {
            'timestamp': result.get('timestamp', datetime.utcnow()),
            'source_ip': pkt.get('src_ip'),
            'dest_ip': pkt.get('dst_ip'),
            'source_port': pkt.get('src_port'),
            'dest_port': pkt.get('dst_port'),
            'protocol': pkt.get('protocol'),
            'anomaly_score': result.get('anomaly_score', 0.0),
            'is_anomaly': result.get('is_anomaly', False),
            'severity': result.get('severity'),
            'raw_packet': str(pkt)[:1000]
        }
        self.db_manager.log_detection(record)
    
    def print_statistics(self):
        """Print analysis statistics."""
        print(f"\n{'='*60}")
        print("PCAP Analysis Statistics")
        print(f"{'='*60}")
        print(f"Total Packets Processed: {self.stats['total_packets']}")
        print(f"Anomalies Detected: {self.stats['anomalies_detected']}")
        print(f"Alerts Generated: {self.stats['alerts_generated']}")
        
        if self.stats['total_packets'] > 0:
            anomaly_rate = (self.stats['anomalies_detected'] / self.stats['total_packets']) * 100
            print(f"Anomaly Rate: {anomaly_rate:.2f}%")
        
        if self.stats['start_time'] and self.stats['end_time']:
            runtime = self.stats['end_time'] - self.stats['start_time']
            print(f"Runtime: {runtime}")
        
        print(f"{'='*60}\n")
    
    def close(self):
        """Cleanup resources."""
        if self.db_manager:
            self.db_manager.close()
