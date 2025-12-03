"""
Main entry point for the Network Anomaly Detection System.
"""

import argparse
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anomaly_detection.utils.config import load_config
from anomaly_detection.utils.logger import LoggerFactory
from anomaly_detection.data_processing.loader import DataLoader
from anomaly_detection.data_processing.preprocessor import DataPreprocessor
from anomaly_detection.data_processing.feature_engineering import FeatureEngineer
from anomaly_detection.training.trainer import ModelTrainer
from anomaly_detection.training.evaluator import ModelEvaluator
from anomaly_detection.visualization.dashboard import AnomalyDashboard
from anomaly_detection.inference.realtime_detector import RealtimeDetector
from anomaly_detection.inference.multi_interface_monitor import MultiInterfaceMonitor
import joblib
import numpy as np
from anomaly_detection.monitoring.automated_monitor import AutomatedMonitor
from anomaly_detection.analysis.pcap_analyzer import PcapAnalyzer


def train_models(config, args):
    """
    Train anomaly detection models.
    
    Args:
        config: Configuration dictionary
        args: Command line arguments
    """
    logger = LoggerFactory.get_logger('Main')
    logger.info("Starting model training pipeline...")
    
    # Load data
    logger.info("Loading dataset...")
    data_loader = DataLoader(config.get('data', {}).get('raw_data_path', 'data/raw'))
    
    try:
        # Try loading NSL-KDD
        train_data, test_data = data_loader.load_nsl_kdd()
        data = train_data
        logger.info(f"Loaded NSL-KDD dataset: {data.shape}")
    except FileNotFoundError:
        logger.warning("NSL-KDD dataset not found. Please download the dataset.")
        logger.info("You can download it from: https://www.unb.ca/cic/datasets/nsl.html")
        return
    
    # Preprocess data
    logger.info("Preprocessing data...")
    preprocessor = DataPreprocessor(
        scaling_method=config.get('features', {}).get('scaling_method', 'standard')
    )
    
    # Assuming 'label' column exists
    label_col = 'label'
    if label_col not in data.columns:
        logger.error(f"Label column '{label_col}' not found in dataset")
        return
    
    X, y, label_mapping = preprocessor.fit_transform(data, label_column=label_col)
    logger.info(f"Preprocessed data shape: {X.shape}")
    logger.info(f"Label distribution: {dict(zip(*np.unique(y, return_counts=True)))}")
    
    # Split data
    X_train, X_val, X_test, y_train, y_val, y_test = data_loader.split_data(
        X, y,
        test_size=config.get('data', {}).get('test_size', 0.2),
        validation_size=config.get('data', {}).get('validation_size', 0.1)
    )
    
    logger.info(f"Train set: {X_train.shape}, Val set: {X_val.shape}, Test set: {X_test.shape}")
    
    # Train models
    logger.info("Training models...")
    trainer = ModelTrainer(config)
    
    if args.model == 'all':
        trainer.train_all_models(X_train, y_train, X_val, y_val)
    else:
        # Train specific model
        if args.model in ['random_forest', 'gradient_boosting', 'svm', 
                         'logistic_regression', 'decision_tree']:
            trainer.train_supervised_model(args.model, X_train, y_train)
        elif args.model in ['isolation_forest', 'kmeans', 'dbscan', 'lof']:
            trainer.train_unsupervised_model(args.model, X_train)
        elif args.model == 'autoencoder':
            trainer.train_autoencoder(X_train, X_val)
        elif args.model == 'dnn':
            trainer.train_dnn(X_train, y_train, X_val, y_val)
    
    logger.info("Training complete!")
    
    # Evaluate models
    if args.evaluate:
        logger.info("Evaluating models...")
        evaluate_models(config, X_test, y_test, trainer)


def evaluate_models(config, X_test, y_test, trainer):
    """
    Evaluate trained models.
    
    Args:
        config: Configuration dictionary
        X_test: Test features
        y_test: Test labels
        trainer: Model trainer instance
    """
    logger = LoggerFactory.get_logger('Main')
    evaluator = ModelEvaluator()
    
    # Evaluate supervised models
    supervised_models = ['random_forest', 'gradient_boosting', 'svm']
    
    for model_name in supervised_models:
        try:
            model = trainer.supervised_models.get_model(model_name)
            if model is not None:
                y_pred = trainer.supervised_models.predict(model_name, X_test)
                y_proba = trainer.supervised_models.predict_proba(model_name, X_test)
                
                metrics = evaluator.evaluate_model(y_test, y_pred, y_proba[:, 1], model_name)
                evaluator.print_evaluation(model_name)
        except Exception as e:
            logger.error(f"Error evaluating {model_name}: {str(e)}")
    
    # Compare models
    comparison_df = evaluator.compare_models()
    print("\nModel Comparison:")
    print(comparison_df.to_string(index=False))
    
    # Get best model
    best_model, best_score = evaluator.get_best_model('f1_score')
    logger.info(f"\nBest Model: {best_model} with F1-Score: {best_score:.4f}")


