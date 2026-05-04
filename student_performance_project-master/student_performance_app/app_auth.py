"""
Student Performance App with Clerk.com Authentication
Secure login and signup functionality
"""

import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename
from auth_middleware import ClerkAuth, login_required, SessionManager, api_auth_required
from functools import wraps

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CLERK_PUBLISHABLE_KEY'] = os.getenv('CLERK_PUBLISHABLE_KEY', 'pk_test_your-key-here')
app.config['CLERK_SECRET_KEY'] = os.getenv('CLERK_SECRET_KEY', 'sk_test_your-key-here')

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize Clerk Authentication
clerk_auth = ClerkAuth(
    app,
    publishable_key=app.config['CLERK_PUBLISHABLE_KEY'],
    secret_key=app.config['CLERK_SECRET_KEY']
)

# Global variables for models
pass_fail_model = None
score_model = None
dropout_model = None
pass_fail_scaler = None
score_scaler = None
dropout_scaler = None

def train_models():
    """Train all models if they don't exist"""
    global pass_fail_model, score_model, dropout_model
    global pass_fail_scaler, score_scaler, dropout_scaler
    
    try:
        # Train Pass/Fail Model
        if not os.path.exists('models/pass_fail_model.joblib'):
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import StandardScaler
            from sklearn.model_selection import train_test_split
            
            np.random.seed(42)
            n_samples = 1000
            
            data = {
                'study_hours': np.random.uniform(1, 10, n_samples),
                'prev_exam_score': np.random.uniform(30, 100, n_samples),
                'attendance': np.random.uniform(0.5, 1.0, n_samples),
                'assignment_score': np.random.uniform(40, 100, n_samples)
            }
            
            df = pd.DataFrame(data)
            pass_fail_prob = (
                (df['study_hours'] < 3) * 0.3 +
                (df['prev_exam_score'] < 50) * 0.3 +
                (df['attendance'] < 0.7) * 0.2 +
                (df['assignment_score'] < 60) * 0.2 +
                np.random.random(n_samples) * 0.1
            )
            df['pass_fail'] = (pass_fail_prob > 0.5).astype(int)
            
            X = df[['study_hours', 'prev_exam_score', 'attendance', 'assignment_score']]
            y = df['pass_fail']
            
            pass_fail_scaler = StandardScaler()
            X_scaled = pass_fail_scaler.fit_transform(X)
            
            pass_fail_model = RandomForestClassifier(n_estimators=100, random_state=42)
            pass_fail_model.fit(X_scaled, y)
            
            os.makedirs('models', exist_ok=True)
            joblib.dump(pass_fail_model, 'models/pass_fail_model.joblib')
            joblib.dump(pass_fail_scaler, 'models/pass_fail_scaler.joblib')
        else:
            pass_fail_model = joblib.load('models/pass_fail_model.joblib')
            pass_fail_scaler = joblib.load('models/pass_fail_scaler.joblib')
        
        # Train Score Model
        if not os.path.exists('models/score_model.joblib'):
            from sklearn.ensemble import RandomForestRegressor
            
            np.random.seed(42)
            n_samples = 1000
            
            data = {
                'study_hours': np.random.uniform(1, 10, n_samples),
                'prev_exam_score': np.random.uniform(30, 100, n_samples),
                'attendance': np.random.uniform(0.5, 1.0, n_samples),
                'assignment_score': np.random.uniform(40, 100, n_samples)
            }
            
            df = pd.DataFrame(data)
            df['score'] = (
                df['study_hours'] * 5 +
                df['prev_exam_score'] * 0.6 +
                df['attendance'] * 20 +
                df['assignment_score'] * 0.3 +
                np.random.normal(0, 5, n_samples)
            ).clip(0, 100)
            
            X = df[['study_hours', 'prev_exam_score', 'attendance', 'assignment_score']]
            y = df['score']
            
            score_scaler = StandardScaler()
            X_scaled = score_scaler.fit_transform(X)
            
            score_model = RandomForestRegressor(n_estimators=100, random_state=42)
            score_model.fit(X_scaled, y)
            
            joblib.dump(score_model, 'models/score_model.joblib')
            joblib.dump(score_scaler, 'models/score_scaler.joblib')
        else:
            score_model = joblib.load('models/score_model.joblib')
            score_scaler = joblib.load('models/score_scaler.joblib')
        
        # Train Dropout Model
        if not os.path.exists('models/dropout_model.joblib'):
            np.random.seed(42)
            n_samples = 1000
            
            data = {
                'age': np.random.randint(17, 30, n_samples),
                'gpa': np.random.uniform(2.0, 4.0, n_samples),
                'study_hours': np.random.uniform(1, 10, n_samples),
                'attendance': np.random.uniform(0.5, 1.0, n_samples),
                'previous_failures': np.random.randint(0, 5, n_samples),
                'scholarship': np.random.randint(0, 2, n_samples),
                'financial_aid': np.random.randint(0, 2, n_samples),
                'work_hours': np.random.randint(0, 40, n_samples)
            }
            
            df = pd.DataFrame(data)
            dropout_prob = (
                (df['gpa'] < 2.5) * 0.3 +
                (df['attendance'] < 0.7) * 0.2 +
                (df['previous_failures'] > 2) * 0.25 +
                (df['work_hours'] > 20) * 0.15 +
                np.random.random(n_samples) * 0.1
            )
            df['dropout'] = (dropout_prob > 0.5).astype(int)
            
            feature_columns = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
            X = df[feature_columns]
            y = df['dropout']
            
            dropout_scaler = StandardScaler()
            X_scaled = dropout_scaler.fit_transform(X)
            
            dropout_model = RandomForestClassifier(n_estimators=100, random_state=42)
            dropout_model.fit(X_scaled, y)
            
            joblib.dump(dropout_model, 'models/dropout_model.joblib')
            joblib.dump(dropout_scaler, 'models/dropout_scaler.joblib')
        else:
            dropout_model = joblib.load('models/dropout_model.joblib')
            dropout_scaler = joblib.load('models/dropout_scaler.joblib')
            
        print("All models loaded/trained successfully!")
        return True
        
    except Exception as e:
        print(f"Error training models: {e}")
        return False

