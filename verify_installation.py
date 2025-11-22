#!/usr/bin/env python
"""
Installation verification script.
Run this to verify that the Network Anomaly Detection System is properly installed.
"""

import sys
import importlib


def check_module(module_name, display_name=None):
    """Check if a module can be imported."""
    if display_name is None:
        display_name = module_name
    
    try:
        importlib.import_module(module_name)
        print(f"✅ {display_name}")
        return True
    except ImportError as e:
        print(f"❌ {display_name} - {str(e)}")
        return False


def verify_installation():
    """Verify installation of all components."""
    print("\n" + "="*60)
    print("Network Anomaly Detection System - Installation Verification")
    print("="*60 + "\n")
    
    all_ok = True
    
    # Core dependencies
    print("Checking Core Dependencies:")
    print("-" * 40)
    deps = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('sklearn', 'Scikit-learn'),
        ('tensorflow', 'TensorFlow'),
        ('matplotlib', 'Matplotlib'),
        ('seaborn', 'Seaborn'),
        ('plotly', 'Plotly'),
        ('dash', 'Dash'),
        ('yaml', 'PyYAML'),
    ]
    
    for module, name in deps:
        if not check_module(module, name):
            all_ok = False
    
    print()
    
    # Project modules
    print("Checking Project Modules:")
    print("-" * 40)
    modules = [
        ('anomaly_detection', 'Main Package'),
        ('anomaly_detection.utils.config', 'Configuration'),
        ('anomaly_detection.utils.logger', 'Logger'),
        ('anomaly_detection.data_processing.loader', 'Data Loader'),
        ('anomaly_detection.data_processing.preprocessor', 'Preprocessor'),
        ('anomaly_detection.data_processing.feature_engineering', 'Feature Engineering'),
        ('anomaly_detection.models.supervised_models', 'Supervised Models'),
        ('anomaly_detection.models.unsupervised_models', 'Unsupervised Models'),
        ('anomaly_detection.models.neural_networks', 'Neural Networks'),
        ('anomaly_detection.training.trainer', 'Trainer'),
        ('anomaly_detection.training.evaluator', 'Evaluator'),
        ('anomaly_detection.inference.realtime_detector', 'Real-time Detector'),
        ('anomaly_detection.inference.alert_manager', 'Alert Manager'),
        ('anomaly_detection.visualization.plotter', 'Plotter'),
        ('anomaly_detection.visualization.dashboard', 'Dashboard'),
        ('anomaly_detection.monitoring.automated_monitor', 'Monitor'),
    ]
    
    for module, name in modules:
        if not check_module(module, name):
            all_ok = False
    
    print()
    
    # Check configuration file
    print("Checking Configuration:")
    print("-" * 40)
    import os
    config_path = 'configs/config.yaml'
    if os.path.exists(config_path):
        print(f"✅ Configuration file found: {config_path}")
    else:
        print(f"❌ Configuration file not found: {config_path}")
        all_ok = False
    
    print()
    
    # Summary
    print("="*60)
    if all_ok:
        print("✅ All checks passed! Installation is complete.")
        print("\nNext steps:")
        print("1. Read QUICKSTART.md for usage instructions")
        print("2. Run: python example_usage.py")
        print("3. Try: python -m anomaly_detection.main --mode train")
    else:
        print("❌ Some checks failed. Please install missing dependencies:")
        print("\n  pip install -r requirements.txt")
        print("  pip install -e .")
    print("="*60 + "\n")
    
    return all_ok


def test_basic_functionality():
    """Test basic functionality."""
    print("\n" + "="*60)
    print("Testing Basic Functionality")
    print("="*60 + "\n")
    
    try:
        print("Testing configuration loading...")
        from anomaly_detection.utils.config import load_config
        config = load_config('configs/config.yaml')
        print(f"✅ Configuration loaded: {len(config)} sections")
        
        print("\nTesting preprocessor...")
        from anomaly_detection.data_processing.preprocessor import DataPreprocessor
        preprocessor = DataPreprocessor()
        print("✅ Preprocessor initialized")
        
        print("\nTesting supervised models...")
        from anomaly_detection.models.supervised_models import SupervisedModels
        models = SupervisedModels({})
        print(f"✅ Supervised models initialized: {len(models.models)} models")
        
        print("\nTesting unsupervised models...")
        from anomaly_detection.models.unsupervised_models import UnsupervisedModels
        models = UnsupervisedModels({})
        print(f"✅ Unsupervised models initialized: {len(models.models)} models")
        
        print("\n" + "="*60)
        print("✅ Basic functionality tests passed!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test failed: {str(e)}")
        print("="*60 + "\n")
        return False


def main():
    """Main verification function."""
    # Change to project directory if needed
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Verify installation
    install_ok = verify_installation()
    
    if install_ok:
        # Test basic functionality
        func_ok = test_basic_functionality()
        
        if func_ok:
            print("\n🎉 System is ready to use! 🎉\n")
            return 0
        else:
            print("\n⚠️  Installation complete but functionality tests failed.\n")
            return 1
    else:
        print("\n⚠️  Installation incomplete. Please install missing dependencies.\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
