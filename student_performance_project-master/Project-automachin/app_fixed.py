from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import pandas as pd
import os
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models
model = None
scaler = None
explainer = None

def train_models():
    """Train simple models for demonstration"""
    global model, scaler, explainer
    
    try:
        # Generate sample data
        np.random.seed(42)
        n_samples = 1000
        
        # Features for student performance
        features = np.random.randn(n_samples, 8)
        # Target: dropout (1) or not (0)
        target = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(features, target)
        
        # Train scaler
        scaler = StandardScaler()
        scaler.fit(features)
        
        # Save models
        joblib.dump(model, 'model_fixed.joblib')
        joblib.dump(scaler, 'scaler_fixed.joblib')
        
        logger.info("Models trained and saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error training models: {e}")
        return False

def load_models():
    """Load pre-trained models"""
    global model, scaler, explainer
    
    try:
        # Try to load existing models
        if os.path.exists('model_fixed.joblib'):
            model = joblib.load('model_fixed.joblib')
            scaler = joblib.load('scaler_fixed.joblib')
            logger.info("Models loaded successfully")
            return True
        else:
            # Train new models if they don't exist
            return train_models()
    except Exception as e:
        logger.error(f"Error loading models: {e}")
        # Try to train new models
        return train_models()

# Initialize models
load_models()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data from the request
        data = request.json
        
        # Create features from input data
        # Using a simplified feature set for demonstration
        features = np.array([[
            float(data.get('feature1', 0)),
            float(data.get('feature2', 0)),
            float(data.get('feature3', 0)),
            float(data.get('feature4', 0)),
            float(data.get('feature5', 0)),
            float(data.get('feature6', 0)),
            float(data.get('feature7', 0)),
            float(data.get('feature8', 0))
        ]])
        
        # Scale features
        if scaler:
            features_scaled = scaler.transform(features)
        else:
            features_scaled = features
        
        # Make prediction
        if model:
            prediction = model.predict(features_scaled)[0]
            probability = model.predict_proba(features_scaled)[0]
            
            result = {
                'prediction': int(prediction),
                'dropout_risk': 'High' if prediction == 1 else 'Low',
                'confidence': float(max(probability) * 100),
                'probabilities': {
                    'no_dropout': float(probability[0] * 100),
                    'dropout': float(probability[1] * 100)
                }
            }
        else:
            result = {'error': 'Model not loaded properly'}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