# Load models on startup
train_models()

# Authentication Routes
@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page"""
    return render_template('signup.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Logout route"""
    SessionManager.destroy_session()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user = clerk_auth.get_current_user()
    return render_template('dashboard.html', user=user)

# Protected Routes
@app.route('/')
def index():
    """Home page - redirect to dashboard if authenticated"""
    if clerk_auth.is_authenticated():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/pass_fail')
@login_required
def pass_fail():
    """Pass/Fail prediction page"""
    return render_template('pass_fail.html')

@app.route('/score_prediction')
@login_required
def score_prediction():
    """Score prediction page"""
    return render_template('score_prediction.html')

@app.route('/dropout_prediction')
@login_required
def dropout_prediction():
    """Dropout prediction page"""
    return render_template('dropout_prediction.html')

@app.route('/history')
@login_required
def history():
    """Prediction history page"""
    return render_template('history.html')

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = clerk_auth.get_current_user()
    return render_template('profile.html', user=user)

@app.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')

# API Endpoints
@app.route('/api/predict_pass_fail', methods=['POST'])
@api_auth_required
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
            'recommendations': recommendations,
            'user_id': request.user.get('id'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/api/predict_score', methods=['POST'])
@api_auth_required
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
        features_scaled = score_scaler.transform(features)
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
            'recommendations': recommendations,
            'user_id': request.user.get('id'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

@app.route('/api/predict_dropout', methods=['POST'])
@api_auth_required
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
            'recommendations': recommendations,
            'user_id': request.user.get('id'),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'Prediction error: {str(e)}'}), 500

# Utility Routes
@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': pd.Timestamp.now().isoformat()})

if __name__ == '__main__':
    print("Starting Student Performance App with Clerk Authentication...")
    print(f"Clerk Publishable Key: {app.config['CLERK_PUBLISHABLE_KEY'][:20]}...")
    app.run(debug=True, host='0.0.0.0', port=5000)
