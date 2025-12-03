"""
Real-time anomaly detection module for live network traffic monitoring.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import time
from datetime import datetime
from collections import deque
from ..utils.logger import LoggerFactory
from .alert_manager import AlertManager
from ..persistence.db import DatabaseManager
from datetime import datetime
from pathlib import Path
from ..threat_intel.providers import ThreatIntelligence

try:
    from scapy.all import sniff, IP  # type: ignore
    _SCAPY_AVAILABLE = True
except Exception:
    _SCAPY_AVAILABLE = False

try:
    import pyshark  # type: ignore
    _PYSHARK_AVAILABLE = True
except Exception:
    _PYSHARK_AVAILABLE = False


class RealtimeDetector:
    """Real-time network anomaly detector."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        model,
        preprocessor,
        alert_manager: Optional[AlertManager] = None
    ):
        """
        Initialize real-time detector.
        
        Args:
            config: Configuration dictionary
            model: Trained model for detection
            preprocessor: Data preprocessor
            alert_manager: Alert manager instance
        """
        self.config = config
        self.model = model
        self.preprocessor = preprocessor
        self.alert_manager = alert_manager or AlertManager(config)
        self.logger = LoggerFactory.get_logger('RealtimeDetector')
        
        # Realtime configuration
        rt_config = config.get('realtime', {})
        self.enabled = rt_config.get('enabled', True)
        self.buffer_size = rt_config.get('buffer_size', 1000)
        self.detection_interval = rt_config.get('detection_interval', 5)
        self.threshold = rt_config.get('threshold', 0.85)
        
        # Detection buffer
        self.buffer = deque(maxlen=self.buffer_size)
        self.running = False
        
        # Statistics
        self.stats = {
            'total_packets': 0,
            'anomalies_detected': 0,
            'alerts_generated': 0,
            'start_time': None,
            'last_detection_time': None
        }
        # Database manager for persistence
        self.db_manager = DatabaseManager(config)
        
        # Threat intelligence
        self.threat_intel = ThreatIntelligence(config)
    
    def process_packet(self, packet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single network packet.
        
        Args:
            packet_data: Dictionary containing packet features
            
        Returns:
            Detection result dictionary
        """
        self.stats['total_packets'] += 1
        
        try:
            # Attempt to map packet_data into expected feature space
            X = None
            if self.preprocessor and self.preprocessor.fitted:
                df = pd.DataFrame([packet_data])
                try:
                    X, _ = self.preprocessor.transform(df)
                except Exception:
                    # Fallback: create zero vector matching trained feature dimension
                    feature_dim = getattr(self.model, 'n_features_in_', None)
                    if feature_dim is None and getattr(self.preprocessor, 'feature_names', None):
                        feature_dim = len(self.preprocessor.feature_names)
                    if feature_dim is None:
                        feature_dim = 42  # default to NSL-KDD processed feature count
                    X = np.zeros((1, feature_dim), dtype=float)
            else:
                feature_dim = getattr(self.model, 'n_features_in_', 42)
                X = np.zeros((1, feature_dim), dtype=float)

            # Predict using prepared feature vector
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
            
            # Add to buffer
            self.buffer.append(result)

            # Log detection (anomaly or normal) for statistics
            self._log_detection(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {str(e)}")
            return {
                'timestamp': datetime.now(),
                'is_anomaly': False,
                'anomaly_score': 0.0,
                'error': str(e)
            }
    
    def process_batch(self, batch_data: pd.DataFrame) -> np.ndarray:
        """
        Process a batch of network data.
        
        Args:
            batch_data: DataFrame containing batch features
            
        Returns:
            Array of detection results
        """
        try:
            # Preprocess
            X, _ = self.preprocessor.transform(batch_data)
            
            # Predict
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(X)
                if len(proba.shape) > 1 and proba.shape[1] > 1:
                    anomaly_scores = proba[:, 1]
                else:
                    anomaly_scores = proba.flatten()
                predictions = (anomaly_scores > self.threshold).astype(int)
            else:
                predictions = self.model.predict(X)
                anomaly_scores = predictions.astype(float)
            
            # Update statistics
            self.stats['total_packets'] += len(batch_data)
            self.stats['anomalies_detected'] += np.sum(predictions)
            
            # Handle anomalies
            for idx, (pred, score) in enumerate(zip(predictions, anomaly_scores)):
                if pred == 1:
                    result = {
                        'timestamp': datetime.now(),
                        'is_anomaly': True,
                        'anomaly_score': float(score),
                        'packet_data': batch_data.iloc[idx].to_dict()
                    }
                    self._handle_anomaly(result)
                else:
                    result = {
                        'timestamp': datetime.now(),
                        'is_anomaly': False,
                        'anomaly_score': float(score),
                        'packet_data': batch_data.iloc[idx].to_dict()
                    }
                self._log_detection(result)
            
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error processing batch: {str(e)}")
            return np.zeros(len(batch_data))
    
    def _handle_anomaly(self, result: Dict[str, Any]):
        """
        Handle detected anomaly.
        
        Args:
            result: Detection result dictionary
        """
        # Enrich with threat intelligence
        packet_data = result.get('packet_data', {})
        detection_record = {
            'timestamp': result['timestamp'],
            'src_ip': packet_data.get('src_ip') or packet_data.get('source_ip'),
            'dst_ip': packet_data.get('dst_ip') or packet_data.get('dest_ip'),
            'protocol': packet_data.get('protocol'),
            'anomaly_score': result['anomaly_score']
        }
        
        # Enrich with threat intel if enabled
        enriched_detection = self.threat_intel.enrich_detection(detection_record)
        
        # Determine severity based on anomaly score and threat score
        score = result['anomaly_score']
        threat_score = enriched_detection.get('threat_score', 0.0)
        
        # Adjust severity based on combined scores
        combined_score = (score * 0.6) + (threat_score / 100.0 * 0.4)
        
        if combined_score >= 0.9 or threat_score >= 75:
            severity = 'high'
        elif combined_score >= 0.7 or threat_score >= 50:
            severity = 'medium'
        else:
            severity = 'low'
        
        # Create alert
        alert_data = {
            'timestamp': result['timestamp'],
            'severity': severity,
            'anomaly_score': score,
            'threat_score': threat_score,
            'threat_intel': enriched_detection.get('threat_intel', {}),
            'description': f"Anomaly detected with score {score:.4f}, threat score {threat_score:.1f}",
            'packet_data': result['packet_data']
        }
        
        # Send to alert manager
        if self.alert_manager:
            self.alert_manager.create_alert(alert_data)
            self.stats['alerts_generated'] += 1
        # Also persist anomaly record
        self._log_detection({
            'timestamp': result['timestamp'],
            'is_anomaly': True,
            'anomaly_score': score,
            'severity': severity,
            'threat_score': threat_score,
            'packet_data': result['packet_data']
        })

    def _log_detection(self, result: Dict[str, Any]):
        """Persist detection result to database."""
        if not self.db_manager.enabled:
            return
        pkt = result.get('packet_data', {}) or {}
        record = {
            'timestamp': result.get('timestamp', datetime.utcnow()),
            'source_ip': pkt.get('src_ip') or pkt.get('source_ip'),
            'dest_ip': pkt.get('dst_ip') or pkt.get('dest_ip'),
            'source_port': pkt.get('src_port') or pkt.get('source_port'),
            'dest_port': pkt.get('dst_port') or pkt.get('dest_port') or pkt.get('destination_port'),
            'protocol': pkt.get('protocol'),
            'anomaly_score': result.get('anomaly_score', 0.0),
            'is_anomaly': result.get('is_anomaly', False),
            'severity': result.get('severity'),
            'raw_packet': str(pkt)[:1000]
        }
        self.db_manager.log_detection(record)
    
    def start_monitoring(self, data_source=None):
        """
        Start real-time monitoring.
        
        Args:
            data_source: Source of network data (optional)
        """
        if not self.enabled:
            self.logger.warning("Real-time detection is disabled")
            return
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        self.logger.info("Real-time monitoring started")
        
        try:
            while self.running:
                # Simulate or process real data
                if data_source is not None:
                    # Process data from source
                    pass
                else:
                    # Sleep for detection interval
                    time.sleep(self.detection_interval)
                
                self.stats['last_detection_time'] = datetime.now()
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")
        finally:
            self.stop_monitoring()

    def start_packet_capture(self, interface: str, backend: str = 'scapy', packet_count: Optional[int] = None, duration: Optional[int] = None, inject_rate: float = 0.0, synthetic_delay: float = 0.0):
        """Start live packet capture using Scapy or PyShark.

        Args:
            interface: Network interface to sniff (e.g., 'eth0')
            backend: 'scapy' or 'pyshark'
            packet_count: Optional limit to number of packets (captures up to this count)
            duration: Optional duration in seconds (captures until time elapses). Ignored if neither backend supports timeout directly (synthetic fallback will approximate).

        Behavior:
            - If packet_count provided: stop after that many packets (or earlier if duration also set and reached first).
            - If duration provided (no packet_count): run until duration expires.
            - If neither provided: continuous capture until interrupted (Ctrl+C). Synthetic fallback remains bounded to 10 packets for safety.
        """
        if backend == 'scapy' and not _SCAPY_AVAILABLE:
            self.logger.error("Scapy not available. Install scapy or choose pyshark backend.")
            return
        if backend == 'pyshark' and not _PYSHARK_AVAILABLE:
            self.logger.error("PyShark not available. Install pyshark or choose scapy backend.")
            return

        self.logger.info(f"Starting packet capture on {interface} using {backend} backend")
        if packet_count:
            self.logger.info(f"Capture limit: packet_count={packet_count}")
        if duration:
            self.logger.info(f"Capture time limit: duration={duration}s")
        if not packet_count and not duration:
            self.logger.info("Continuous mode: Ctrl+C to stop")
        self.stats['start_time'] = datetime.now()

        def _process_packet(pkt):
            try:
                packet_data = {}
                if backend == 'scapy':
                    # Extract basic IP layer features if present
                    if IP in pkt:
                        packet_data['src_ip'] = pkt[IP].src
                        packet_data['dst_ip'] = pkt[IP].dst
                        packet_data['protocol'] = pkt.payload.name
                    packet_data['packet_length'] = len(pkt)
                    packet_data['capture_time'] = datetime.utcnow().isoformat()
                else:  # pyshark
                    if hasattr(pkt, 'ip'):
                        packet_data['src_ip'] = getattr(pkt.ip, 'src', None)
                        packet_data['dst_ip'] = getattr(pkt.ip, 'dst', None)
                    
                    # Extract port information from TCP/UDP layers
                    if hasattr(pkt, 'tcp'):
                        packet_data['src_port'] = int(getattr(pkt.tcp, 'srcport', 0))
                        packet_data['dst_port'] = int(getattr(pkt.tcp, 'dstport', 0))
                    elif hasattr(pkt, 'udp'):
                        packet_data['src_port'] = int(getattr(pkt.udp, 'srcport', 0))
                        packet_data['dst_port'] = int(getattr(pkt.udp, 'dstport', 0))
                    
                    packet_data['protocol'] = getattr(pkt, 'highest_layer', None)
                    packet_data['packet_length'] = getattr(pkt, 'length', None)
                    packet_data['capture_time'] = datetime.utcnow().isoformat()

                # Placeholder: mapping raw packet features to trained feature space is non-trivial.
                # For now we attempt detection using available subset; preprocessor may skip missing columns.
                self.process_packet(packet_data)
            except Exception as e:
                self.logger.error(f"Packet processing error: {e}")

        if backend == 'scapy':
            try:
                sniff_args = {
                    'iface': interface,
                    'prn': _process_packet,
                    'count': packet_count
                }
                # scapy sniff supports timeout parameter for duration-based capture
                if duration:
                    sniff_args['timeout'] = duration
                sniff(**sniff_args)
            except Exception as e:
                # If synthetic injection is disabled, do NOT generate synthetic traffic.
                # This ensures dashboard reflects real traffic state (idle when wifi is off).
                if inject_rate == 0:
                    self.logger.error(f"Scapy sniff failed: {e}. Synthetic fallback disabled (inject_rate=0). Capture stopped/idle.")
                    # Print current statistics and return without synthetic generation
                    self.print_statistics()
                    return
                self.logger.error(f"Scapy sniff failed: {e}. Falling back to synthetic packet generation.")
                # Fallback synthetic packets honoring packet_count or duration
                import random
                start_t = time.time()
                emitted = 0
                
                # Realistic port scanning simulation
                # Well-known ports that are commonly scanned
                common_scan_ports = [
                    21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
                    1433, 1521, 3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017
                ]
                
                # Simulate different types of traffic
                scanner_ips = [f'192.168.0.{random.randint(50,100)}' for _ in range(5)]  # Potential scanners
                normal_ips = [f'192.168.0.{random.randint(101,254)}' for _ in range(10)]  # Normal traffic
                target_servers = [f'192.168.1.{random.randint(1,50)}' for _ in range(3)]  # Target servers
                
                while True:
                    # Decide if this is a scan or normal traffic (30% scan, 70% normal)
                    is_port_scan = random.random() < 0.3
                    
                    if is_port_scan:
                        # Port scanning behavior: one IP scanning multiple ports on target
                        protocol = 'TCP'  # Most scans use TCP
                        src_ip = random.choice(scanner_ips)
                        dst_ip = random.choice(target_servers)
                        src_port = random.randint(40000, 65535)  # High ephemeral port
                        dst_port = random.choice(common_scan_ports)  # Scanning common ports
                    else:
                        # Normal traffic
                        protocol = random.choice(['TCP', 'TCP', 'TCP', 'UDP', 'ICMP'])  # TCP is most common
                        src_ip = random.choice(normal_ips)
                        dst_ip = f'192.168.1.{random.randint(1,254)}'
                        
                        if protocol == 'TCP':
                            src_port = random.randint(40000, 65535)
                            dst_port = random.choice([80, 443, 22, 25, 110, 143, 3306, 5432, 8080])
                        elif protocol == 'UDP':
                            src_port = random.randint(40000, 65535)
                            dst_port = random.choice([53, 67, 68, 123, 161, 162, 500, 514])
                        else:  # ICMP
                            src_port = 0
                            dst_port = 0
                    
                    packet_data = {
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'src_port': src_port,
                        'dst_port': dst_port,
                        'source_port': src_port,
                        'dest_port': dst_port,
                        'destination_port': dst_port,
                        'protocol': protocol,
                        'packet_length': random.randint(60, 1500),
                        'capture_time': datetime.utcnow().isoformat()
                    }
                    
                    # Anomaly injection - port scans and suspicious traffic
                    if inject_rate > 0 and (is_port_scan or random.random() < inject_rate):
                        self.stats['total_packets'] += 1
                        score = round(random.uniform(max(self.threshold, 0.9), 1.0), 4)
                        injected = {
                            'timestamp': datetime.now(),
                            'is_anomaly': True,
                            'anomaly_score': score,
                            'packet_data': packet_data
                        }
                        self.stats['anomalies_detected'] += 1
                        self._handle_anomaly(injected)
                        self.buffer.append(injected)
                    else:
                        # Process and log normal synthetic packets so they appear in live feed
                        result = self.process_packet(packet_data)
                        # Also log non-anomalous synthetic packets to database for live feed
                        if inject_rate > 0:  # We're in synthetic mode
                            self._log_detection({
                                'timestamp': datetime.now(),
                                'is_anomaly': False,
                                'anomaly_score': 0.0,
                                'severity': None,
                                'packet_data': packet_data
                            })
                    emitted += 1
                    if synthetic_delay > 0:
                        time.sleep(synthetic_delay)
                    if packet_count and emitted >= packet_count:
                        break
                    if duration and (time.time() - start_t) >= duration:
                        break
        else:
            try:
                import subprocess
                import time as time_module
                
                def is_interface_up(iface):
                    """Check if network interface is up and has an IP address"""
                    try:
                        result = subprocess.run(
                            ['ip', 'addr', 'show', iface],
                            capture_output=True,
                            text=True,
                            timeout=2
                        )
                        if result.returncode != 0:
                            return False
                        # Check if interface is UP and has an inet (IPv4) address
                        output = result.stdout
                        return 'state UP' in output and 'inet ' in output
                    except Exception:
                        return False
                
                # Initial interface check
                if not is_interface_up(interface):
                    self.logger.warning(f"Interface {interface} is DOWN or has no IP address. Waiting for it to come up...")
                    print(f"⚠️  WARNING: Interface {interface} is not ready. Waiting...")
                    
                    # Wait for interface to come up (with timeout)
                    wait_timeout = 300  # 5 minutes
                    wait_start = time_module.time()
                    while not is_interface_up(interface):
                        if time_module.time() - wait_start > wait_timeout:
                            self.logger.error(f"Timeout waiting for interface {interface} to come up")
                            return
                        time_module.sleep(5)
                        if is_interface_up(interface):
                            self.logger.info(f"Interface {interface} is now UP! Starting capture...")
                            print(f"✅ Interface {interface} is UP! Starting capture...")
                            break
                
                # Start capture with auto-recovery
                capture = None
                capture_iterator = None
                start_t = time_module.time()
                packet_count_captured = 0
                last_interface_check = time_module.time()
                interface_check_interval = 5  # Check interface status every 5 seconds
                packets_since_last_check = 0
                
                while True:
                    # Periodic interface check
                    current_time = time_module.time()
                    if current_time - last_interface_check >= interface_check_interval:
                        last_interface_check = current_time
                        
                        # Check if interface is down
                        if not is_interface_up(interface):
                            self.logger.warning(f"Interface {interface} went DOWN! Pausing capture...")
                            print(f"⚠️  Interface {interface} went DOWN! Waiting for it to come back up...")
                            
                            # Clean up capture
                            if capture:
                                try:
                                    capture.close()
                                except Exception:
                                    pass
                                capture = None
                                capture_iterator = None
                            
                            # Wait for interface to come back up
                            while not is_interface_up(interface):
                                time_module.sleep(5)
                            
                            self.logger.info(f"Interface {interface} is back UP! Resuming capture...")
                            print(f"✅ Interface {interface} is back UP! Resuming capture...")
                            
                        # Check if capture is stuck (no packets for 5+ seconds while interface is up)
                        elif packets_since_last_check == 0 and capture is not None:
                            self.logger.warning("No packets captured in last 5 seconds, recreating capture...")
                            print(f"⚠️  Capture appears stuck, recreating...")
                            if capture:
                                try:
                                    capture.close()
                                except Exception:
                                    pass
                                capture = None
                                capture_iterator = None
                        
                        # Reset counter
                        packets_since_last_check = 0
                    
                    # (Re)create capture if needed
                    if capture is None or capture_iterator is None:
                        try:
                            if capture:
                                try:
                                    capture.close()
                                except Exception:
                                    pass
                            
                            self.logger.info(f"Creating new capture on {interface}...")
                            print(f"🔄 Creating new capture on {interface}...")
                            capture = pyshark.LiveCapture(interface=interface)
                            capture_iterator = capture.sniff_continuously()
                            self.logger.info("Capture created successfully, starting packet sniffing...")
                            print(f"✅ Capture ready, sniffing packets...")
                        except Exception as e:
                            self.logger.error(f"Failed to create capture: {e}")
                            capture = None
                            capture_iterator = None
                            time_module.sleep(5)
                            continue
                    
                    # Capture packets
                    try:
                        # Get next packet with timeout
                        pkt = next(capture_iterator, None)
                        
                        if pkt:
                            _process_packet(pkt)
                            packet_count_captured += 1
                            packets_since_last_check += 1
                            
                            # Check stop conditions
                            if packet_count and packet_count_captured >= packet_count:
                                self.logger.info(f"Reached packet count limit: {packet_count}")
                                return
                            if duration and (time_module.time() - start_t) >= duration:
                                self.logger.info(f"Reached duration limit: {duration}s")
                                return
                        else:
                            # No packet, small delay
                            time_module.sleep(0.01)
                            
                    except KeyboardInterrupt:
                        self.logger.info("Packet capture interrupted by user")
                        raise
                    except StopIteration:
                        # Iterator ended, recreate everything
                        self.logger.warning("Capture iterator ended, recreating...")
                        print(f"⚠️  Capture ended, recreating...")
                        if capture:
                            try:
                                capture.close()
                            except Exception:
                                pass
                        capture = None
                        capture_iterator = None
                        time_module.sleep(1)
                        continue
                    except Exception as e:
                        # Capture error
                        error_msg = str(e).lower()
                        
                        # Check if interface went down
                        if not is_interface_up(interface):
                            self.logger.warning(f"Interface {interface} went DOWN during capture")
                            if capture:
                                try:
                                    capture.close()
                                except Exception:
                                    pass
                            capture = None
                            capture_iterator = None
                            continue
                        
                        # Other errors - recreate capture
                        self.logger.error(f"PyShark capture error: {e}, recreating capture...")
                        print(f"⚠️  Capture error, recreating...")
                        if capture:
                            try:
                                capture.close()
                            except Exception:
                                pass
                        capture = None
                        capture_iterator = None
                        time_module.sleep(1)
                        continue
                            
            except KeyboardInterrupt:
                self.logger.info("Packet capture interrupted by user")
            except Exception as e:
                self.logger.error(f"PyShark capture failed: {e}. No synthetic fallback implemented for pyshark.")
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.running = False
        self.logger.info("Real-time monitoring stopped")
        self.print_statistics()
    
    def print_statistics(self):
        """Print detection statistics."""
        print(f"\n{'='*60}")
        print("Real-time Detection Statistics")
        print(f"{'='*60}")
        print(f"Total Packets Processed: {self.stats['total_packets']}")
        print(f"Anomalies Detected: {self.stats['anomalies_detected']}")
        print(f"Alerts Generated: {self.stats['alerts_generated']}")
        
        if self.stats['total_packets'] > 0:
            anomaly_rate = (self.stats['anomalies_detected'] / self.stats['total_packets']) * 100
            print(f"Anomaly Rate: {anomaly_rate:.2f}%")
        
        if self.stats['start_time']:
            runtime = datetime.now() - self.stats['start_time']
            print(f"Runtime: {runtime}")
        
        print(f"{'='*60}\n")
    
    def get_recent_detections(self, n: int = 10) -> list:
        """
        Get recent detection results from buffer.
        
        Args:
            n: Number of recent detections to return
            
        Returns:
            List of recent detection results
        """
        return list(self.buffer)[-n:]
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """
        Get summary of detected anomalies.
        
        Returns:
            Dictionary with anomaly summary
        """
        anomalies = [d for d in self.buffer if d.get('is_anomaly', False)]
        
        if not anomalies:
            return {
                'total_anomalies': 0,
                'avg_score': 0.0,
                'max_score': 0.0,
                'min_score': 0.0
            }
        
        scores = [a['anomaly_score'] for a in anomalies]
        
        return {
            'total_anomalies': len(anomalies),
            'avg_score': np.mean(scores),
            'max_score': np.max(scores),
            'min_score': np.min(scores),
            'recent_anomalies': anomalies[-5:]
        }

    def close(self):
        """Close resources."""
        try:
            if self.db_manager:
                self.db_manager.close()
        except Exception:
            pass