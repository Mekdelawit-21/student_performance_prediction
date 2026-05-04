"""
Feature Diagnostic Tool - Identifies Feature Mismatch Issues
This tool helps identify why the dropout prediction is getting feature mismatch errors
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os

def analyze_feature_mismatch():
    """Analyze the feature mismatch issue in dropout prediction"""
    
    print("=" * 60)
    print("FEATURE MISMATCH DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Current model training (from app_minimal_working.py)
    print("\n1. CURRENT MODEL TRAINING:")
    print("-" * 30)
    
    np.random.seed(42)
    X_dropout = np.random.randn(100, 8)  # 8 features
    y_dropout = np.random.randint(0, 2, 100)
    
    print(f"Training data shape: {X_dropout.shape}")
    print(f"Number of features in training: {X_dropout.shape[1]}")
    print(f"Feature names (should be): age, gpa, study_hours, attendance, previous_failures, scholarship, financial_aid, work_hours")
    
    # Train model
    dropout_model = RandomForestClassifier(n_estimators=10, random_state=42)
    dropout_model.fit(X_dropout, y_dropout)
    dropout_scaler = StandardScaler()
    dropout_scaler.fit(X_dropout)
    
    print(f"Model trained with {X_dropout.shape[1]} features")
    print(f"Model expects: {dropout_model.n_features_in_} features")
    
    # Current API input (from app_minimal_working.py)
    print("\n2. CURRENT API INPUT:")
    print("-" * 30)
    
    # Simulate the data being sent from the frontend
    frontend_data = {
        'age': 20,
        'gpa': 3.2,
        'study_hours': 6.0,
        'attendance': 0.85,
        'previous_failures': 1,
        'scholarship': 1,
        'financial_aid': 0,
        'work_hours': 15
    }
    
    print(f"Frontend sends {len(frontend_data)} features:")
    for i, (key, value) in enumerate(frontend_data.items()):
        print(f"  {i+1}. {key}: {value}")
    
    # Current API processing
    print("\n3. CURRENT API PROCESSING:")
    print("-" * 30)
    
    features = np.array([[
        float(frontend_data['age']),
        float(frontend_data['gpa']),
        float(frontend_data['study_hours']),
        float(frontend_data['attendance']),
        float(frontend_data['previous_failures']),
        float(frontend_data['scholarship']),
        float(frontend_data['financial_aid']),
        float(frontend_data['work_hours'])
    ]])
    
    print(f"API creates features array with shape: {features.shape}")
    print(f"Number of features in API: {features.shape[1]}")
    
    # Test prediction
    print("\n4. PREDICTION TEST:")
    print("-" * 30)
    
    try:
        features_scaled = dropout_scaler.transform(features)
        prediction = dropout_model.predict(features_scaled)[0]
        probabilities = dropout_model.predict_proba(features_scaled)[0]
        
        print("SUCCESS: Prediction works!")
        print(f"Prediction: {prediction}")
        print(f"Probabilities: {probabilities}")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("This is the feature mismatch error!")
    
    # Check for potential issues
    print("\n5. POTENTIAL ISSUES:")
    print("-" * 30)
    
    # Check if there are any extra features being sent
    print("Checking for feature count mismatch...")
    if features.shape[1] != dropout_model.n_features_in_:
        print(f"MISMATCH DETECTED!")
        print(f"  API sends: {features.shape[1]} features")
        print(f"  Model expects: {dropout_model.n_features_in_} features")
    else:
        print("Feature count matches correctly")
    
    # Check for common issues
    print("\nCommon causes of feature mismatch:")
    print("1. Extra features being sent from frontend")
    print("2. Missing features in API processing")
    print("3. Model was trained with different number of features")
    print("4. Data preprocessing adding/removing features")
    
    # Show expected vs actual
    print("\n6. EXPECTED vs ACTUAL:")
    print("-" * 30)
    
    expected_features = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
    actual_features = list(frontend_data.keys())
    
    print("Expected features:")
    for i, feature in enumerate(expected_features):
        print(f"  {i+1}. {feature}")
    
    print("\nActual features from frontend:")
    for i, feature in enumerate(actual_features):
        print(f"  {i+1}. {feature}")
    
    # Check for differences
    if set(expected_features) != set(actual_features):
        print("\nDIFFERENCE DETECTED!")
        missing = set(expected_features) - set(actual_features)
        extra = set(actual_features) - set(expected_features)
        
        if missing:
            print(f"Missing features: {missing}")
        if extra:
            print(f"Extra features: {extra}")
    else:
        print("\nFeature names match correctly")

def create_fixed_api():
    """Create a fixed version of the dropout API"""
    
    print("\n" + "=" * 60)
    print("FIXED API SOLUTION")
    print("=" * 60)
    
    print("\nTo fix the feature mismatch error, ensure:")
    print("1. Frontend sends exactly 8 features")
    print("2. API processes exactly 8 features")
    print("3. Model was trained with exactly 8 features")
    print("4. No extra features are added during processing")
    
    print("\nFixed API code:")
    print("-" * 30)
    
    fixed_api_code = '''
@app.route('/api/predict_dropout', methods=['POST'])
def predict_dropout():
    try:
        data = request.get_json()
        
        # Validate exactly 8 features
        required_features = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        
        # Check for missing features
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            return jsonify({'error': f'Missing features: {missing_features}'}), 400
        
        # Check for extra features
        extra_features = [f for f in data if f not in required_features]
        if extra_features:
            return jsonify({'error': f'Extra features not allowed: {extra_features}'}), 400
        
        # Create features array with exactly 8 features in correct order
        features = np.array([[
            float(data['age']),
            float(data['gpa']),
            float(data['study_hours']),
            float(data['attendance']),
            float(data['previous_failures']),
            float(data['scholarship']),
            float(data['financial_aid']),
            float(data['work_hours'])
        ]])
        
        # Debug: verify feature count
        print(f"DEBUG: Features shape: {features.shape}")
        print(f"DEBUG: Expected: 8, Got: {features.shape[1]}")
        
        if features.shape[1] != 8:
            return jsonify({'error': f'Expected 8 features, got {features.shape[1]}'}), 400
        
        # Scale and predict
        features_scaled = dropout_scaler.transform(features)
        prediction = dropout_model.predict(features_scaled)[0]
        probabilities = dropout_model.predict_proba(features_scaled)[0]
        
        return jsonify({
            'dropout_risk': 'High' if prediction == 1 else 'Low',
            'confidence': float(max(probabilities) * 100),
            'dropout_probability': float(probabilities[1] * 100)
        })
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500
'''
    
    print(fixed_api_code)

if __name__ == '__main__':
    analyze_feature_mismatch()
    create_fixed_api()