def run_detection(config, args):
    """
    Run real-time detection.
    
    Args:
        config: Configuration dictionary
        args: Command line arguments
    """
    logger = LoggerFactory.get_logger('Main')
    logger.info("Starting real-time detection...")

    # Load trained model (only supervised example: random_forest)
    model_path = os.path.join(config.get('model_storage', {}).get('save_dir', 'saved_models'), 'supervised', 'random_forest.joblib')
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}. Train the model first.")
        return

    try:
        model = joblib.load(model_path)
        logger.info("Loaded trained random_forest model")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return

    # Fit preprocessor on training data for feature alignment
    data_loader = DataLoader(config.get('data', {}).get('raw_data_path', 'data/raw'))
    try:
        train_data, _ = data_loader.load_nsl_kdd()
    except FileNotFoundError:
        logger.error("NSL-KDD dataset not found for preprocessor fitting.")
        return

    preprocessor = DataPreprocessor(
        scaling_method=config.get('features', {}).get('scaling_method', 'standard')
    )
    X_train, y_train, _ = preprocessor.fit_transform(train_data, label_column='label')
    logger.info(f"Preprocessor fitted on training data shape: {X_train.shape}")

    # Check if multiple interfaces specified
    interfaces = getattr(args, 'interfaces', None)
    interface = args.interface
    backend = getattr(args, 'backend', 'scapy')
    packet_count = getattr(args, 'packet_count', None)
    duration = getattr(args, 'duration', None)
    inject_rate = getattr(args, 'inject_rate', 0.0)
    synthetic_delay = getattr(args, 'synthetic_delay', 0.0)
    
    # Multi-interface mode
    if interfaces:
        interface_list = [iface.strip() for iface in interfaces.split(',')]
        logger.info(f"Multi-interface mode: {', '.join(interface_list)}")
        
        monitor = MultiInterfaceMonitor(
            config=config,
            model=model,
            preprocessor=preprocessor,
            interfaces=interface_list,
            backend=backend
        )
        
        try:
            monitor.start_monitoring(
                packet_count=packet_count,
                duration=duration,
                inject_rate=inject_rate,
                synthetic_delay=synthetic_delay
            )
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        finally:
            monitor.stop_monitoring()
        return
    
    # Single-interface mode
    detector = RealtimeDetector(config, model, preprocessor)

    if packet_count is not None:
        mode_desc = f"packet_count={packet_count}"
    elif duration is not None:
        mode_desc = f"duration={duration}s"
    else:
        mode_desc = "continuous (Ctrl+C to stop)"

    logger.info(f"Interface configured: {interface}")
    logger.info(f"Starting packet capture: backend={backend}, mode={mode_desc}")

    try:
        detector.start_packet_capture(interface=interface, backend=backend, packet_count=packet_count, duration=duration, inject_rate=inject_rate, synthetic_delay=synthetic_delay)
    except Exception as e:
        logger.error(f"Packet capture failed: {e}")
    finally:
        detector.print_statistics()
        detector.close()


def run_dashboard(config, args):
    """
    Run visualization dashboard.
    
    Args:
        config: Configuration dictionary
        args: Command line arguments
    """
    logger = LoggerFactory.get_logger('Main')
    logger.info("Starting dashboard...")
    
    dashboard = AnomalyDashboard(config)
    dashboard.run()


def run_monitoring(config, args):
    """
    Run automated monitoring.
    
    Args:
        config: Configuration dictionary
        args: Command line arguments
    """
    logger = LoggerFactory.get_logger('Main')
    logger.info("Starting automated monitoring...")
    
    monitor = AutomatedMonitor(config)
    monitor.start_monitoring()


