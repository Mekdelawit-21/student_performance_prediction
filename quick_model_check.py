#!/usr/bin/env python3
"""
Quick Model File Checker
Usage: python quick_model_check.py <model_file_path>
"""

import sys
import os
import joblib
import pickle
import json
from pathlib import Path

def check_model_file(file_path):
    """Quick check of a model file"""
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"File not found: {file_path}")
            return
        
        print(f"Checking: {file_path}")
        print(f"Size: {file_path.stat().st_size / 1024:.2f} KB")
        print(f"Modified: {file_path.stat().st_mtime}")
        
        # Try to load the file
        try:
            data = joblib.load(file_path)
            print("Loaded with joblib")
        except:
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                print("Loaded with pickle")
            except Exception as e:
                print(f"Error loading: {e}")
                return
        
        # Basic info
        print(f"Type: {type(data).__name__}")
        
        if hasattr(data, '__dict__'):
            print(f"Module: {type(data).__module__}")
            
            # Common ML model attributes
            attrs = ['n_features_', 'n_classes_', 'feature_importances_', 'coef_', 'intercept_']
            for attr in attrs:
                if hasattr(data, attr):
                    value = getattr(data, attr)
                    print(f"  {attr}: {value}")
        
        elif isinstance(data, dict):
            print(f"Dictionary with {len(data)} keys")
            for key, value in list(data.items())[:5]:  # Show first 5
                print(f"  {key}: {type(value).__name__}")
            if len(data) > 5:
                print(f"  ... and {len(data) - 5} more items")
        
        elif isinstance(data, (list, tuple)):
            print(f"{type(data).__name__} with {len(data)} items")
            if len(data) > 0:
                print(f"  First item: {type(data[0]).__name__}")
        
        print("Check completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python quick_model_check.py <model_file_path>")
        print("\nExample:")
        print("  python quick_model_check.py models/classification_model.joblib")
        print("  python quick_model_check.py dropout_model_simple.joblib")
        return
    
    file_path = sys.argv[1]
    check_model_file(file_path)

if __name__ == "__main__":
    main()
