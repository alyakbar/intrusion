# Network Anomaly Detection System

A comprehensive, modular Machine Learning-based Network Anomaly Detection System supporting offline dataset training (NSL-KDD), real-time packet capture (Scapy / PyShark with synthetic fallback), live anomaly scoring, SQLite persistence, and a Dash-powered monitoring dashboard.

## Features

- **Multiple ML Models**: Supervised (Random Forest, SVM, Gradient Boosting, Logistic Regression, Decision Tree) & Unsupervised (Isolation Forest, K-Means, DBSCAN, LOF)
- **Deep Learning**: Autoencoder, DNN, LSTM (placeholder extension) using TensorFlow/Keras
- **Real-time Detection**: Interface packet capture (Scapy raw sniff / PyShark) with synthetic fallback if privileges/traffic unavailable
- **Persistence Layer**: SQLite database (`data/detections.db`) logging each detection (timestamp, IPs, protocol, score, severity)
- **Live Dashboard**: Dash app visualizing stats, timeline, distributions, severity counts from DB (auto-refresh)
- **Dataset Support**: NSL-KDD integrated; CICIDS structure ready for extension
- **Comprehensive Evaluation**: Accuracy, precision, recall, F1-score, ROC-AUC, confusion matrix
- **Alert Management**: Severity tagging (low/medium/high) ready for future notification outputs
- **Configuration Driven**: Central `configs/config.yaml` for models, training, persistence, dashboard
- **Logging & Monitoring**: Structured application logging, hooks for future resource monitoring
- **CLI Tooling**: Console script `anomaly-detect` + module entrypoints

## Quick Run Guide

### 1. Environment Setup
```bash
cd /home/non/Desktop/New\ Folder/khan/network-anomaly-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify & Test
```bash
python verify_installation.py
pytest tests/ -v
```

### 3. Train a Model
```bash
anomaly-detect --mode train --model random_forest --evaluate
```
Train all:
```bash
anomaly-detect --mode train --model all --evaluate
```

### 4. Real-Time Detection (Packet Capture)
Loopback (synthetic fallback automatically if needed):
```bash
anomaly-detect --mode detect --model random_forest --interface lo --duration 15
```
Specific interface with PyShark backend:
```bash
anomaly-detect --mode detect --model random_forest --interface eth0 --backend pyshark --duration 30
```

Packet count limited run (captures exactly 25 packets then stops):
```bash
anomaly-detect --mode detect --model random_forest --interface eth0 --packet-count 25
```

Injected anomalies (20% synthetic, throttled 10ms):
```bash
anomaly-detect --mode detect --model random_forest --interface lo --packet-count 50 --inject-rate 0.2 --synthetic-delay 0.01
```

Continuous with low-rate injected anomalies (5%) until Ctrl+C:
```bash
anomaly-detect --mode detect --model random_forest --interface lo --inject-rate 0.05 --synthetic-delay 0.05
```

Continuous capture (until Ctrl+C):
```bash
anomaly-detect --mode detect --model random_forest --interface eth0
```

Flags summary:
- `--packet-count N`: Stop after N packets (overrides duration if both supplied until count reached first).
- `--duration S`: Run for S seconds (ignored once packet-count reached; if only duration given stops on time).
- No `--packet-count` & no `--duration`: Continuous until interrupted.
- `--backend {scapy|pyshark}`: Choose capture library (scapy supports timeout internally; pyshark uses loop break checks).
- `--inject-rate F`: Fraction (0-1) of synthetic fallback packets forcibly marked anomalous (demo/testing only; real captures unaffected).
- `--synthetic-delay SECONDS`: Sleep between synthetic packets to control generation speed.

### 5. Launch Dashboard (DB-backed)
```bash
anomaly-detect --mode dashboard
```
Open http://127.0.0.1:8050 (keep detection running in another terminal for live updates).

### 6. Inspect Logged Detections
```bash
sqlite3 data/detections.db "SELECT id,timestamp,source_ip,dest_ip,protocol,anomaly_score,is_anomaly,severity FROM detections ORDER BY id DESC LIMIT 10;"
```

### 7. Notebook Exploration
```bash
source venv/bin/activate
jupyter notebook notebooks/exploratory_analysis.ipynb
```

### 8. Configuration Tweaks
Edit `configs/config.yaml` (e.g. thresholds, batch_size, enable_database) then re-run commands.

## Project Structure

```
network-anomaly-project/
├── anomaly_detection/          # Main package
│   ├── data_processing/        # Data loading and preprocessing
│   ├── models/                 # ML model implementations
│   ├── training/               # Model training and evaluation
│   ├── inference/              # Real-time detection and alerts
│   ├── visualization/          # Dashboard and plotting
│   ├── monitoring/             # Automated monitoring
│   └── utils/                  # Utilities and configuration
├── configs/                    # Configuration files
├── data/                       # Dataset storage
├── logs/                       # Application logs
├── notebooks/                  # Jupyter notebooks
├── saved_models/               # Trained models
└── tests/                      # Unit tests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/network-anomaly-detection.git
cd network-anomaly-detection
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install the package:
```bash
pip install -e .
```

## Usage

### Configuration

