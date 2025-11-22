"""
Interactive dashboard for real-time monitoring and visualization.
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from typing import Dict, Any
from datetime import datetime
from ..persistence.db import DatabaseManager


class AnomalyDashboard:
    """Interactive dashboard for anomaly detection monitoring."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize dashboard.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        dash_config = config.get('visualization', {}).get('dashboard', {})
        
        self.host = dash_config.get('host', '127.0.0.1')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        
        # Initialize Dash app
        self.app = dash.Dash(__name__)
        # Database manager for live metrics
        self.db_manager = DatabaseManager(self.config)
        self._setup_layout()
        self._setup_callbacks()
    
    def _setup_layout(self):
        """Setup dashboard layout."""
        self.app.layout = html.Div([
            html.H1('Network Anomaly Detection Dashboard',
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            html.Div([
                html.Div([
                    html.H3('Real-time Statistics'),
                    html.Div(id='stats-container')
                ], className='six columns'),
                
                html.Div([
                    html.H3('Alert Summary'),
                    html.Div(id='alert-summary')
                ], className='six columns'),
            ], className='row'),
            
            html.Hr(),
            
            html.Div([
                html.H3('Detection Timeline'),
                dcc.Graph(id='timeline-graph')
            ]),
            
            html.Hr(),
            
            html.Div([
                html.Div([
                    html.H3('Model Performance'),
                    dcc.Graph(id='performance-graph')
                ], className='six columns'),
                
                html.Div([
                    html.H3('Anomaly Distribution'),
                    dcc.Graph(id='distribution-graph')
                ], className='six columns'),
            ], className='row'),
            
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # Update every 5 seconds
                n_intervals=0
            )
        ])
    
    def _setup_callbacks(self):
        """Setup dashboard callbacks."""
        
        @self.app.callback(
            Output('stats-container', 'children'),
            Input('interval-component', 'n_intervals')
        )
        def update_stats(n):
            """Update statistics display."""
            stats_data = self._get_live_stats()
            
            return html.Div([
                html.P(f"Total Packets: {stats_data['total_packets']}"),
                html.P(f"Anomalies Detected: {stats_data['anomalies']}"),
                html.P(f"Detection Rate: {stats_data['detection_rate']:.2f}%"),
                html.P(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")
            ])
        
        @self.app.callback(
            Output('alert-summary', 'children'),
            Input('interval-component', 'n_intervals')
        )
        def update_alerts(n):
            """Update alert summary."""
            alert_data = self._get_live_alerts()
            
            return html.Div([
                html.P(f"🔴 High: {alert_data['high']}", style={'color': 'red'}),
                html.P(f"🟡 Medium: {alert_data['medium']}", style={'color': 'orange'}),
                html.P(f"🟢 Low: {alert_data['low']}", style={'color': 'green'}),
                html.P(f"Total Alerts: {alert_data['total']}")
            ])
        
        @self.app.callback(
            Output('timeline-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_timeline(n):
            """Update detection timeline."""
            timeline_data = self._get_live_timeline()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timeline_data['timestamps'],
                y=timeline_data['scores'],
                mode='markers+lines',
                name='Anomaly Score',
                marker=dict(
                    size=8,
                    color=timeline_data['colors'],
                    colorscale='RdYlGn_r'
                )
            ))
            
            fig.add_hline(y=0.5, line_dash='dash', line_color='orange',
                         annotation_text='Threshold')
            
            fig.update_layout(
                xaxis_title='Time',
                yaxis_title='Anomaly Score',
                hovermode='closest',
                showlegend=True
            )
            
            return fig
        
        @self.app.callback(
            Output('performance-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_performance(n):
            """Update performance metrics."""
            perf_data = self._get_live_performance()
            
            fig = go.Figure(data=[
                go.Bar(name='Metrics', x=perf_data['metrics'], y=perf_data['values'])
            ])
            
            fig.update_layout(
                xaxis_title='Metric',
                yaxis_title='Score',
                yaxis_range=[0, 1],
                showlegend=False
            )
            
            return fig
        
        @self.app.callback(
            Output('distribution-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_distribution(n):
            """Update anomaly distribution."""
            dist_data = self._get_live_distribution()
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=dist_data['normal'],
                name='Normal',
                opacity=0.7,
                marker_color='blue'
            ))
            fig.add_trace(go.Histogram(
                x=dist_data['anomaly'],
                name='Anomaly',
                opacity=0.7,
                marker_color='red'
            ))
            
            fig.update_layout(
                xaxis_title='Anomaly Score',
                yaxis_title='Frequency',
                barmode='overlay',
                showlegend=True
            )
            
            return fig
    
    def _get_live_stats(self) -> Dict[str, Any]:
        """Fetch live statistics from database or fallback."""
        if not self.db_manager.enabled:
            return {'total_packets': 0, 'anomalies': 0, 'detection_rate': 0.0}
        stats = self.db_manager.get_stats()
        return {
            'total_packets': stats['total'],
            'anomalies': stats['anomalies'],
            'detection_rate': stats['detection_rate']
        }
    
    def _get_live_alerts(self) -> Dict[str, int]:
        if not self.db_manager.enabled:
            return {'high': 0, 'medium': 0, 'low': 0, 'total': 0}
        return self.db_manager.severity_counts()
    
    def _get_live_timeline(self) -> Dict[str, list]:
        data = self.db_manager.metric_timeseries(limit=50)
        # Convert timestamp strings to datetime for plotting
        try:
            ts = [datetime.fromisoformat(t) for t in data['timestamps']]
        except Exception:
            ts = data['timestamps']
        return {'timestamps': ts, 'scores': data['scores'], 'colors': data['colors']}
    
    def _get_live_performance(self) -> Dict[str, list]:
        # Placeholder: could aggregate recent anomaly_score stats as pseudo performance
        stats = self.db_manager.get_stats()
        if stats['total'] == 0:
            return {'metrics': ['Accuracy', 'Precision', 'Recall', 'F1-Score'], 'values': [0, 0, 0, 0]}
        # Without ground truth labels in DB, we approximate using anomaly ratio
        anomaly_ratio = stats['anomalies'] / stats['total']
        return {
            'metrics': ['Packets', 'Anomalies', 'Anomaly Ratio', 'Detection Rate %'],
            'values': [stats['total'], stats['anomalies'], anomaly_ratio, stats['detection_rate'] / 100.0]
        }
    
    def _get_live_distribution(self) -> Dict[str, list]:
        recent = self.db_manager.fetch_recent(limit=200)
        normal_scores = [r['anomaly_score'] for r in recent if not r['is_anomaly']]
        anomaly_scores = [r['anomaly_score'] for r in recent if r['is_anomaly']]
        return {
            'normal': normal_scores,
            'anomaly': anomaly_scores
        }
    
    def run(self):
        """Run the dashboard server."""
        print(f"Starting dashboard at http://{self.host}:{self.port}")
        # Dash >=3 replaced run_server with run
        self.app.run(host=self.host, port=self.port, debug=self.debug)


if __name__ == '__main__':
    from ..utils.config import load_config
    
    config = load_config('configs/config.yaml')
    dashboard = AnomalyDashboard(config)
    dashboard.run()