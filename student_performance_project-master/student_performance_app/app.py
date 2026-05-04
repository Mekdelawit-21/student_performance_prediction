from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Explicitly set template and static folders to avoid conflicts with other projects
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Configure Flask to not search parent directories
app.config['EXPLAIN_TEMPLATE_LOADING'] = True

# Global variables for models and scalers
classification_model = None
regression_model = None
scaler = None
dropout_model = None

def train_simple_models():
    """Train simple models for demonstration purposes"""
    global classification_model, regression_model, scaler, dropout_model
    
    # Generate sample data for simple pass/fail prediction
    np.random.seed(42)
    n_samples = 1000
    
    # Features: study_hours, prev_exam_score, attendance, assignment_score
    study_hours = np.random.uniform(1, 10, n_samples)
    prev_exam_score = np.random.uniform(0, 100, n_samples)
    attendance = np.random.uniform(0.5, 1.0, n_samples)
    assignment_score = np.random.uniform(0, 100, n_samples)
    
    # Target: pass/fail (1 if average score > 60, else 0)
    avg_score = (prev_exam_score + assignment_score) / 2
    pass_fail = (avg_score > 60).astype(int)
    
    # Create feature matrix
    X = np.column_stack([study_hours, prev_exam_score, attendance, assignment_score])
    
    # Train classification model (pass/fail)
    classification_model = RandomForestClassifier(n_estimators=100, random_state=42)
    classification_model.fit(X, pass_fail)
    
    # Train regression model (exact score prediction)
    regression_model = RandomForestRegressor(n_estimators=100, random_state=42)
    regression_model.fit(X, avg_score)
    
    # Train scaler
    scaler = StandardScaler()
    scaler.fit(X)
    
    # Generate sample data for dropout prediction using same 4 features
    dropout_target = ((avg_score < 50) & (attendance < 0.7)).astype(int)  # Dropout if low score and attendance
    
    dropout_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dropout_model.fit(X, dropout_target)
    
    # Save the models
    joblib.dump(classification_model, 'models/classification_model.joblib')
    joblib.dump(regression_model, 'models/regression_model.joblib')
    joblib.dump(scaler, 'models/scaler.joblib')
    joblib.dump(dropout_model, 'models/dropout_model.joblib')

def load_models():
    """Load pre-trained models"""
    global classification_model, regression_model, scaler, dropout_model
    
    try:
        classification_model = joblib.load('models/classification_model.joblib')
        regression_model = joblib.load('models/regression_model.joblib')
        scaler = joblib.load('models/scaler.joblib')
        dropout_model = joblib.load('models/dropout_model.joblib')
        return True
    except:
        return False

# Initialize models
if not load_models():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    train_simple_models()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/pass_fail')
def pass_fail_page():
    return render_template('pass_fail.html')

@app.route('/score_prediction')
def score_prediction_page():
    return render_template('score_prediction.html')

@app.route('/dropout_prediction')
def dropout_prediction_page():
    return render_template('dropout_prediction.html')

@app.route('/predict_pass_fail', methods=['POST'])
def predict_pass_fail():
    try:
        data = request.json
        
        # Extract features
        study_hours = float(data['study_hours'])
        prev_exam_score = float(data['prev_exam_score'])
        attendance = float(data.get('attendance', 0.8))
        assignment_score = float(data.get('assignment_score', 70))
        
        # Create feature array
        features = np.array([[study_hours, prev_exam_score, attendance, assignment_score]])
        
        # Make prediction
        prediction = classification_model.predict(features)[0]
        probability = classification_model.predict_proba(features)[0]
        
        result = {
            'prediction': 'Pass' if prediction == 1 else 'Fail',
            'confidence': float(max(probability) * 100),
            'pass_probability': float(probability[1] * 100),
            'fail_probability': float(probability[0] * 100)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/predict_score', methods=['POST'])
def predict_score():
    try:
        data = request.json
        
        # Extract features
        study_hours = float(data['study_hours'])
        prev_exam_score = float(data['prev_exam_score'])
        attendance = float(data.get('attendance', 0.8))
        assignment_score = float(data.get('assignment_score', 70))
        
        # Create feature array
        features = np.array([[study_hours, prev_exam_score, attendance, assignment_score]])
        
        # Make prediction
        predicted_score = regression_model.predict(features)[0]
        
        result = {
            'predicted_score': round(float(predicted_score), 2),
            'grade': get_grade(predicted_score),
            'performance_level': get_performance_level(predicted_score)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/predict_dropout', methods=['POST'])
def predict_dropout():
    try:
        data = request.json
        
        # For dropout prediction, we'll use the same 4 features as other models
        # In a real application, this would use the actual dropout dataset features
        study_hours = float(data.get('study_hours', 15))
        prev_exam_score = float(data.get('prev_exam_score', 62.5))
        attendance = float(data.get('attendance', 0.75))
        assignment_score = float(data.get('assignment_score', 70))
        
        # Create feature array with 4 features (matching the model)
        features = np.array([[study_hours, prev_exam_score, attendance, assignment_score]])
        
        # Make prediction
        prediction = dropout_model.predict(features)[0]
        probability = dropout_model.predict_proba(features)[0]
        
        result = {
            'prediction': 'High Risk' if prediction == 1 else 'Low Risk',
            'dropout_risk': 'High' if prediction == 1 else 'Low',
            'confidence': float(max(probability) * 100),
            'dropout_probability': float(probability[1] * 100),
            'retention_probability': float(probability[0] * 100)
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)})

def get_grade(score):
    """Convert numerical score to letter grade"""
    if score >= 90:
        return 'A'
    elif score >= 80:
        return 'B'
    elif score >= 70:
        return 'C'
    elif score >= 60:
        return 'D'
    else:
        return 'F'

def get_performance_level(score):
    """Get performance level based on score"""
    if score >= 80:
        return 'Excellent'
    elif score >= 70:
        return 'Good'
    elif score >= 60:
        return 'Average'
    elif score >= 50:
        return 'Below Average'
    else:
        return 'Poor'

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
