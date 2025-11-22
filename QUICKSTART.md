# Quick Start Guide

## Network Anomaly Detection System

This guide will help you get started with the Network Anomaly Detection System quickly.

## Prerequisites

- Python 3.8 or higher
- pip package manager
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space

## Installation

### 1. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Package

```bash
pip install -e .
```

## Quick Demo with Synthetic Data

Run the example script to see the system in action with synthetic data:

```bash
python example_usage.py
```

This will demonstrate:
- Data preprocessing
- Training supervised models (Random Forest, Gradient Boosting)
- Training unsupervised models (Isolation Forest, K-Means)
- Model evaluation and comparison
- Visualization

## Using Real Datasets

### NSL-KDD Dataset

1. **Download the dataset:**
   - Visit: https://www.unb.ca/cic/datasets/nsl.html
   - Download `KDDTrain+.txt` and `KDDTest+.txt`

2. **Place files in the correct location:**
   ```bash
   mkdir -p data/raw/nsl-kdd
   # Move downloaded files to data/raw/nsl-kdd/
   ```

3. **Train models:**
   ```bash
   python -m anomaly_detection.main --mode train --model all --evaluate
   ```

### CICIDS Dataset

1. **Download the dataset:**
   - Visit: https://www.unb.ca/cic/datasets/ids-2017.html
   - Download CSV files

2. **Place files:**
   ```bash
   mkdir -p data/raw/cicids
   # Move CSV files to data/raw/cicids/
   ```

## Common Tasks

### Train Specific Model

```bash
# Train Random Forest
python -m anomaly_detection.main --mode train --model random_forest

# Train Isolation Forest
python -m anomaly_detection.main --mode train --model isolation_forest

# Train Deep Neural Network
python -m anomaly_detection.main --mode train --model dnn
```

### Run Dashboard

```bash
python -m anomaly_detection.main --mode dashboard
```

Then open browser to: http://127.0.0.1:8050

### Run Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest --cov=anomaly_detection tests/

# Run specific test file
pytest tests/test_models.py
```

### Evaluate Models

```bash
python -m anomaly_detection.main --mode train --evaluate
```

## Configuration

Edit `configs/config.yaml` to customize:

- Model hyperparameters
- Data preprocessing options
- Real-time detection settings
- Alert thresholds
- Dashboard settings

## Directory Structure

```
network-anomaly-project/
├── anomaly_detection/       # Main package
│   ├── data_processing/     # Data loading and preprocessing
│   ├── models/              # ML models
│   ├── training/            # Training and evaluation
│   ├── inference/           # Real-time detection
│   ├── visualization/       # Dashboard and plots
│   ├── monitoring/          # System monitoring
│   └── utils/               # Utilities
├── configs/                 # Configuration files
├── data/                    # Datasets
│   ├── raw/                 # Raw datasets
│   └── processed/           # Processed data
├── saved_models/            # Trained models
├── logs/                    # Application logs
├── tests/                   # Unit tests
└── notebooks/               # Jupyter notebooks
```

## Troubleshooting

### Import Errors

```bash
# Make sure package is installed
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

### Missing Dependencies

```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

### TensorFlow GPU Issues

```bash
# Install CPU version if GPU not available
pip install tensorflow-cpu
```

### Dataset Not Found

Make sure datasets are in the correct directories:
- NSL-KDD: `data/raw/nsl-kdd/`
- CICIDS: `data/raw/cicids/`

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Explore Jupyter notebooks** in `notebooks/` directory
3. **Customize configuration** in `configs/config.yaml`
4. **Implement real-time detection** by integrating with network interfaces
5. **Add custom models** by extending model classes

## Support

For issues and questions:
- Check the documentation in README.md
- Review example code in `example_usage.py`
- Run tests to verify installation: `pytest tests/`

## Key Features

✅ Multiple ML models (supervised & unsupervised)
✅ Deep learning with TensorFlow
✅ Real-time detection capability
✅ Interactive dashboard
✅ Comprehensive evaluation metrics
✅ Automated monitoring
✅ Alert management system
✅ Visualization tools

Happy anomaly detecting! 🔍🛡️
