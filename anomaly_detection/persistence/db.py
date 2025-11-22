"""SQLite persistence layer for detection logging and metrics aggregation."""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..utils.logger import LoggerFactory


class DatabaseManager:
    """Manage SQLite database for anomaly detections."""

    def __init__(self, config: Dict[str, Any]):
        persistence_cfg = config.get('persistence', {})
        self.enabled = persistence_cfg.get('enable_database', True)
        self.db_path = Path(persistence_cfg.get('database_path', 'data/detections.db'))
        self.logger = LoggerFactory.get_logger('DatabaseManager')
        # We avoid holding a single connection across threads; create per-call connections.
        self._conn: Optional[sqlite3.Connection] = None  # Deprecated usage; retained for backward compatibility in close()
        self._lock = threading.Lock()
        if self.enabled:
            self._initialize()

    def _initialize(self):
        """Initialize database and tables."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS detections (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              timestamp TEXT NOT NULL,
              source_ip TEXT,
              dest_ip TEXT,
              source_port INTEGER,
              dest_port INTEGER,
              protocol TEXT,
              anomaly_score REAL,
              is_anomaly INTEGER,
              severity TEXT,
              raw_packet TEXT
            )
            """
        )
        
        # Add port columns if they don't exist (for existing databases)
        try:
            conn.execute("ALTER TABLE detections ADD COLUMN source_port INTEGER")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        try:
            conn.execute("ALTER TABLE detections ADD COLUMN dest_port INTEGER")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()
        conn.close()
        self.logger.info(f"Database initialized at {self.db_path}")

    def _connect(self) -> sqlite3.Connection:
        """Create a new SQLite connection safe for cross-thread use."""
        return sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)

    def log_detection(self, record: Dict[str, Any]):
        """Insert detection record.

        Expected keys: timestamp (datetime), source_ip, dest_ip, source_port, dest_port,
                       protocol, anomaly_score, is_anomaly (bool/int), severity, raw_packet (str/JSON)
        """
        if not self.enabled:
            return
        try:
            ts = record.get('timestamp', datetime.utcnow())
            if isinstance(ts, datetime):
                ts = ts.isoformat()
            with self._lock:
                conn = self._connect()
                conn.execute(
                    """INSERT INTO detections (timestamp, source_ip, dest_ip, source_port, dest_port, protocol, anomaly_score, is_anomaly, severity, raw_packet)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        ts,
                        record.get('source_ip'),
                        record.get('dest_ip'),
                        record.get('source_port'),
                        record.get('dest_port'),
                        record.get('protocol'),
                        float(record.get('anomaly_score', 0.0)),
                        1 if record.get('is_anomaly') else 0,
                        record.get('severity'),
                        record.get('raw_packet')
                    )
                )
                conn.commit()
                conn.close()
        except Exception as e:
            self.logger.error(f"Failed to log detection: {e}")

    def fetch_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        if not self.enabled:
            return []
        conn = self._connect()
        cur = conn.execute(
            "SELECT id, timestamp, source_ip, dest_ip, protocol, anomaly_score, is_anomaly, severity FROM detections ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                'id': r[0], 'timestamp': r[1], 'source_ip': r[2], 'dest_ip': r[3],
                'protocol': r[4], 'anomaly_score': r[5], 'is_anomaly': bool(r[6]), 'severity': r[7]
            } for r in rows
        ]

    def get_stats(self) -> Dict[str, Any]:
        if not self.enabled:
            return {'total': 0, 'anomalies': 0, 'detection_rate': 0.0}
        conn = self._connect()
        cur = conn.execute("SELECT COUNT(*), SUM(is_anomaly) FROM detections")
        total, anomalies = cur.fetchone()
        conn.close()
        anomalies = anomalies or 0
        rate = (anomalies / total * 100.0) if total else 0.0
        return {
            'total': total,
            'anomalies': anomalies,
            'detection_rate': rate
        }

    def metric_timeseries(self, limit: int = 50) -> Dict[str, List[Any]]:
        if not self.enabled:
            return {'timestamps': [], 'scores': [], 'colors': []}
        conn = self._connect()
        cur = conn.execute(
            "SELECT timestamp, anomaly_score, is_anomaly FROM detections ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()[::-1]
        conn.close()
        return {
            'timestamps': [r[0] for r in rows],
            'scores': [r[1] for r in rows],
            'colors': [r[2] for r in rows]
        }

    def severity_counts(self) -> Dict[str, int]:
        if not self.enabled:
            return {'high': 0, 'medium': 0, 'low': 0, 'total': 0}
        conn = self._connect()
        cur = conn.execute(
            "SELECT severity, COUNT(*) FROM detections WHERE is_anomaly=1 GROUP BY severity"
        )
        counts = {row[0]: row[1] for row in cur.fetchall()}
        conn.close()
        total = sum(counts.values())
        return {
            'high': counts.get('high', 0),
            'medium': counts.get('medium', 0),
            'low': counts.get('low', 0),
            'total': total
        }

    def close(self):
        # Backward compatibility; no persistent connection kept now.
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None
