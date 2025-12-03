"""
Multi-interface network monitoring module.
Supports simultaneous monitoring of multiple network interfaces.
"""

import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from ..utils.logger import LoggerFactory
from ..persistence.db import DatabaseManager
from .realtime_detector import RealtimeDetector


class MultiInterfaceMonitor:
    """Monitor multiple network interfaces simultaneously."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        model,
        preprocessor,
        interfaces: List[str],
        backend: str = 'scapy'
    ):
        """
        Initialize multi-interface monitor.
        
        Args:
            config: Configuration dictionary
            model: Trained detection model
            preprocessor: Data preprocessor
            interfaces: List of network interfaces to monitor
            backend: Capture backend ('scapy' or 'pyshark')
        """
        self.config = config
        self.model = model
        self.preprocessor = preprocessor
        self.interfaces = interfaces
        self.backend = backend
        self.logger = LoggerFactory.get_logger('MultiInterfaceMonitor')
        self.db_manager = DatabaseManager(config)
        
        # Detector threads
        self.detectors = {}
        self.threads = {}
        self.running = False
        
        # Aggregated statistics
        self.aggregate_stats = {
            'total_packets': 0,
            'anomalies_detected': 0,
            'alerts_generated': 0,
            'interfaces': {},
            'start_time': None
        }
    
    def start_monitoring(
        self,
        packet_count: Optional[int] = None,
        duration: Optional[int] = None,
        inject_rate: float = 0.0,
        synthetic_delay: float = 0.0
    ):
        """
        Start monitoring all interfaces.
        
        Args:
            packet_count: Optional packet limit per interface
            duration: Optional duration in seconds
            inject_rate: Synthetic injection rate (for testing)
            synthetic_delay: Delay between synthetic packets
        """
        self.logger.info(f"Starting multi-interface monitoring on: {', '.join(self.interfaces)}")
        self.running = True
        self.aggregate_stats['start_time'] = datetime.now()
        
        for interface in self.interfaces:
            try:
                # Create detector for this interface
                detector = RealtimeDetector(
                    config=self.config,
                    model=self.model,
                    preprocessor=self.preprocessor
                )
                
                # Initialize interface stats
                self.aggregate_stats['interfaces'][interface] = {
                    'packets': 0,
                    'anomalies': 0,
                    'status': 'starting'
                }
                
                # Start detector in separate thread
                thread = threading.Thread(
                    target=self._monitor_interface,
                    args=(interface, detector, packet_count, duration, inject_rate, synthetic_delay),
                    name=f"Monitor-{interface}",
                    daemon=True
                )
                
                self.detectors[interface] = detector
                self.threads[interface] = thread
                thread.start()
                
                self.logger.info(f"Started monitoring on interface: {interface}")
                
            except Exception as e:
                self.logger.error(f"Failed to start monitoring on {interface}: {e}")
                self.aggregate_stats['interfaces'][interface]['status'] = 'error'
        
        # Wait for all threads (or until interrupted)
        try:
            for interface, thread in self.threads.items():
                thread.join()
        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")
            self.stop_monitoring()
    
    def _monitor_interface(
        self,
        interface: str,
        detector: RealtimeDetector,
        packet_count: Optional[int],
        duration: Optional[int],
        inject_rate: float,
        synthetic_delay: float
    ):
        """
        Monitor a single interface (runs in separate thread).
        
        Args:
            interface: Network interface name
            detector: RealtimeDetector instance
            packet_count: Optional packet limit
            duration: Optional duration
            inject_rate: Synthetic injection rate
            synthetic_delay: Synthetic packet delay
        """
        try:
            self.aggregate_stats['interfaces'][interface]['status'] = 'active'
            
            # Start capture
            detector.start_packet_capture(
                interface=interface,
                backend=self.backend,
                packet_count=packet_count,
                duration=duration,
                inject_rate=inject_rate,
                synthetic_delay=synthetic_delay
            )
            
            # Update aggregate stats
            self.aggregate_stats['interfaces'][interface]['packets'] = detector.stats['total_packets']
            self.aggregate_stats['interfaces'][interface]['anomalies'] = detector.stats['anomalies_detected']
            self.aggregate_stats['interfaces'][interface]['status'] = 'completed'
            
            self.aggregate_stats['total_packets'] += detector.stats['total_packets']
            self.aggregate_stats['anomalies_detected'] += detector.stats['anomalies_detected']
            self.aggregate_stats['alerts_generated'] += detector.stats['alerts_generated']
            
        except Exception as e:
            self.logger.error(f"Error monitoring interface {interface}: {e}")
            self.aggregate_stats['interfaces'][interface]['status'] = 'error'
        finally:
            detector.close()
    
    def stop_monitoring(self):
        """Stop monitoring all interfaces."""
        self.logger.info("Stopping multi-interface monitoring...")
        self.running = False
        
        # Close all detectors
        for interface, detector in self.detectors.items():
            try:
                detector.running = False
                detector.close()
            except Exception as e:
                self.logger.error(f"Error stopping detector for {interface}: {e}")
        
        self.print_aggregate_statistics()
    
    def print_aggregate_statistics(self):
        """Print aggregated statistics from all interfaces."""
        print(f"\n{'='*70}")
        print("Multi-Interface Monitoring Statistics")
        print(f"{'='*70}")
        print(f"Total Packets Processed: {self.aggregate_stats['total_packets']}")
        print(f"Total Anomalies Detected: {self.aggregate_stats['anomalies_detected']}")
        print(f"Total Alerts Generated: {self.aggregate_stats['alerts_generated']}")
        
        if self.aggregate_stats['total_packets'] > 0:
            rate = (self.aggregate_stats['anomalies_detected'] / self.aggregate_stats['total_packets']) * 100
            print(f"Overall Anomaly Rate: {rate:.2f}%")
        
        if self.aggregate_stats['start_time']:
            runtime = datetime.now() - self.aggregate_stats['start_time']
            print(f"Runtime: {runtime}")
        
        print(f"\n{'-'*70}")
        print("Per-Interface Statistics:")
        print(f"{'-'*70}")
        
        for interface, stats in self.aggregate_stats['interfaces'].items():
            print(f"\n  Interface: {interface}")
            print(f"    Status: {stats['status']}")
            print(f"    Packets: {stats['packets']}")
            print(f"    Anomalies: {stats['anomalies']}")
            if stats['packets'] > 0:
                iface_rate = (stats['anomalies'] / stats['packets']) * 100
                print(f"    Anomaly Rate: {iface_rate:.2f}%")
        
        print(f"\n{'='*70}\n")
    
    def get_interface_statistics(self, interface: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific interface.
        
        Args:
            interface: Network interface name
            
        Returns:
            Statistics dictionary or None if interface not found
        """
        return self.aggregate_stats['interfaces'].get(interface)
    
    def get_aggregate_statistics(self) -> Dict[str, Any]:
        """Get aggregated statistics from all interfaces."""
        return self.aggregate_stats.copy()
