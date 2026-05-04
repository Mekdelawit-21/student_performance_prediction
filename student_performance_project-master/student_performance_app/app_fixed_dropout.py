"""
Student Performance App - Fixed Dropout Prediction
Complete fix for dropout prediction page and API
"""

import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, session, redirect, url_for
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
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
dropout_scaler = None

def train_simple_models():
    """Train simple models for demonstration purposes"""
    global pass_fail_model, score_model, dropout_model
    global pass_fail_scaler, dropout_scaler
    
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
    
    # Train dropout model with exactly 8 features
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

# Main Routes
@app.route('/')
def index():
    """Home page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .navbar-brand i {
            color: white;
            font-size: 2.2rem;
        }
        .navbar-brand {
            color: white !important;
            font-weight: 700;
        }
        .nav-link {
            color: white !important;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
            text-align: center;
        }
        .feature-card {
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .feature-icon {
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open"></i>
                Student Performance Predictor
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/signup">Sign Up</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <h1 class="display-4 fw-bold mb-4">Student Performance Predictor</h1>
            <p class="lead mb-4">Advanced machine learning models to predict academic success and identify at-risk students</p>
            <div class="d-flex justify-content-center gap-3">
                <a href="/login" class="btn btn-light btn-lg">Get Started</a>
                <a href="#features" class="btn btn-outline-light btn-lg">Learn More</a>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Features</h2>
            <div class="row">
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="text-center">
                            <i class="fas fa-check-circle feature-icon"></i>
                            <h4>Pass/Fail Prediction</h4>
                            <p>Predict whether students will pass or fail based on their academic performance</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="text-center">
                            <i class="fas fa-chart-line feature-icon"></i>
                            <h4>Score Prediction</h4>
                            <p>Get accurate predictions of student scores with our advanced ML models</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="feature-card">
                        <div class="text-center">
                            <i class="fas fa-exclamation-triangle feature-icon"></i>
                            <h4>Dropout Risk Analysis</h4>
                            <p>Identify students at risk of dropping out and provide early intervention</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    '''

@app.route('/login')
def login():
    """Login page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - Student Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .auth-body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .auth-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 450px;
            width: 100%;
        }
        .logo-section {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo-section i {
            color: white;
            font-size: 2.2rem;
            margin-bottom: 15px;
        }
        .logo-section h2 {
            color: #333;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px;
            font-weight: 600;
        }
        .auth-link {
            color: #667eea;
            text-decoration: none;
        }
        .auth-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body class="auth-body">
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="logo-section">
                    <i class="fas fa-book-open"></i>
                    <h2>Student Performance Predictor</h2>
                </div>
                <p class="auth-subtitle">Sign in to access your academic dashboard</p>
            </div>

            <form class="auth-form" action="/dashboard" method="post">
                <div class="form-group mb-3">
                    <label for="email" class="form-label">
                        <i class="fas fa-envelope me-2"></i>Email Address
                    </label>
                    <input type="email" class="form-control" id="email" name="email" required 
                           placeholder="Enter your email">
                </div>

                <div class="form-group mb-3">
                    <label for="password" class="form-label">
                        <i class="fas fa-lock me-2"></i>Password
                    </label>
                    <input type="password" class="form-control" id="password" name="password" required 
                           placeholder="Enter your password">
                </div>

                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="remember-me">
                    <label class="form-check-label" for="remember-me">
                        Remember me for 30 days
                    </label>
                </div>

                <button type="submit" class="btn btn-primary w-100 mb-3">
                    <i class="fas fa-sign-in-alt me-2"></i>Sign In
                </button>

                <div class="text-center mb-3">
                    <a href="#" onclick="alert('Password reset coming soon!')" class="auth-link">Forgot your password?</a>
                </div>
            </div>

            <div class="auth-footer">
                <p class="text-center mb-0">
                    Don't have an account? 
                    <a href="/signup" class="auth-link">Sign up here</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/signup')
def signup():
    """Signup page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - Student Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .auth-body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .auth-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        .logo-section {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo-section i {
            color: white;
            font-size: 2.2rem;
            margin-bottom: 15px;
        }
        .logo-section h2 {
            color: #333;
            font-weight: 700;
            margin-bottom: 10px;
        }
        .auth-subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            padding: 12px;
            font-weight: 600;
        }
        .auth-link {
            color: #667eea;
            text-decoration: none;
        }
        .auth-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body class="auth-body">
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <div class="logo-section">
                    <i class="fas fa-book-open"></i>
                    <h2>Join Student Performance Predictor</h2>
                </div>
                <p class="auth-subtitle">Create your account to start predicting academic success</p>
            </div>

            <form class="auth-form" action="/dashboard" method="post">
                <div class="row">
                    <div class="col-md-6">
                        <div class="form-group mb-3">
                            <label for="first-name" class="form-label">
                                <i class="fas fa-user me-2"></i>First Name
                            </label>
                            <input type="text" class="form-control" id="first-name" name="firstName" required 
                                   placeholder="Enter your first name">
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="form-group mb-3">
                            <label for="last-name" class="form-label">
                                <i class="fas fa-user me-2"></i>Last Name
                            </label>
                            <input type="text" class="form-control" id="last-name" name="lastName" required 
                                   placeholder="Enter your last name">
                        </div>
                    </div>
                </div>

                <div class="form-group mb-3">
                    <label for="email" class="form-label">
                        <i class="fas fa-envelope me-2"></i>Email Address
                    </label>
                    <input type="email" class="form-control" id="email" name="email" required 
                           placeholder="Enter your email">
                </div>

                <div class="form-group mb-3">
                    <label for="password" class="form-label">
                        <i class="fas fa-lock me-2"></i>Password
                    </label>
                    <input type="password" class="form-control" id="password" name="password" required 
                           placeholder="Create a strong password">
                </div>

                <div class="form-group mb-3">
                    <label for="role" class="form-label">
                        <i class="fas fa-user-tag me-2"></i>I am a
                    </label>
                    <select class="form-select" id="role" name="role" required>
                        <option value="">Select your role</option>
                        <option value="student">Student</option>
                        <option value="teacher">Teacher</option>
                        <option value="parent">Parent</option>
                        <option value="admin">Administrator</option>
                    </select>
                </div>

                <div class="form-check mb-3">
                    <input class="form-check-input" type="checkbox" id="agree-terms" required>
                    <label class="form-check-label" for="agree-terms">
                        I agree to the <a href="#" class="auth-link">Terms of Service</a> and <a href="#" class="auth-link">Privacy Policy</a>
                    </label>
                </div>

                <button type="submit" class="btn btn-primary w-100 mb-3">
                    <i class="fas fa-user-plus me-2"></i>Create Account
                </button>
            </div>

            <div class="auth-footer">
                <p class="text-center mb-0">
                    Already have an account? 
                    <a href="/login" class="auth-link">Sign in here</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>
    '''

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Student Performance Predictor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .navbar-brand i {
            color: white;
            font-size: 2.2rem;
        }
        .navbar-brand {
            color: white !important;
            font-weight: 700;
        }
        .nav-link {
            color: white !important;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .welcome-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
        }
        .card {
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 10px;
        }
        .border-left-primary {
            border-left: 4px solid #667eea !important;
        }
        .border-left-success {
            border-left: 4px solid #28a745 !important;
        }
        .border-left-info {
            border-left: 4px solid #17a2b8 !important;
        }
        .border-left-warning {
            border-left: 4px solid #ffc107 !important;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open"></i>
                Student Performance Predictor
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pass_fail_page">Pass/Fail</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/score_prediction_page">Score Prediction</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dropout_prediction">Dropout Risk</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/logout">Logout</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid">
        <div class="row">
            <!-- Main content -->
            <main class="col-12 px-md-4">
                <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
                    <h1 class="h2">Dashboard</h1>
                    <div class="btn-toolbar mb-2 mb-md-0">
                        <button type="button" class="btn btn-sm btn-primary" onclick="logout()">
                            <i class="fas fa-sign-out-alt me-1"></i>Logout
                        </button>
                    </div>
                </div>

                <!-- Welcome Card -->
                <div class="welcome-card mb-4">
                    <div class="card-body">
                        <h2 class="card-title">
                            <i class="fas fa-graduation-cap me-2"></i>Welcome to Your Dashboard!
                        </h2>
                        <p class="card-text">Track your academic performance and get personalized predictions to help you succeed.</p>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="row mb-4">
                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-primary shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-primary text-uppercase mb-1">Predictions Made</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">24</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-chart-bar fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-success shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-success text-uppercase mb-1">Success Rate</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">85%</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-check-circle fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-info shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-info text-uppercase mb-1">Avg Score</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">78.5</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-award fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-xl-3 col-md-6 mb-4">
                        <div class="card border-left-warning shadow h-100 py-2">
                            <div class="card-body">
                                <div class="row no-gutters align-items-center">
                                    <div class="col mr-2">
                                        <div class="text-xs font-weight-bold text-warning text-uppercase mb-1">Risk Level</div>
                                        <div class="h5 mb-0 font-weight-bold text-gray-800">Low</div>
                                    </div>
                                    <div class="col-auto">
                                        <i class="fas fa-shield-alt fa-2x text-gray-300"></i>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="row">
                    <div class="col-lg-6 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="m-0 font-weight-bold text-primary">Quick Actions</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-6 mb-3">
                                        <button class="btn btn-primary w-100" onclick="navigateToPrediction('pass_fail')">
                                            <i class="fas fa-check-circle me-2"></i>Pass/Fail Prediction
                                        </button>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <button class="btn btn-success w-100" onclick="navigateToPrediction('score')">
                                            <i class="fas fa-chart-line me-2"></i>Score Prediction
                                        </button>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <button class="btn btn-warning w-100" onclick="navigateToPrediction('dropout')">
                                            <i class="fas fa-exclamation-triangle me-2"></i>Dropout Risk
                                        </button>
                                    </div>
                                    <div class="col-6 mb-3">
                                        <button class="btn btn-info w-100" onclick="showHistory()">
                                            <i class="fas fa-history me-2"></i>View History
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="col-lg-6 mb-4">
                        <div class="card">
                            <div class="card-header">
                                <h6 class="m-0 font-weight-bold text-primary">Recent Activity</h6>
                            </div>
                            <div class="card-body">
                                <div class="list-group list-group-flush">
                                    <div class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fas fa-check-circle text-success me-2"></i>
                                            Pass/Fail Prediction
                                        </div>
                                        <small class="text-muted">2 hours ago</small>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fas fa-chart-line text-primary me-2"></i>
                                            Score Prediction
                                        </div>
                                        <small class="text-muted">5 hours ago</small>
                                    </div>
                                    <div class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                            Dropout Risk Analysis
                                        </div>
                                        <small class="text-muted">1 day ago</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                window.location.href = '/logout';
            }
        }

        function navigateToPrediction(type) {
            switch(type) {
                case 'pass_fail':
                    window.location.href = '/pass_fail_page';
                    break;
                case 'score':
                    window.location.href = '/score_prediction_page';
                    break;
                case 'dropout':
                    window.location.href = '/dropout_prediction';
                    break;
            }
        }

        function showHistory() {
            alert('Prediction history feature coming soon!');
        }
    </script>
</body>
</html>
    '''

@app.route('/logout')
def logout():
    """Logout page"""
    session.clear()
    return redirect(url_for('login'))

# Prediction Pages
@app.route('/pass_fail_page')
def pass_fail_page():
    """Pass/Fail prediction page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pass/Fail Prediction</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .navbar-brand i {
            color: white;
            font-size: 2.2rem;
        }
        .navbar-brand {
            color: white !important;
            font-weight: 700;
        }
        .nav-link {
            color: white !important;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .prediction-form {
            max-width: 600px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .result-card {
            display: none;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open"></i>
                Student Performance Predictor
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/pass_fail_page">Pass/Fail</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/score_prediction_page">Score Prediction</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dropout_prediction">Dropout Risk</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <div class="prediction-form">
            <h2 class="text-center mb-4">
                <i class="fas fa-check-circle me-2"></i>Pass/Fail Prediction
            </h2>
            <form id="predictionForm">
                <div class="mb-3">
                    <label for="study_hours" class="form-label">Study Hours per Day</label>
                    <input type="number" class="form-control" id="study_hours" step="0.1" min="1" max="10" required>
                </div>
                <div class="mb-3">
                    <label for="prev_exam_score" class="form-label">Previous Exam Score</label>
                    <input type="number" class="form-control" id="prev_exam_score" min="0" max="100" required>
                </div>
                <div class="mb-3">
                    <label for="attendance" class="form-label">Attendance Rate</label>
                    <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" required>
                </div>
                <div class="mb-3">
                    <label for="assignment_score" class="form-label">Assignment Score</label>
                    <input type="number" class="form-control" id="assignment_score" min="0" max="100" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Predict</button>
            </form>

            <div id="result" class="result-card">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Prediction Result</h5>
                        <div id="resultContent"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                study_hours: parseFloat(document.getElementById('study_hours').value),
                prev_exam_score: parseFloat(document.getElementById('prev_exam_score').value),
                attendance: parseFloat(document.getElementById('attendance').value),
                assignment_score: parseFloat(document.getElementById('assignment_score').value)
            };

            try {
                const response = await fetch('/api/predict_pass_fail', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');

                if (result.error) {
                    resultContent.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
                } else {
                    resultContent.innerHTML = `
                        <div class="alert alert-success">
                            <h6>Result: ${result.result}</h6>
                            <p>Confidence: ${result.confidence.toFixed(1)}%</p>
                            <p>Pass Probability: ${result.pass_probability.toFixed(1)}%</p>
                            <p>Fail Probability: ${result.fail_probability.toFixed(1)}%</p>
                            ${result.recommendations.length > 0 ? '<h6>Recommendations:</h6><ul>' + result.recommendations.map(r => `<li>${r}</li>`).join('') + '</ul>' : ''}
                        </div>
                    `;
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                document.getElementById('resultContent').innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
                document.getElementById('result').style.display = 'block';
            }
        });
    </script>
</body>
</html>
    '''

@app.route('/score_prediction_page')
def score_prediction_page():
    """Score prediction page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Score Prediction</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .navbar-brand i {
            color: white;
            font-size: 2.2rem;
        }
        .navbar-brand {
            color: white !important;
            font-weight: 700;
        }
        .nav-link {
            color: white !important;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .prediction-form {
            max-width: 600px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .result-card {
            display: none;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open"></i>
                Student Performance Predictor
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pass_fail_page">Pass/Fail</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/score_prediction_page">Score Prediction</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dropout_prediction">Dropout Risk</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <div class="prediction-form">
            <h2 class="text-center mb-4">
                <i class="fas fa-chart-line me-2"></i>Score Prediction
            </h2>
            <form id="predictionForm">
                <div class="mb-3">
                    <label for="study_hours" class="form-label">Study Hours per Day</label>
                    <input type="number" class="form-control" id="study_hours" step="0.1" min="1" max="10" required>
                </div>
                <div class="mb-3">
                    <label for="prev_exam_score" class="form-label">Previous Exam Score</label>
                    <input type="number" class="form-control" id="prev_exam_score" min="0" max="100" required>
                </div>
                <div class="mb-3">
                    <label for="attendance" class="form-label">Attendance Rate</label>
                    <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" required>
                </div>
                <div class="mb-3">
                    <label for="assignment_score" class="form-label">Assignment Score</label>
                    <input type="number" class="form-control" id="assignment_score" min="0" max="100" required>
                </div>
                <button type="submit" class="btn btn-primary w-100">Predict</button>
            </form>

            <div id="result" class="result-card">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Prediction Result</h5>
                        <div id="resultContent"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const data = {
                study_hours: parseFloat(document.getElementById('study_hours').value),
                prev_exam_score: parseFloat(document.getElementById('prev_exam_score').value),
                attendance: parseFloat(document.getElementById('attendance').value),
                assignment_score: parseFloat(document.getElementById('assignment_score').value)
            };

            try {
                const response = await fetch('/api/predict_score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');

                if (result.error) {
                    resultContent.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
                } else {
                    resultContent.innerHTML = `
                        <div class="alert alert-success">
                            <h6>Predicted Score: ${result.predicted_score.toFixed(1)}</h6>
                            <p>Grade: ${result.grade}</p>
                            <p>Performance Level: ${result.performance_level}</p>
                            ${result.recommendations.length > 0 ? '<h6>Recommendations:</h6><ul>' + result.recommendations.map(r => `<li>${r}</li>`).join('') + '</ul>' : ''}
                        </div>
                    `;
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                document.getElementById('resultContent').innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
                document.getElementById('result').style.display = 'block';
            }
        });
    </script>
</body>
</html>
    '''

@app.route('/dropout_prediction')
def dropout_prediction():
    """Dropout prediction page - FIXED VERSION"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dropout Risk Analysis</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        .bg-gradient {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        .navbar-brand i {
            color: white;
            font-size: 2.2rem;
        }
        .navbar-brand {
            color: white !important;
            font-weight: 700;
        }
        .nav-link {
            color: white !important;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .prediction-form {
            max-width: 600px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .result-card {
            display: none;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open"></i>
                Student Performance Predictor
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pass_fail_page">Pass/Fail</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/score_prediction_page">Score Prediction</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active" href="/dropout_prediction">Dropout Risk</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/dashboard">Dashboard</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container my-5">
        <div class="prediction-form">
            <h2 class="text-center mb-4">
                <i class="fas fa-exclamation-triangle me-2"></i>Dropout Risk Analysis
            </h2>
            <form id="predictionForm">
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="age" class="form-label">Age</label>
                        <input type="number" class="form-control" id="age" min="16" max="30" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="gpa" class="form-label">GPA</label>
                        <input type="number" class="form-control" id="gpa" step="0.1" min="0" max="4" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="study_hours" class="form-label">Study Hours per Day</label>
                        <input type="number" class="form-control" id="study_hours" step="0.1" min="0" max="10" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="attendance" class="form-label">Attendance Rate</label>
                        <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="previous_failures" class="form-label">Previous Failures</label>
                        <input type="number" class="form-control" id="previous_failures" min="0" max="10" required>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="work_hours" class="form-label">Work Hours per Week</label>
                        <input type="number" class="form-control" id="work_hours" min="0" max="40" required>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-6 mb-3">
                        <label for="scholarship" class="form-label">Has Scholarship</label>
                        <select class="form-select" id="scholarship" required>
                            <option value="0">No</option>
                            <option value="1">Yes</option>
                        </select>
                    </div>
                    <div class="col-md-6 mb-3">
                        <label for="financial_aid" class="form-label">Has Financial Aid</label>
                        <select class="form-select" id="financial_aid" required>
                            <option value="0">No</option>
                            <option value="1">Yes</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary w-100">Analyze Risk</button>
            </form>

            <div id="result" class="result-card">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Risk Analysis Result</h5>
                        <div id="resultContent"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('predictionForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Ensure exactly 8 features as expected by the model
            const data = {
                age: parseInt(document.getElementById('age').value),
                gpa: parseFloat(document.getElementById('gpa').value),
                study_hours: parseFloat(document.getElementById('study_hours').value),
                attendance: parseFloat(document.getElementById('attendance').value),
                previous_failures: parseInt(document.getElementById('previous_failures').value),
                scholarship: parseInt(document.getElementById('scholarship').value),
                financial_aid: parseInt(document.getElementById('financial_aid').value),
                work_hours: parseInt(document.getElementById('work_hours').value)
            };

            try {
                const response = await fetch('/api/predict_dropout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');

                if (result.error) {
                    resultContent.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
                } else {
                    const alertClass = result.dropout_risk === 'High' ? 'alert-danger' : 'alert-success';
                    resultContent.innerHTML = `
                        <div class="alert ${alertClass}">
                            <h6>Dropout Risk: ${result.dropout_risk}</h6>
                            <p>Confidence: ${result.confidence.toFixed(1)}%</p>
                            <p>Dropout Probability: ${result.dropout_probability.toFixed(1)}%</p>
                            <p>Retention Probability: ${result.retention_probability.toFixed(1)}%</p>
                            ${result.recommendations.length > 0 ? '<h6>Recommendations:</h6><ul>' + result.recommendations.map(r => `<li>${r}</li>`).join('') + '</ul>' : ''}
                        </div>
                    `;
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                document.getElementById('resultContent').innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
                document.getElementById('result').style.display = 'block';
            }
        });
    </script>
</body>
</html>
    '''

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
    """API endpoint for dropout prediction - FIXED VERSION"""
    try:
        data = request.get_json()
        
        # Validate input - exactly 8 features required
        required_fields = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Prepare data - ensure exactly 8 features as expected by the model
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
        if features.shape[1] != 8:
            return jsonify({'error': f'Expected 8 features, got {features.shape[1]}'}), 400
        
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
    print("Starting Student Performance App - Fixed Dropout Prediction Version...")
    print("Login page: http://127.0.0.1:5000/login")
    print("Signup page: http://127.0.0.1:5000/signup")
    print("Dashboard: http://127.0.0.1:5000/dashboard")
    print("Dropout Prediction: http://127.0.0.1:5000/dropout_prediction")
    app.run(debug=True, host='0.0.0.0', port=5000)
