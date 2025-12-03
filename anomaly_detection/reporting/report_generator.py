"""
Detection report generator for PDF and CSV exports.
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
from io import BytesIO

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from ..utils.logger import LoggerFactory
from ..persistence.db import DatabaseManager


class ReportGenerator:
    """Generate detection reports in PDF and CSV formats."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize report generator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = LoggerFactory.get_logger('ReportGenerator')
        self.db_manager = DatabaseManager(config)
    
    def generate_report(
        self,
        output_path: str,
        format: str = 'pdf',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Generate detection report.
        
        Args:
            output_path: Output file path
            format: Report format ('pdf' or 'csv')
            start_date: Optional start date filter
            end_date: Optional end date filter
            include_charts: Include visualizations in PDF (requires matplotlib)
            
        Returns:
            Result dictionary with status and file path
        """
        try:
            # Query detections
            detections = self._query_detections(start_date, end_date)
            
            if not detections:
                return {
                    'status': 'no_data',
                    'message': 'No detections found for the specified date range'
                }
            
            # Generate report based on format
            if format.lower() == 'pdf':
                if not REPORTLAB_AVAILABLE:
                    return {
                        'status': 'error',
                        'message': 'reportlab not installed. Install with: pip install reportlab'
                    }
                result = self._generate_pdf_report(output_path, detections, include_charts)
            elif format.lower() == 'csv':
                result = self._generate_csv_report(output_path, detections)
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported format: {format}'
                }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _query_detections(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[Dict[str, Any]]:
        """
        Query detections from database.
        
        Args:
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of detection dictionaries
        """
        db_path = self.config.get('persistence', {}).get('db_path', 'data/detections.db')
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM detections WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
        
        query += " ORDER BY timestamp DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        detections = [dict(row) for row in rows]
        
        conn.close()
        
        return detections
    
    def _generate_csv_report(
        self,
        output_path: str,
        detections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate CSV report.
        
        Args:
            output_path: Output file path
            detections: List of detections
            
        Returns:
            Result dictionary
        """
        try:
            df = pd.DataFrame(detections)
            df.to_csv(output_path, index=False)
            
            self.logger.info(f"CSV report generated: {output_path}")
            
            return {
                'status': 'success',
                'file_path': output_path,
                'format': 'csv',
                'detection_count': len(detections)
            }
            
        except Exception as e:
            self.logger.error(f"CSV generation failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _generate_pdf_report(
        self,
        output_path: str,
        detections: List[Dict[str, Any]],
        include_charts: bool
    ) -> Dict[str, Any]:
        """
        Generate PDF report.
        
        Args:
            output_path: Output file path
            detections: List of detections
            include_charts: Include visualizations
            
        Returns:
            Result dictionary
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                alignment=TA_CENTER,
                spaceAfter=30
            )
            story.append(Paragraph("Network Anomaly Detection Report", title_style))
            story.append(Spacer(1, 0.2 * inch))
            
            # Report metadata
            metadata = self._generate_metadata(detections)
            story.append(Paragraph("<b>Report Details</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            metadata_data = [
                ['Generated:', metadata['generated']],
                ['Date Range:', metadata['date_range']],
                ['Total Detections:', str(metadata['total_detections'])],
                ['Unique Sources:', str(metadata['unique_sources'])],
                ['Anomaly Rate:', f"{metadata['anomaly_rate']:.2f}%"]
            ]
            
            metadata_table = Table(metadata_data, colWidths=[2*inch, 4*inch])
            metadata_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(metadata_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Summary statistics
            stats = self._generate_statistics(detections)
            story.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            # By severity
            story.append(Paragraph("<i>By Severity</i>", styles['Heading3']))
            severity_data = [['Severity', 'Count', 'Percentage']]
            for severity, count in stats['by_severity'].items():
                pct = (count / stats['total']) * 100
                severity_data.append([severity, str(count), f"{pct:.1f}%"])
            
            severity_table = Table(severity_data, colWidths=[2*inch, 2*inch, 2*inch])
            severity_table.setStyle(self._get_table_style())
            story.append(severity_table)
            story.append(Spacer(1, 0.2 * inch))
            
            # By attack type
            if stats['by_attack_type']:
                story.append(Paragraph("<i>By Attack Type</i>", styles['Heading3']))
                attack_data = [['Attack Type', 'Count', 'Percentage']]
                for attack_type, count in sorted(stats['by_attack_type'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    pct = (count / stats['total']) * 100
                    attack_data.append([attack_type, str(count), f"{pct:.1f}%"])
                
                attack_table = Table(attack_data, colWidths=[2*inch, 2*inch, 2*inch])
                attack_table.setStyle(self._get_table_style())
                story.append(attack_table)
                story.append(Spacer(1, 0.2 * inch))
            
            # Top source IPs
            story.append(Paragraph("<i>Top Source IPs</i>", styles['Heading3']))
            top_sources_data = [['Source IP', 'Detection Count']]
            for ip, count in stats['top_sources'][:10]:
                top_sources_data.append([ip, str(count)])
            
            top_sources_table = Table(top_sources_data, colWidths=[3*inch, 3*inch])
            top_sources_table.setStyle(self._get_table_style())
            story.append(top_sources_table)
            story.append(Spacer(1, 0.3 * inch))
            
            # Charts
            if include_charts:
                try:
                    chart_images = self._generate_charts(detections)
                    if chart_images:
                        story.append(PageBreak())
                        story.append(Paragraph("<b>Visualizations</b>", styles['Heading2']))
                        story.append(Spacer(1, 0.2 * inch))
                        
                        for chart_img in chart_images:
                            img = Image(chart_img, width=6*inch, height=4*inch)
                            story.append(img)
                            story.append(Spacer(1, 0.3 * inch))
                except Exception as e:
                    self.logger.warning(f"Chart generation failed: {e}")
            
            # Recent detections
            story.append(PageBreak())
            story.append(Paragraph("<b>Recent Detections (Last 50)</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1 * inch))
            
            recent_data = [['Timestamp', 'Source', 'Dest', 'Protocol', 'Severity']]
            for detection in detections[:50]:
                recent_data.append([
                    detection.get('timestamp', '')[:19],
                    detection.get('src_ip', 'N/A'),
                    detection.get('dst_ip', 'N/A'),
                    detection.get('protocol', 'N/A'),
                    detection.get('severity', 'N/A')
                ])
            
            recent_table = Table(recent_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch, 1*inch])
            recent_table.setStyle(self._get_table_style())
            story.append(recent_table)
            
            # Build PDF
            doc.build(story)
            
            self.logger.info(f"PDF report generated: {output_path}")
            
            return {
                'status': 'success',
                'file_path': output_path,
                'format': 'pdf',
                'detection_count': len(detections)
            }
            
        except Exception as e:
            self.logger.error(f"PDF generation failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style."""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
    
    def _generate_metadata(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report metadata."""
        timestamps = [d.get('timestamp', '') for d in detections if d.get('timestamp')]
        
        date_range = 'N/A'
        if timestamps:
            sorted_times = sorted(timestamps)
            date_range = f"{sorted_times[0][:10]} to {sorted_times[-1][:10]}"
        
        unique_sources = len(set(d.get('src_ip', '') for d in detections if d.get('src_ip')))
        
        return {
            'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date_range': date_range,
            'total_detections': len(detections),
            'unique_sources': unique_sources,
            'anomaly_rate': 100.0  # All records are anomalies
        }
    
    def _generate_statistics(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics from detections."""
        stats = {
            'total': len(detections),
            'by_severity': {},
            'by_attack_type': {},
            'by_protocol': {},
            'top_sources': []
        }
        
        # Count by severity
        for detection in detections:
            severity = detection.get('severity', 'unknown')
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        # Count by attack type
        for detection in detections:
            attack_type = detection.get('attack_type', 'unknown')
            if attack_type:
                stats['by_attack_type'][attack_type] = stats['by_attack_type'].get(attack_type, 0) + 1
        
        # Count by protocol
        for detection in detections:
            protocol = detection.get('protocol', 'unknown')
            stats['by_protocol'][protocol] = stats['by_protocol'].get(protocol, 0) + 1
        
        # Top source IPs
        source_counts = {}
        for detection in detections:
            src_ip = detection.get('src_ip', 'unknown')
            source_counts[src_ip] = source_counts.get(src_ip, 0) + 1
        
        stats['top_sources'] = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        
        return stats
    
    def _generate_charts(self, detections: List[Dict[str, Any]]) -> List[BytesIO]:
        """
        Generate charts for PDF report.
        
        Args:
            detections: List of detections
            
        Returns:
            List of image buffers
        """
        try:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            chart_images = []
            
            # Timeline chart
            df = pd.DataFrame(detections)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                daily_counts = df.groupby('date').size()
                
                fig, ax = plt.subplots(figsize=(8, 5))
                daily_counts.plot(kind='line', ax=ax, marker='o')
                ax.set_title('Detections Timeline')
                ax.set_xlabel('Date')
                ax.set_ylabel('Detection Count')
                ax.grid(True, alpha=0.3)
                
                buf = BytesIO()
                plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                buf.seek(0)
                chart_images.append(buf)
                plt.close()
            
            return chart_images
            
        except ImportError:
            self.logger.warning("matplotlib not available for chart generation")
            return []
        except Exception as e:
            self.logger.error(f"Chart generation error: {e}")
            return []
