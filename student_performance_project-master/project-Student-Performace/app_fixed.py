from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import os
import logging
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
model = None
scaler = None
explainer = None

def train_models():
    """Train models for student performance prediction"""
    global model, scaler, explainer
    
    try:
        # Generate sample data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: study_hours, prev_exam_score, attendance, assignment_score
        study_hours = np.random.uniform(1, 10, n_samples)
        prev_exam_score = np.random.uniform(0, 100, n_samples)
        attendance = np.random.uniform(0.5, 1.0, n_samples)
        assignment_score = np.random.uniform(0, 100, n_samples)
        
        # Target: final exam score
        final_score = (prev_exam_score * 0.4 + assignment_score * 0.3 + 
                      study_hours * 5 + attendance * 20 + np.random.normal(0, 5, n_samples))
        final_score = np.clip(final_score, 0, 100)
        
        # Create feature matrix
        X = np.column_stack([study_hours, prev_exam_score, attendance, assignment_score])
        
        # Train regression model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, final_score)
        
        # Train scaler
        scaler = StandardScaler()
        scaler.fit(X)
        
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
        
        # Extract features
        study_hours = float(data.get('study_hours', 4))
        prev_exam_score = float(data.get('prev_exam_score', 65))
        attendance = float(data.get('attendance', 0.8))
        assignment_score = float(data.get('assignment_score', 70))
        
        # Create feature array
        features = np.array([[study_hours, prev_exam_score, attendance, assignment_score]])
        
        # Scale features
        if scaler:
            scaled_features = scaler.transform(features)
        else:
            scaled_features = features
        
        # Make prediction
        if model:
            predicted_score = model.predict(scaled_features)[0]
            
            # Determine grade
            if predicted_score >= 90:
                grade = 'A'
            elif predicted_score >= 80:
                grade = 'B'
            elif predicted_score >= 70:
                grade = 'C'
            elif predicted_score >= 60:
                grade = 'D'
            else:
                grade = 'F'
            
            # Performance level
            if predicted_score >= 80:
                performance = 'Excellent'
            elif predicted_score >= 70:
                performance = 'Good'
            elif predicted_score >= 60:
                performance = 'Average'
            else:
                performance = 'Poor'
            
            result = {
                'predicted_score': round(float(predicted_score), 2),
                'grade': grade,
                'performance_level': performance,
                'study_hours': study_hours,
                'prev_exam_score': prev_exam_score
            }
        else:
            result = {'error': 'Model not loaded properly'}
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
