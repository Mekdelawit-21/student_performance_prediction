"""
Student Performance App with Clerk Authentication - Simple Version
No conflicts with middleware
"""

import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')

# Global variables for models
pass_fail_model = None
score_model = None
dropout_model = None
pass_fail_scaler = None
score_scaler = None
dropout_scaler = None

def train_simple_models():
    """Train simple models for demonstration purposes"""
    global pass_fail_model, score_model, dropout_model
    global pass_fail_scaler, score_scaler, dropout_scaler
    
    # Generate sample data for pass/fail prediction
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
    pass_fail_model = RandomForestClassifier(n_estimators=100, random_state=42)
    pass_fail_model.fit(X, pass_fail)
    
    # Train regression model (exact score prediction)
    score_model = RandomForestRegressor(n_estimators=100, random_state=42)
    score_model.fit(X, avg_score)
    
    # Train scaler
    pass_fail_scaler = StandardScaler()
    pass_fail_scaler.fit(X)
    
    # Train dropout model
    dropout_features = np.random.randn(n_samples, 8)
    dropout_labels = np.random.randint(0, 2, n_samples)
    dropout_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dropout_model.fit(dropout_features, dropout_labels)
    
    dropout_scaler = StandardScaler()
    dropout_scaler.fit(dropout_features)
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(pass_fail_model, 'models/pass_fail_model.joblib')
    joblib.dump(score_model, 'models/score_model.joblib')
    joblib.dump(dropout_model, 'models/dropout_model.joblib')
    joblib.dump(pass_fail_scaler, 'models/pass_fail_scaler.joblib')
    joblib.dump(dropout_scaler, 'models/dropout_scaler.joblib')

# Load models
if os.path.exists('models/pass_fail_model.joblib'):
    pass_fail_model = joblib.load('models/pass_fail_model.joblib')
    score_model = joblib.load('models/score_model.joblib')
    dropout_model = joblib.load('models/dropout_model.joblib')
    pass_fail_scaler = joblib.load('models/pass_fail_scaler.joblib')
    dropout_scaler = joblib.load('models/dropout_scaler.joblib')
else:
    train_simple_models()

# Authentication Routes
@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page"""
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    """Logout page"""
    session.clear()
    return redirect(url_for('login'))

# Main App Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/pass_fail_page')
def pass_fail_page():
    """Pass/Fail prediction page"""
    return render_template('pass_fail.html')

@app.route('/score_prediction_page')
def score_prediction_page():
    """Score prediction page"""
    return render_template('score_prediction.html')

@app.route('/dropout_prediction_page')
def dropout_prediction_page():
    """Dropout prediction page"""
    return render_template('dropout_prediction.html')

# API Endpoints
@app.route('/api/predict_pass_fail', methods=['POST'])
def predict_pass_fail():
    """API endpoint for pass/fail prediction"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['study_hours', 'prev_exam_score', 'attendance', 'assignment_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Prepare data
        features = np.array([[
            data['study_hours'],
            data['prev_exam_score'],
            data['attendance'],
            data['assignment_score']
        ]])
        
        # Scale and predict
        features_scaled = pass_fail_scaler.transform(features)
        prediction = pass_fail_model.predict(features_scaled)[0]
        probabilities = pass_fail_model.predict_proba(features_scaled)[0]
        
        # Generate recommendations
        recommendations = []
        if data['study_hours'] < 5:
            recommendations.append("Increase study hours to at least 5 hours per day")
        if data['attendance'] < 0.8:
            recommendations.append("Maintain attendance above 80%")
        if data['assignment_score'] < 70:
            recommendations.append("Focus on improving assignment scores")
        
        result = {
            'prediction': int(prediction),
            'result': 'PASS' if prediction == 1 else 'FAIL',
            'confidence': float(max(probabilities) * 100),
            'pass_probability': float(probabilities[1] * 100),
            'fail_probability': float(probabilities[0] * 100),
            'recommendations': recommendations
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/api/predict_score', methods=['POST'])
def predict_score():
    """API endpoint for score prediction"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['study_hours', 'prev_exam_score', 'attendance', 'assignment_score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Prepare data
        features = np.array([[
            data['study_hours'],
            data['prev_exam_score'],
            data['attendance'],
            data['assignment_score']
        ]])
        
        # Scale and predict
        features_scaled = pass_fail_scaler.transform(features)
        prediction = score_model.predict(features_scaled)[0]
        
        # Determine grade and performance level
        if prediction >= 90:
            grade = 'A'
            performance = 'Excellent'
        elif prediction >= 80:
            grade = 'B'
            performance = 'Good'
        elif prediction >= 70:
            grade = 'C'
            performance = 'Average'
        elif prediction >= 60:
            grade = 'D'
            performance = 'Below Average'
        else:
            grade = 'F'
            performance = 'Poor'
        
        # Generate recommendations
        recommendations = []
        if prediction < 70:
            recommendations.append("Consider additional study time")
            recommendations.append("Seek help from teachers or tutors")
        if data['study_hours'] < 6:
            recommendations.append("Increase daily study hours")
        if data['attendance'] < 0.9:
            recommendations.append("Improve class attendance")
        
        result = {
            'predicted_score': float(prediction),
            'grade': grade,
            'performance_level': performance,
            'recommendations': recommendations
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/api/predict_dropout', methods=['POST'])
def predict_dropout():
    """API endpoint for dropout prediction"""
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Prepare data
        features = np.array([[
            data['age'],
            data['gpa'],
            data['study_hours'],
            data['attendance'],
            data['previous_failures'],
            data['scholarship'],
            data['financial_aid'],
            data['work_hours']
        ]])
        
        # Scale and predict
        features_scaled = dropout_scaler.transform(features)
        prediction = dropout_model.predict(features_scaled)[0]
        probabilities = dropout_model.predict_proba(features_scaled)[0]
        
        # Generate recommendations
        recommendations = []
        if data['gpa'] < 2.5:
            recommendations.append("Focus on improving GPA through tutoring")
        if data['attendance'] < 0.8:
            recommendations.append("Maintain regular class attendance")
        if data['work_hours'] > 20:
            recommendations.append("Consider reducing work hours")
        if data['scholarship'] == 0 and data['financial_aid'] == 0:
            recommendations.append("Apply for financial aid or scholarships")
        
        result = {
            'prediction': int(prediction),
            'dropout_risk': 'High' if prediction == 1 else 'Low',
            'confidence': float(max(probabilities) * 100),
            'dropout_probability': float(probabilities[1] * 100),
            'retention_probability': float(probabilities[0] * 100),
            'recommendations': recommendations
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Student Performance App with Clerk Authentication...")
    print(f"Clerk Publishable Key: {os.getenv('CLERK_PUBLISHABLE_KEY', 'Not set')}")
    print("Login page: http://127.0.0.1:5000/login")
    print("Signup page: http://127.0.0.1:5000/signup")
    print("Dashboard: http://127.0.0.1:5000/dashboard")
    app.run(debug=True, host='0.0.0.0', port=5000)
