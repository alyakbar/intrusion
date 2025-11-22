# Dataset Download Guide

## Complete Guide to Downloading and Setting Up Real Network Anomaly Detection Datasets

---

## 📊 Option 1: NSL-KDD Dataset (RECOMMENDED FOR BEGINNERS)

### About NSL-KDD
- **Type**: Network intrusion detection dataset
- **Size**: ~150 MB
- **Samples**: ~125,000 training + ~22,500 test records
- **Features**: 41 features + 1 label
- **Classes**: Binary (Normal vs Attack) or Multi-class (5 attack types)
- **Best for**: Quick start, benchmarking, research

### Download Steps

#### Method 1: Official Website
1. **Visit**: https://www.unb.ca/cic/datasets/nsl.html

2. **Download these files**:
   - `KDDTrain+.txt` - Training set
   - `KDDTest+.txt` - Test set
   - `KDDTrain+_20Percent.txt` - Smaller training set (optional)

3. **Alternative direct links**:
   ```
   https://github.com/defcom17/NSL_KDD/raw/master/KDDTrain%2B.txt
   https://github.com/defcom17/NSL_KDD/raw/master/KDDTest%2B.txt
   ```

#### Method 2: Using Command Line

```bash
# Navigate to project directory
cd /home/non/Desktop/New\ Folder/khan/network-anomaly-project

# Create directory
mkdir -p data/raw/nsl-kdd

# Download using wget
cd data/raw/nsl-kdd
wget https://github.com/defcom17/NSL_KDD/raw/master/KDDTrain%2B.txt
wget https://github.com/defcom17/NSL_KDD/raw/master/KDDTest%2B.txt

# Or using curl
curl -L -o KDDTrain+.txt https://github.com/defcom17/NSL_KDD/raw/master/KDDTrain%2B.txt
curl -L -o KDDTest+.txt https://github.com/defcom17/NSL_KDD/raw/master/KDDTest%2B.txt
```

#### Method 3: Python Script

```python
import urllib.request
import os

# Create directory
os.makedirs('data/raw/nsl-kdd', exist_ok=True)

# Download files
base_url = 'https://github.com/defcom17/NSL_KDD/raw/master/'
files = ['KDDTrain%2B.txt', 'KDDTest%2B.txt']

for file in files:
    url = base_url + file
    local_file = file.replace('%2B', '+')
    print(f'Downloading {local_file}...')
    urllib.request.urlretrieve(url, f'data/raw/nsl-kdd/{local_file}')
    print(f'✅ {local_file} downloaded!')
```

### File Structure After Download
```
data/raw/nsl-kdd/
├── KDDTrain+.txt      (~20 MB)
└── KDDTest+.txt       (~5 MB)
```

### Verify Installation

```bash
python -c "from anomaly_detection.data_processing.loader import DataLoader; \
           loader = DataLoader(); \
           train, test = loader.load_nsl_kdd(); \
           print(f'✅ NSL-KDD loaded: Train={train.shape}, Test={test.shape}')"
```

---

## 📊 Option 2: CICIDS 2017 Dataset (MORE COMPREHENSIVE)

### About CICIDS 2017
- **Type**: Intrusion Detection Evaluation Dataset
- **Size**: ~7 GB (full dataset)
- **Samples**: ~2.8 million records
- **Features**: 78 features + labels
- **Classes**: Normal + 14 attack types
- **Best for**: Real-world scenarios, comprehensive analysis

### Download Steps

#### Method 1: Official Website (Requires Registration)

1. **Visit**: https://www.unb.ca/cic/datasets/ids-2017.html

2. **Register/Login** (Free academic access)

3. **Download**: CSV files for each day
   - Monday-WorkingHours.pcap_ISCX.csv
   - Tuesday-WorkingHours.pcap_ISCX.csv
   - Wednesday-workingHours.pcap_ISCX.csv
   - Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
   - Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
   - Friday-WorkingHours-Morning.pcap_ISCX.csv
   - Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
   - Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv

#### Method 2: Kaggle (Alternative Source)

1. **Visit**: https://www.kaggle.com/datasets/cicdataset/cicids2017

2. **Download** the dataset (requires Kaggle account)

3. **Extract** CSV files

#### Method 3: Using Kaggle API

```bash
# Install Kaggle API
pip install kaggle

# Setup Kaggle credentials (get from kaggle.com/account)
mkdir -p ~/.kaggle
# Copy kaggle.json to ~/.kaggle/

# Download dataset
kaggle datasets download -d cicdataset/cicids2017 -p data/raw/cicids
cd data/raw/cicids
unzip cicids2017.zip
```

### Recommended Subset (For Quick Start)

If the full dataset is too large, download just **Monday** and **Friday** files:
- Monday: Normal traffic baseline (~440 MB)
- Friday: Contains DDoS attacks (~630 MB)

### File Structure After Download
```
data/raw/cicids/
├── Monday-WorkingHours.pcap_ISCX.csv
├── Tuesday-WorkingHours.pcap_ISCX.csv
├── Wednesday-workingHours.pcap_ISCX.csv
├── Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv
├── Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv
├── Friday-WorkingHours-Morning.pcap_ISCX.csv
├── Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv
└── Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
```

### Verify Installation

```bash
python -c "from anomaly_detection.data_processing.loader import DataLoader; \
           loader = DataLoader(); \
           data = loader.load_cicids(); \
           print(f'✅ CICIDS loaded: {data.shape}')"
```

---

## 📊 Option 3: Other Datasets

### 3.1 UNSW-NB15
- **Source**: https://research.unsw.edu.au/projects/unsw-nb15-dataset
- **Size**: ~2 GB
- **Records**: 2.5 million
- **Features**: 49 features
- **Good for**: Modern attack types