Edit `configs/config.yaml` to customize:
- Dataset paths and parameters
- Model hyperparameters
- Real-time detection settings
- Alert thresholds
- Visualization preferences

### Training Models

```python
from anomaly_detection.training.trainer import ModelTrainer
from anomaly_detection.utils.config import load_config

config = load_config('configs/config.yaml')
trainer = ModelTrainer(config)

# Train all models
trainer.train_all_models()

# Or train specific model
trainer.train_model('random_forest')
```

### Real-time Detection

```python
from anomaly_detection.inference.realtime_detector import RealtimeDetector

detector = RealtimeDetector(config)
detector.start_monitoring()
```

### Run Dashboard

```bash
python -m anomaly_detection.visualization.dashboard
```

Or use the CLI:
```bash
anomaly-detect --mode dashboard
```

### Command Line Interface

```bash
# Train models
anomaly-detect --mode train --model all

# Run real-time detection
anomaly-detect --mode detect --interface eth0 --packet-count 50

# Start dashboard
anomaly-detect --mode dashboard

# Evaluate models
anomaly-detect --mode evaluate
```

## Datasets

### NSL-KDD Dataset

Download from: [NSL-KDD Dataset](https://www.unb.ca/cic/datasets/nsl.html)

Place files in `data/raw/nsl-kdd/`

### CICIDS Dataset

Download from: [CICIDS Dataset](https://www.unb.ca/cic/datasets/ids-2017.html)

Place files in `data/raw/cicids/`

## Model Performance (NSL-KDD Example)

| Model | Accuracy | Precision | Recall | F1-Score | Notes |
|-------|----------|-----------|--------|----------|-------|
| Random Forest | 99.95% | 99.97% | 99.93% | 99.95% | Trained & saved (`saved_models/supervised/random_forest.joblib`) |
| Gradient Boosting | TBD | TBD | TBD | TBD | Train: `--model gradient_boosting` |
| SVM | TBD | TBD | TBD | TBD | May be slower on full feature set |
| Logistic Regression | TBD | TBD | TBD | TBD | Fast baseline |
| Decision Tree | TBD | TBD | TBD | TBD | Interpretable baseline |
| Isolation Forest | TBD | TBD | TBD | TBD | Unsupervised |
| K-Means | TBD | N/A | N/A | N/A | Cluster distances |
| DBSCAN | TBD | N/A | N/A | N/A | Density-based |
| LOF | TBD | N/A | N/A | N/A | Local outlier scores |
| Autoencoder | TBD | TBD | TBD | TBD | Reconstruction error |
| DNN | TBD | TBD | TBD | TBD | General classifier |
| LSTM | Placeholder | - | - | - | Sequence modeling extension |

## Development

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=anomaly_detection tests/

# Run specific test file
pytest tests/test_models.py
```

### Code Structure

- **Data Processing**: Handles data loading, cleaning, preprocessing, and feature engineering
- **Models**: Implements various ML models (supervised, unsupervised, neural networks)
- **Training**: Manages model training, hyperparameter tuning, and evaluation
- **Inference**: Provides real-time detection capabilities
- **Visualization**: Creates plots, charts, and interactive dashboard
- **Monitoring**: Tracks system performance and model metrics
- **Utils**: Configuration management, logging, and helper functions

## Persistence & Live Monitoring

The persistence layer (`anomaly_detection/persistence/db.py`) logs each detection event into SQLite. The dashboard queries fresh data every 5 seconds for:
- Total packet / anomaly counts and detection rate
- Recent anomaly score timeline
- Score distribution (normal vs anomaly)
- Severity counts (high / medium / low)

Severity tagging is currently basic; extend logic for probabilistic thresholds or external alerting (email, webhook, etc.). For higher scale swap SQLite with another backend by replacing the manager.

## SDLC Methodology
## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| No packets captured | Insufficient privileges or silent interface | Use `--backend pyshark`, different interface, or (carefully) run with sudo |
| Dashboard not updating | No detection process populating DB | Run detect mode concurrently |
| SQLite thread error (legacy) | Old shared connection | Update code & restart; current version uses per-call connections |
| High memory usage | Large batch size / neural nets | Reduce `training.batch_size` or disable large models |
| Module not found | Env not activated | `source venv/bin/activate` then reinstall requirements |
| Dataset missing | Files absent | Follow `DATASET_DOWNLOAD_GUIDE.md` and place in `data/raw/nsl-kdd/` |

Quick checks:
```bash
grep enable_database configs/config.yaml
sqlite3 data/detections.db "SELECT COUNT(*) FROM detections;"
tail -f logs/anomaly_detection.log
```

This project follows standard Software Development Life Cycle phases:

1. **Requirements Analysis**: Define system requirements and objectives
2. **Design**: Architecture design and component specification
3. **Implementation**: Code development following best practices
4. **Testing**: Unit tests, integration tests, and system tests
5. **Deployment**: Model deployment and monitoring setup
6. **Maintenance**: Continuous monitoring and model updates

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NSL-KDD Dataset creators
- CICIDS Dataset creators
- Scikit-learn and TensorFlow communities

## Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/network-anomaly-detection](https://github.com/yourusername/network-anomaly-detection)