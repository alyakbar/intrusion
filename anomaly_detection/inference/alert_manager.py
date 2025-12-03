"""
Alert management system for handling and notifying anomaly detections.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import deque
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from ..utils.logger import LoggerFactory, log_detection_event


class AlertManager:
    """Manager for creating and handling security alerts."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = LoggerFactory.get_logger('AlertManager')
        
        # Alert configuration
        alert_config = config.get('alerts', {})
        self.enabled = alert_config.get('enabled', True)
        self.severity_levels = alert_config.get('severity_levels', {
            'high': 0.9,
            'medium': 0.7,
            'low': 0.5
        })
        self.notification_methods = alert_config.get('notification_methods', ['console', 'log'])
        self.alert_cooldown = alert_config.get('alert_cooldown', 60)
        
        # Alert storage
        self.alerts = deque(maxlen=1000)
        self.alert_history = []
        self.last_alert_time = {}
        
        # Statistics
        self.stats = {
            'total_alerts': 0,
            'high_severity': 0,
            'medium_severity': 0,
            'low_severity': 0
        }
    
    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new alert.
        
        Args:
            alert_data: Dictionary containing alert information
            
        Returns:
            Complete alert dictionary
        """
        if not self.enabled:
            return None
        
        # Check cooldown
        alert_type = alert_data.get('description', 'unknown')
        if self._is_in_cooldown(alert_type):
            return None
        
        # Create alert object
        alert = {
            'id': self._generate_alert_id(),
            'timestamp': alert_data.get('timestamp', datetime.now()),
            'severity': alert_data.get('severity', 'low'),
            'anomaly_score': alert_data.get('anomaly_score', 0.0),
            'description': alert_data.get('description', 'Anomaly detected'),
            'packet_data': alert_data.get('packet_data', {}),
            'status': 'active'
        }
        
        # Store alert
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Update statistics
        self.stats['total_alerts'] += 1
        severity_key = f"{alert['severity']}_severity"
        if severity_key in self.stats:
            self.stats[severity_key] += 1
        
        # Update cooldown
        self.last_alert_time[alert_type] = datetime.now()
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        return f"ALERT-{timestamp}"
    
    def _is_in_cooldown(self, alert_type: str) -> bool:
        """
        Check if alert type is in cooldown period.
        
        Args:
            alert_type: Type/description of alert
            
        Returns:
            True if in cooldown, False otherwise
        """
        if alert_type not in self.last_alert_time:
            return False
        
        time_since_last = datetime.now() - self.last_alert_time[alert_type]
        return time_since_last.total_seconds() < self.alert_cooldown
    
    def _send_notifications(self, alert: Dict[str, Any]):
        """
        Send notifications through configured methods.
        
        Args:
            alert: Alert dictionary
        """
        for method in self.notification_methods:
            try:
                if method == 'console':
                    self._notify_console(alert)
                elif method == 'log':
                    self._notify_log(alert)
                elif method == 'email':
                    self._notify_email(alert)
                elif method == 'webhook':
                    self._notify_webhook(alert)
            except Exception as e:
                self.logger.error(f"Error sending notification via {method}: {str(e)}")
    
    def _notify_console(self, alert: Dict[str, Any]):
        """Print alert to console."""
        severity_symbol = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(alert['severity'], '⚪')
        
        print(f"\n{severity_symbol} ALERT [{alert['severity'].upper()}] {severity_symbol}")
        print(f"ID: {alert['id']}")
        print(f"Time: {alert['timestamp']}")
        print(f"Score: {alert['anomaly_score']:.4f}")
        print(f"Description: {alert['description']}")
        print("-" * 60)
    
    def _notify_log(self, alert: Dict[str, Any]):
        """Log alert to file."""
        event_data = {
            'severity': alert['severity'],
            'anomaly_score': alert['anomaly_score'],
            'description': alert['description']
        }
        log_detection_event(self.logger, event_data)
    
    def _notify_email(self, alert: Dict[str, Any]):
        """
        Send email notification via SMTP.
        
        Args:
            alert: Alert dictionary
        """
        email_config = self.config.get('alerts', {}).get('email', {})
        
        if not email_config.get('enabled', False):
            return
        
        try:
            # Email configuration
            smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = email_config.get('smtp_port', 587)
            sender_email = email_config.get('sender_email')
            sender_password = email_config.get('sender_password')
            recipients = email_config.get('recipients', [])
            
            if not sender_email or not sender_password or not recipients:
                self.logger.warning("Email configuration incomplete. Skipping email notification.")
                return
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 Security Alert: {alert['severity'].upper()} Severity"
            msg['From'] = sender_email
            msg['To'] = ', '.join(recipients)
            
            # Email body
            html_body = f"""
            <html>
                <body>
                    <h2 style="color: {'#dc2626' if alert['severity'] == 'high' else '#f59e0b' if alert['severity'] == 'medium' else '#10b981'};">
                        Network Anomaly Alert
                    </h2>
                    <p><strong>Alert ID:</strong> {alert['id']}</p>
                    <p><strong>Timestamp:</strong> {alert['timestamp']}</p>
                    <p><strong>Severity:</strong> {alert['severity'].upper()}</p>
                    <p><strong>Anomaly Score:</strong> {alert['anomaly_score']:.4f}</p>
                    <p><strong>Description:</strong> {alert['description']}</p>
                    
                    <h3>Packet Details:</h3>
                    <ul>
                        <li><strong>Source IP:</strong> {alert['packet_data'].get('src_ip', 'N/A')}</li>
                        <li><strong>Destination IP:</strong> {alert['packet_data'].get('dst_ip', 'N/A')}</li>
                        <li><strong>Source Port:</strong> {alert['packet_data'].get('src_port', 'N/A')}</li>
                        <li><strong>Destination Port:</strong> {alert['packet_data'].get('dst_port', 'N/A')}</li>
                        <li><strong>Protocol:</strong> {alert['packet_data'].get('protocol', 'N/A')}</li>
                    </ul>
                    
                    <p style="color: #6b7280; font-size: 0.875rem;">
                        This is an automated alert from the Network Anomaly Detection System.
                    </p>
                </body>
            </html>
            """
            
            text_body = f"""
            Network Anomaly Alert
            
            Alert ID: {alert['id']}
            Timestamp: {alert['timestamp']}
            Severity: {alert['severity'].upper()}
            Anomaly Score: {alert['anomaly_score']:.4f}
            Description: {alert['description']}
            
            Packet Details:
            - Source IP: {alert['packet_data'].get('src_ip', 'N/A')}
            - Destination IP: {alert['packet_data'].get('dst_ip', 'N/A')}
            - Source Port: {alert['packet_data'].get('src_port', 'N/A')}
            - Destination Port: {alert['packet_data'].get('dst_port', 'N/A')}
            - Protocol: {alert['packet_data'].get('protocol', 'N/A')}
            
            This is an automated alert from the Network Anomaly Detection System.
            """
            
            # Attach both plain text and HTML
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())
            
            self.logger.info(f"Email notification sent for alert {alert['id']}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
    
    def _notify_webhook(self, alert: Dict[str, Any]):
        """
        Send webhook notification via HTTP POST.
        
        Args:
            alert: Alert dictionary
        """
        webhook_config = self.config.get('alerts', {}).get('webhook', {})
        
        if not webhook_config.get('enabled', False):
            return
        
        try:
            url = webhook_config.get('url')
            headers = webhook_config.get('headers', {'Content-Type': 'application/json'})
            timeout = webhook_config.get('timeout', 10)
            
            if not url:
                self.logger.warning("Webhook URL not configured. Skipping webhook notification.")
                return
            
            # Prepare payload
            payload = {
                'alert_id': alert['id'],
                'timestamp': alert['timestamp'].isoformat() if isinstance(alert['timestamp'], datetime) else str(alert['timestamp']),
                'severity': alert['severity'],
                'anomaly_score': alert['anomaly_score'],
                'description': alert['description'],
                'packet_data': {
                    'source_ip': alert['packet_data'].get('src_ip'),
                    'destination_ip': alert['packet_data'].get('dst_ip'),
                    'source_port': alert['packet_data'].get('src_port'),
                    'destination_port': alert['packet_data'].get('dst_port'),
                    'protocol': alert['packet_data'].get('protocol')
                },
                'status': alert['status']
            }
            
            # Send POST request
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                self.logger.info(f"Webhook notification sent for alert {alert['id']}")
            else:
                self.logger.warning(f"Webhook returned status {response.status_code} for alert {alert['id']}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to send webhook notification: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Get all active alerts.
        
        Returns:
            List of active alerts
        """
        return [a for a in self.alerts if a['status'] == 'active']
    
    def get_alerts_by_severity(self, severity: str) -> List[Dict[str, Any]]:
        """
        Get alerts by severity level.
        
        Args:
            severity: Severity level ('high', 'medium', 'low')
            
        Returns:
            List of alerts with specified severity
        """
        return [a for a in self.alerts if a['severity'] == severity]
    
    def get_recent_alerts(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent alerts.
        
        Args:
            n: Number of recent alerts to return
            
        Returns:
            List of recent alerts
        """
        return list(self.alerts)[-n:]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            
        Returns:
            True if successful, False otherwise
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'acknowledged'
                alert['acknowledged_at'] = datetime.now()
                self.logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_note: str = '') -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of alert to resolve
            resolution_note: Note about resolution
            
        Returns:
            True if successful, False otherwise
        """
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['status'] = 'resolved'
                alert['resolved_at'] = datetime.now()
                alert['resolution_note'] = resolution_note
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dictionary with alert statistics
        """
        active_alerts = len(self.get_active_alerts())
        
        stats = self.stats.copy()
        stats['active_alerts'] = active_alerts
        
        if self.alerts:
            recent_time = datetime.now() - timedelta(hours=1)
            recent_alerts = [a for a in self.alerts if a['timestamp'] > recent_time]
            stats['alerts_last_hour'] = len(recent_alerts)
        else:
            stats['alerts_last_hour'] = 0
        
        return stats
    
    def print_statistics(self):
        """Print alert statistics."""
        stats = self.get_statistics()
        
        print(f"\n{'='*60}")
        print("Alert Manager Statistics")
        print(f"{'='*60}")
        print(f"Total Alerts: {stats['total_alerts']}")
        print(f"Active Alerts: {stats['active_alerts']}")
        print(f"Alerts (Last Hour): {stats['alerts_last_hour']}")
        print(f"\nBy Severity:")
        print(f"  High:   {stats['high_severity']}")
        print(f"  Medium: {stats['medium_severity']}")
        print(f"  Low:    {stats['low_severity']}")
        print(f"{'='*60}\n")
    
    def export_alerts(self, filepath: str, format: str = 'json'):
        """
        Export alerts to file.
        
        Args:
            filepath: Path to export file
            format: Export format ('json' or 'csv')
        """
        if format == 'json':
            alerts_data = []
            for alert in self.alert_history:
                alert_copy = alert.copy()
                alert_copy['timestamp'] = alert_copy['timestamp'].isoformat()
                alerts_data.append(alert_copy)
            
            with open(filepath, 'w') as f:
                json.dump(alerts_data, f, indent=2)
        
        self.logger.info(f"Alerts exported to {filepath}")