### 3.2 KDD Cup 1999 (Original)
- **Source**: http://kdd.ics.uci.edu/databases/kddcup99/kddcup99.html
- **Size**: ~700 MB
- **Historical**: Older dataset, less recommended
- **Use**: NSL-KDD instead (improved version)

### 3.3 CIC-IDS2018
- **Source**: https://www.unb.ca/cic/datasets/ids-2018.html
- **Size**: ~7 GB
- **Updated**: More recent than 2017 version
- **Similar**: To CICIDS 2017 but newer attacks

---

## 🚀 Quick Start After Download

### 1. Verify Dataset Location

```bash
# Check NSL-KDD
ls -lh data/raw/nsl-kdd/

# Check CICIDS
ls -lh data/raw/cicids/
```

### 2. Train Models

```bash
# With NSL-KDD
python -m anomaly_detection.main --mode train --model all --evaluate

# Or run the demo
python example_usage.py

# Or use the Jupyter notebook
jupyter notebook notebooks/exploratory_analysis.ipynb
```

### 3. Verify Loading

```python
from anomaly_detection.data_processing.loader import DataLoader

loader = DataLoader()

# Try NSL-KDD
try:
    train_data, test_data = loader.load_nsl_kdd()
    print(f"✅ NSL-KDD: Train={train_data.shape}, Test={test_data.shape}")
except Exception as e:
    print(f"❌ NSL-KDD: {e}")

# Try CICIDS
try:
    cicids_data = loader.load_cicids()
    print(f"✅ CICIDS: {cicids_data.shape}")
except Exception as e:
    print(f"❌ CICIDS: {e}")
```

---

## 📝 Dataset Information

### NSL-KDD Features (41 total)

**Basic Features:**
- duration, protocol_type, service, flag
- src_bytes, dst_bytes
- land, wrong_fragment, urgent

**Content Features:**
- hot, num_failed_logins, logged_in
- num_compromised, root_shell, su_attempted
- num_root, num_file_creations, num_shells
- num_access_files, num_outbound_cmds

**Time-based Traffic Features:**
- count, srv_count
- serror_rate, srv_serror_rate
- rerror_rate, srv_rerror_rate
- same_srv_rate, diff_srv_rate
- srv_diff_host_rate

**Host-based Traffic Features:**
- dst_host_count, dst_host_srv_count
- dst_host_same_srv_rate, dst_host_diff_srv_rate
- dst_host_same_src_port_rate
- dst_host_srv_diff_host_rate
- dst_host_serror_rate, dst_host_srv_serror_rate
- dst_host_rerror_rate, dst_host_srv_rerror_rate

**Label:**
- label (normal, dos, probe, r2l, u2r)
- difficulty (optional)

### CICIDS 2017 Attack Types

- **Normal**: Benign traffic
- **DoS/DDoS**: Denial of Service attacks
- **PortScan**: Port scanning activities
- **Botnet**: Botnet traffic
- **Infiltration**: Network infiltration
- **Web Attacks**: SQL injection, XSS, etc.
- **Brute Force**: FTP and SSH brute force
- **Heartbleed**: SSL vulnerability exploit

---

## 🔧 Troubleshooting

### Issue: Files Not Found

```bash
# Check current directory
pwd

# Check if files exist
find . -name "*.txt" -o -name "*.csv" | grep -E "(KDD|ISCX)"

# Verify permissions
ls -la data/raw/nsl-kdd/
ls -la data/raw/cicids/
```

### Issue: Download Failed

```bash
# Check internet connection
ping github.com

# Try alternative download method
# Use browser to download, then move files manually

# Check disk space
df -h
```

### Issue: Memory Error (CICIDS)

```python
# Load only specific days
import pandas as pd

# Load in chunks
data = pd.read_csv('data/raw/cicids/Monday-WorkingHours.pcap_ISCX.csv', 
                   nrows=100000)  # Load first 100k rows
```

### Issue: Column Names Mismatch

```python
# CICIDS may have extra spaces in column names
data.columns = data.columns.str.strip()
```

---

## 📊 Dataset Comparison

| Feature | NSL-KDD | CICIDS 2017 | UNSW-NB15 |
|---------|---------|-------------|-----------|
| Size | 150 MB | 7 GB | 2 GB |
| Records | 150K | 2.8M | 2.5M |
| Features | 41 | 78 | 49 |
| Download Time | < 1 min | 10-30 min | 5-15 min |
| Processing Time | Fast | Slow | Medium |
| Difficulty | Beginner | Advanced | Intermediate |
| Recommended | ✅ Yes | ✅ Yes | ⚠️ Optional |

---

## 💡 Recommendations

### For Learning/Testing:
✅ **Start with NSL-KDD**
- Quick to download and process
- Well-documented
- Standard benchmark
- Our system is optimized for it

### For Production/Research:
✅ **Use CICIDS 2017 or 2018**
- More realistic traffic
- Modern attack types
- Comprehensive features
- Better for real-world deployment

### For Quick Demo:
✅ **Use Synthetic Data**
- No download needed
- Instant start
- Run: `python example_usage.py`

---

## ✅ Next Steps After Download

1. **Verify Installation**:
   ```bash
   python verify_installation.py
   ```

2. **Explore Data**:
   ```bash
   jupyter notebook notebooks/exploratory_analysis.ipynb
   ```

3. **Train Models**:
   ```bash
   python -m anomaly_detection.main --mode train --evaluate
   ```

4. **Launch Dashboard**:
   ```bash
   python -m anomaly_detection.main --mode dashboard
   ```

---

## 📞 Need Help?

- Check README.md for general information
- Check QUICKSTART.md for setup instructions
- Run tests: `pytest tests/`
- Verify: `python verify_installation.py`

**Happy anomaly detecting! 🔍🛡️**
