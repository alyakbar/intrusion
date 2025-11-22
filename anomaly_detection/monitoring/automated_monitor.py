"""
Automated monitoring system for continuous performance tracking.
"""

import time
from typing import Dict, Any
from datetime import datetime
import psutil
import numpy as np
from ..utils.logger import LoggerFactory


class AutomatedMonitor:
    """Automated monitoring system for model and system performance."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize automated monitor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = LoggerFactory.get_logger('AutomatedMonitor')
        
        # Monitoring configuration
        mon_config = config.get('monitoring', {})
        self.enabled = mon_config.get('enabled', True)
        self.metrics_interval = mon_config.get('metrics_interval', 300)
        self.performance_tracking = mon_config.get('performance_tracking', True)
        
        # Metrics storage
        self.system_metrics = []
        self.model_metrics = []
        self.running = False
    
    def start_monitoring(self):
        """Start automated monitoring."""
        if not self.enabled:
            self.logger.warning("Monitoring is disabled")
            return
        
        self.running = True
        self.logger.info("Automated monitoring started")
        
        try:
            while self.running:
                # Collect metrics
                self._collect_system_metrics()
                
                # Sleep for interval
                time.sleep(self.metrics_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring interrupted by user")
        finally:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop automated monitoring."""
        self.running = False
        self.logger.info("Automated monitoring stopped")
        self.print_summary()
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            metrics = {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent
            }
            
            # Add GPU metrics if available
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    metrics['gpu_utilization'] = gpus[0].load * 100
                    metrics['gpu_memory'] = gpus[0].memoryUtil * 100
            except:
                pass
            
            self.system_metrics.append(metrics)
            
            # Log if thresholds exceeded
            if metrics['cpu_percent'] > 80:
                self.logger.warning(f"High CPU usage: {metrics['cpu_percent']:.1f}%")
            if metrics['memory_percent'] > 80:
                self.logger.warning(f"High memory usage: {metrics['memory_percent']:.1f}%")
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {str(e)}")
    
    def track_model_performance(
        self,
        model_name: str,
        metrics: Dict[str, float]
    ):
        """
        Track model performance metrics.
        
        Args:
            model_name: Name of the model
            metrics: Dictionary of performance metrics
        """
        if not self.performance_tracking:
            return
        
        metric_entry = {
            'timestamp': datetime.now(),
            'model_name': model_name,
            **metrics
        }
        
        self.model_metrics.append(metric_entry)
        self.logger.info(f"Tracked performance for {model_name}")
    
    def track_detection_latency(self, latency_ms: float):
        """
        Track detection latency.
        
        Args:
            latency_ms: Latency in milliseconds
        """
        if hasattr(self, 'latency_history'):
            self.latency_history.append(latency_ms)
        else:
            self.latency_history = [latency_ms]
        
        # Log if latency is high
        if latency_ms > 1000:  # More than 1 second
            self.logger.warning(f"High detection latency: {latency_ms:.2f}ms")
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get current system health status.
        
        Returns:
            Dictionary with system health metrics
        """
        if not self.system_metrics:
            return {
                'status': 'no_data',
                'message': 'No monitoring data available'
            }
        
        latest = self.system_metrics[-1]
        
        # Determine health status
        cpu_ok = latest['cpu_percent'] < 80
        mem_ok = latest['memory_percent'] < 80
        
        if cpu_ok and mem_ok:
            status = 'healthy'
        elif cpu_ok or mem_ok:
            status = 'warning'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'timestamp': latest['timestamp'],
            'cpu_percent': latest['cpu_percent'],
            'memory_percent': latest['memory_percent'],
            'disk_usage': latest['disk_usage']
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get summary of model performance over time.
        
        Returns:
            Dictionary with performance summary
        """
        if not self.model_metrics:
            return {'message': 'No performance data available'}
        
        # Calculate average metrics per model
        model_summaries = {}
        
        for entry in self.model_metrics:
            model_name = entry['model_name']
            if model_name not in model_summaries:
                model_summaries[model_name] = []
            model_summaries[model_name].append(entry)
        
        summary = {}
        for model_name, entries in model_summaries.items():
            # Calculate averages
            metrics = {}
            for key in entries[0].keys():
                if key not in ['timestamp', 'model_name']:
                    values = [e[key] for e in entries if isinstance(e.get(key), (int, float))]
                    if values:
                        metrics[f'avg_{key}'] = np.mean(values)
                        metrics[f'std_{key}'] = np.std(values)
            
            summary[model_name] = metrics
        
        return summary
    
    def print_summary(self):
        """Print monitoring summary."""
        print(f"\n{'='*60}")
        print("Monitoring Summary")
        print(f"{'='*60}")
        
        # System metrics summary
        if self.system_metrics:
            cpu_values = [m['cpu_percent'] for m in self.system_metrics]
            mem_values = [m['memory_percent'] for m in self.system_metrics]
            
            print("\nSystem Metrics:")
            print(f"  Avg CPU Usage: {np.mean(cpu_values):.2f}%")
            print(f"  Max CPU Usage: {np.max(cpu_values):.2f}%")
            print(f"  Avg Memory Usage: {np.mean(mem_values):.2f}%")
            print(f"  Max Memory Usage: {np.max(mem_values):.2f}%")
        
        # Model performance summary
        if self.model_metrics:
            print(f"\nModel Performance:")
            print(f"  Total Tracking Entries: {len(self.model_metrics)}")
            
            perf_summary = self.get_performance_summary()
            for model_name, metrics in perf_summary.items():
                print(f"\n  {model_name}:")
                for metric, value in metrics.items():
                    print(f"    {metric}: {value:.4f}")
        
        # Latency summary
        if hasattr(self, 'latency_history') and self.latency_history:
            print(f"\nDetection Latency:")
            print(f"  Avg: {np.mean(self.latency_history):.2f}ms")
            print(f"  Max: {np.max(self.latency_history):.2f}ms")
            print(f"  Min: {np.min(self.latency_history):.2f}ms")
        
        print(f"{'='*60}\n")
    
    def export_metrics(self, filepath: str):
        """
        Export metrics to file.
        
        Args:
            filepath: Path to export file
        """
        import json
        
        export_data = {
            'system_metrics': [
                {k: str(v) if isinstance(v, datetime) else v 
                 for k, v in m.items()}
                for m in self.system_metrics
            ],
            'model_metrics': [
                {k: str(v) if isinstance(v, datetime) else v 
                 for k, v in m.items()}
                for m in self.model_metrics
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Metrics exported to {filepath}")