def run_pcap_analysis(config, args):
    """
    Analyze PCAP file for anomalies.
    
    Args:
        config: Configuration dictionary
        args: Command line arguments
    """
    logger = LoggerFactory.get_logger('Main')
    logger.info("Starting PCAP analysis...")
    
    if not args.pcap_file:
        logger.error("PCAP file path required. Use --pcap-file <path>")
        return
    
    # Load trained model
    model_path = os.path.join(
        config.get('model_storage', {}).get('save_dir', 'saved_models'),
        'supervised',
        f'{args.model}.joblib'
    )
    
    if not os.path.exists(model_path):
        logger.error(f"Model not found at {model_path}. Train the model first.")
        return
    
    try:
        model = joblib.load(model_path)
        logger.info(f"Loaded trained {args.model} model")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        return
    
    # Fit preprocessor on training data
    data_loader = DataLoader(config.get('data', {}).get('raw_data_path', 'data/raw'))
    try:
        train_data, _ = data_loader.load_nsl_kdd()
    except FileNotFoundError:
        logger.error("NSL-KDD dataset not found for preprocessor fitting.")
        return
    
    preprocessor = DataPreprocessor(
        scaling_method=config.get('features', {}).get('scaling_method', 'standard')
    )
    X_train, y_train, _ = preprocessor.fit_transform(train_data, label_column='label')
    logger.info(f"Preprocessor fitted on training data shape: {X_train.shape}")
    
    # Create analyzer
    analyzer = PcapAnalyzer(
        config=config,
        model=model,
        preprocessor=preprocessor,
        backend=args.backend
    )
    
    try:
        # Analyze PCAP
        results = analyzer.analyze_pcap(
            pcap_path=args.pcap_file,
            packet_filter=args.packet_filter
        )
        
        # Print results
        analyzer.print_statistics()
        
        if results['status'] == 'success':
            logger.info(f"Analysis complete. Found {len(results['detections'])} anomalies.")
        else:
            logger.error(f"Analysis failed: {results.get('error', 'Unknown error')}")
    
    except Exception as e:
        logger.error(f"PCAP analysis failed: {e}")
    finally:
        analyzer.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Network Anomaly Detection System'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['train', 'detect', 'dashboard', 'monitor', 'evaluate', 'pcap'],
        default='train',
        help='Operation mode'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default='all',
        help='Model to train (default: all)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='configs/config.yaml',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--evaluate',
        action='store_true',
        help='Evaluate models after training'
    )
    
    parser.add_argument(
        '--interface',
        type=str,
        default='eth0',
        help='Network interface for real-time detection (single interface)'
    )
    parser.add_argument(
        '--interfaces',
        type=str,
        default=None,
        help='Comma-separated list of network interfaces for multi-interface monitoring (e.g., "wlo1,enp0s25")'
    )
    parser.add_argument(
        '--packet-count',
        type=int,
        default=None,
        help='Number of packets to capture (omit for continuous until Ctrl+C or duration)'
    )
    parser.add_argument(
        '--duration',
        type=int,
        default=None,
        help='Duration in seconds for capture (continuous mode). Ignored if packet-count provided.'
    )
    parser.add_argument(
        '--backend',
        type=str,
        choices=['scapy','pyshark'],
        default='scapy',
        help='Packet capture backend (scapy or pyshark)'
    )
    parser.add_argument(
        '--inject-rate',
        type=float,
        default=0.0,
        help='Fraction (0-1) of synthetic fallback packets to force as anomalies'
    )
    parser.add_argument(
        '--synthetic-delay',
        type=float,
        default=0.0,
        help='Seconds sleep between synthetic fallback packets (throttle)'
    )
    parser.add_argument(
        '--pcap-file',
        type=str,
        default=None,
        help='Path to PCAP file for offline analysis (use with --mode pcap)'
    )
    parser.add_argument(
        '--packet-filter',
        type=str,
        default=None,
        help='BPF-style packet filter (e.g., "tcp port 80" or "icmp")'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Configuration file not found: {args.config}")
        sys.exit(1)
    
    # Setup logging
    log_config = config.get('logging', {})
    logger = LoggerFactory.get_logger(
        'Main',
        log_dir=log_config.get('log_dir', 'logs'),
        level=config.get('monitoring', {}).get('log_level', 'INFO')
    )
    
    logger.info(f"Starting Network Anomaly Detection System in '{args.mode}' mode")
    
    # Route to appropriate function
    if args.mode == 'train':
        train_models(config, args)
    elif args.mode == 'detect':
        run_detection(config, args)
    elif args.mode == 'dashboard':
        run_dashboard(config, args)
    elif args.mode == 'monitor':
        run_monitoring(config, args)
    elif args.mode == 'pcap':
        run_pcap_analysis(config, args)
    elif args.mode == 'evaluate':
        logger.info("Evaluate mode requires trained models")
    
    logger.info("System shutdown complete")


if __name__ == '__main__':
    import numpy as np
    main()