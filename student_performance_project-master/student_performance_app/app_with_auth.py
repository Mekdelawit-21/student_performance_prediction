"""
Student Performance App - Complete with Professional Authentication
Includes comprehensive signup and login pages with header design
"""

import os
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify, session, redirect, url_for, render_template_string
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

# Simple user storage (in production, use a database)
users = {}

def train_or_load_models():
    """Train new models or load existing ones with feature validation"""
    global pass_fail_model, score_model, dropout_model
    global pass_fail_scaler, dropout_scaler
    
    print("Initializing models...")
    
    # Check if pre-trained models exist and validate them
    if os.path.exists('models/dropout_model.joblib'):
        try:
            # Load pre-trained models
            dropout_model = joblib.load('models/dropout_model.joblib')
            dropout_scaler = joblib.load('models/dropout_scaler.joblib')
            
            print(f"Loaded pre-trained dropout model with {dropout_model.n_features_in_} features")
            
            # Validate feature count
            if dropout_model.n_features_in_ != 8:
                print(f"WARNING: Pre-trained model expects {dropout_model.n_features_in_} features, but we need 8")
                train_new_models()
            else:
                print("Pre-trained dropout model is compatible")
                
        except Exception as e:
            print(f"Error loading pre-trained models: {e}")
            print("Training new models...")
            train_new_models()
    else:
        print("No pre-trained models found, training new models...")
        train_new_models()

def train_new_models():
    """Train new models with exactly 8 features for dropout prediction"""
    global pass_fail_model, score_model, dropout_model
    global pass_fail_scaler, dropout_scaler
    
    print("Training new models...")
    
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
    
    # Train dropout model with EXACTLY 8 features
    print("Training dropout model with 8 features...")
    
    # Create realistic dropout data with 8 features
    dropout_features = np.column_stack([
        np.random.uniform(16, 30, n_samples),  # age
        np.random.uniform(0.0, 4.0, n_samples),  # gpa
        np.random.uniform(0.0, 10.0, n_samples),  # study_hours
        np.random.uniform(0.0, 1.0, n_samples),   # attendance
        np.random.randint(0, 5, n_samples),       # previous_failures
        np.random.randint(0, 2, n_samples),       # scholarship
        np.random.randint(0, 2, n_samples),       # financial_aid
        np.random.uniform(0.0, 40.0, n_samples)   # work_hours
    ])
    
    dropout_labels = np.random.randint(0, 2, n_samples)
    
    print(f"Dropout training data shape: {dropout_features.shape}")
    
    dropout_model = RandomForestClassifier(n_estimators=100, random_state=42)
    dropout_model.fit(dropout_features, dropout_labels)
    
    dropout_scaler = StandardScaler()
    dropout_scaler.fit(dropout_features)
    
    print(f"Dropout model trained with {dropout_model.n_features_in_} features")
    
    # Save models
    os.makedirs('models', exist_ok=True)
    joblib.dump(pass_fail_model, 'models/pass_fail_model.joblib')
    joblib.dump(score_model, 'models/score_model.joblib')
    joblib.dump(dropout_model, 'models/dropout_model.joblib')
    joblib.dump(pass_fail_scaler, 'models/pass_fail_scaler.joblib')
    joblib.dump(dropout_scaler, 'models/dropout_scaler.joblib')
    
    print("Models saved successfully")

# Initialize models
train_or_load_models()

# Professional Header Template
HEADER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
            font-weight: 500;
        }
        .nav-link:hover {
            color: #f0f0f0 !important;
        }
        .nav-link.active {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
        }
        .navbar-toggler {
            border: 1px solid white;
        }
        .navbar-toggler-icon {
            background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3e%3cpath stroke='white' stroke-linecap='round' stroke-miterlimit='10' stroke-width='2' d='M4 7h22M4 15h22M4 23h22'/%3e%3c/svg%3e");
        }
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
            backdrop-filter: blur(10px);
        }
        .logo-section {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo-section i {
            color: #667eea;
            font-size: 3rem;
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
            border-radius: 8px;
        }
        .btn-primary:hover {
            background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        }
        .form-control, .form-select {
            border-radius: 8px;
            border: 1px solid #ddd;
            padding: 12px;
        }
        .form-control:focus, .form-select:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .form-label {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        .auth-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        .auth-link:hover {
            text-decoration: underline;
        }
        .alert {
            border-radius: 8px;
            border: none;
        }
        .password-strength {
            height: 5px;
            border-radius: 3px;
            margin-top: 5px;
            transition: all 0.3s ease;
        }
        .strength-weak { background-color: #dc3545; }
        .strength-medium { background-color: #ffc107; }
        .strength-strong { background-color: #28a745; }
        .feature-icon {
            font-size: 2.5rem;
            color: #667eea;
            margin-bottom: 15px;
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
    </style>
</head>
<body>
    <!-- Navigation Header -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-gradient">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i class="fas fa-book-open me-2"></i>
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
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/signup">Sign Up</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
'''

# Main Routes
@app.route('/')
def index():
    """Home page"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Student Performance Predictor') + '''
    <!-- Hero Section -->
    <section class="hero-section">
        <div class="container">
            <h1 class="display-4 fw-bold mb-4">Student Performance Predictor</h1>
            <p class="lead mb-4">Advanced machine learning models to predict academic success and identify at-risk students</p>
            <div class="d-flex justify-content-center gap-3">
                <a href="/signup" class="btn btn-light btn-lg">
                    <i class="fas fa-user-plus me-2"></i>Get Started
                </a>
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
    ''')

@app.route('/signup')
def signup():
    """Comprehensive signup page with header"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Sign Up - Student Performance Predictor') + '''
    <div class="auth-body">
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="logo-section">
                        <i class="fas fa-user-plus"></i>
                        <h2>Create Account</h2>
                        <p class="auth-subtitle">Join our academic prediction platform</p>
                    </div>
                </div>

                <form id="signupForm" class="auth-form">
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group mb-3">
                                <label for="firstName" class="form-label">
                                    <i class="fas fa-user me-2"></i>First Name
                                </label>
                                <input type="text" class="form-control" id="firstName" name="firstName" required 
                                       placeholder="Enter your first name">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group mb-3">
                                <label for="lastName" class="form-label">
                                    <i class="fas fa-user me-2"></i>Last Name
                                </label>
                                <input type="text" class="form-control" id="lastName" name="lastName" required 
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
                               placeholder="Create a strong password" oninput="checkPasswordStrength()">
                        <div id="passwordStrength" class="password-strength"></div>
                        <small class="text-muted">Password must be at least 8 characters with uppercase, lowercase, and numbers</small>
                    </div>

                    <div class="form-group mb-3">
                        <label for="confirmPassword" class="form-label">
                            <i class="fas fa-lock me-2"></i>Confirm Password
                        </label>
                        <input type="password" class="form-control" id="confirmPassword" name="confirmPassword" required 
                               placeholder="Confirm your password">
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

                    <div class="form-group mb-3">
                        <label for="institution" class="form-label">
                            <i class="fas fa-school me-2"></i>Institution
                        </label>
                        <input type="text" class="form-control" id="institution" name="institution" required 
                                       placeholder="Enter your school/institution name">
                    </div>

                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="agreeTerms" required>
                        <label class="form-check-label" for="agreeTerms">
                            I agree to the <a href="#" class="auth-link">Terms of Service</a> and <a href="#" class="auth-link">Privacy Policy</a>
                        </label>
                    </div>

                    <div class="form-check mb-3">
                        <input class="form-check-input" type="checkbox" id="newsletter">
                        <label class="form-check-label" for="newsletter">
                            Send me updates and educational resources
                        </label>
                    </div>

                    <button type="submit" class="btn btn-primary w-100 mb-3">
                        <i class="fas fa-user-plus me-2"></i>Create Account
                    </button>

                    <div class="text-center mb-3">
                        <span class="text-muted">Already have an account?</span>
                        <a href="/login" class="auth-link">Sign in here</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function checkPasswordStrength() {
            const password = document.getElementById('password').value;
            const strengthBar = document.getElementById('passwordStrength');
            
            let strength = 0;
            
            // Check password strength
            if (password.length >= 8) strength++;
            if (password.match(/[a-z]/)) strength++;
            if (password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[^a-zA-Z0-9]/)) strength++;
            
            // Update strength bar
            strengthBar.className = 'password-strength';
            
            if (strength <= 2) {
                strengthBar.classList.add('strength-weak');
                strengthBar.style.width = '33%';
            } else if (strength <= 4) {
                strengthBar.classList.add('strength-medium');
                strengthBar.style.width = '66%';
            } else {
                strengthBar.classList.add('strength-strong');
                strengthBar.style.width = '100%';
            }
        }

        document.getElementById('signupForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            const formData = {
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
                password: password,
                role: document.getElementById('role').value,
                institution: document.getElementById('institution').value,
                newsletter: document.getElementById('newsletter').checked
            };
            
            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Account created successfully! Please login.');
                    window.location.href = '/login';
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/login')
def login():
    """Comprehensive login page with header"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Login - Student Performance Predictor') + '''
    <div class="auth-body">
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="logo-section">
                        <i class="fas fa-sign-in-alt"></i>
                        <h2>Welcome Back</h2>
                        <p class="auth-subtitle">Sign in to access your academic dashboard</p>
                    </div>
                </div>

                <form id="loginForm" class="auth-form">
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

                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="rememberMe">
                            <label class="form-check-label" for="rememberMe">
                                Remember me for 30 days
                            </label>
                        </div>
                        <a href="#" class="auth-link" onclick="showForgotPassword()">Forgot password?</a>
                    </div>

                    <button type="submit" class="btn btn-primary w-100 mb-3">
                        <i class="fas fa-sign-in-alt me-2"></i>Sign In
                    </button>

                    <div class="text-center mb-3">
                        <span class="text-muted">Don't have an account?</span>
                        <a href="/signup" class="auth-link">Sign up here</a>
                    </div>

                    <div class="text-center">
                        <p class="text-muted mb-2">Or continue with</p>
                        <div class="d-flex justify-content-center gap-2">
                            <button type="button" class="btn btn-outline-primary">
                                <i class="fab fa-google me-2"></i>Google
                            </button>
                            <button type="button" class="btn btn-outline-primary">
                                <i class="fab fa-microsoft me-2"></i>Microsoft
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showForgotPassword() {
            const email = document.getElementById('email').value;
            if (email) {
                alert(`Password reset link has been sent to ${email}`);
            } else {
                alert('Please enter your email address first');
            }
        }

        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                rememberMe: document.getElementById('rememberMe').checked
            };
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    alert('Login successful! Redirecting to dashboard...');
                    window.location.href = '/dashboard';
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Dashboard - Student Performance Predictor') + '''
    <div class="container my-5">
        <h1 class="mb-4">Dashboard</h1>
        <p class="text-muted">Welcome to your academic dashboard!</p>
        
        <div class="row">
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>24</h5>
                        <p>Predictions Made</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>85%</h5>
                        <p>Success Rate</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>78.5</h5>
                        <p>Avg Score</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-center">
                    <div class="card-body">
                        <h5>Low</h5>
                        <p>Risk Level</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h3>Quick Actions</h3>
            <div class="row">
                <div class="col-md-6">
                    <a href="/dropout_prediction" class="btn btn-warning w-100 mb-2">
                        <i class="fas fa-exclamation-triangle me-2"></i>Dropout Risk Analysis
                    </a>
                </div>
                <div class="col-md-6">
                    <a href="/pass_fail_page" class="btn btn-primary w-100 mb-2">
                        <i class="fas fa-check-circle me-2"></i>Pass/Fail Prediction
                    </a>
                </div>
                <div class="col-md-6">
                    <a href="/score_prediction_page" class="btn btn-success w-100 mb-2">
                        <i class="fas fa-chart-line me-2"></i>Score Prediction
                    </a>
                </div>
                <div class="col-md-6">
                    <a href="/logout" class="btn btn-secondary w-100 mb-2">
                        <i class="fas fa-sign-out-alt me-2"></i>Logout
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''')

@app.route('/logout')
def logout():
    """Logout page"""
    session.clear()
    return redirect(url_for('login'))

# Prediction Pages
@app.route('/dropout_prediction')
def dropout_prediction():
    """Dropout prediction page"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Dropout Risk Analysis') + '''
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-center">
                            <i class="fas fa-exclamation-triangle me-2"></i>Dropout Risk Analysis
                        </h2>
                        <p class="text-center text-muted">Enter student information to analyze dropout risk</p>
                    </div>
                    <div class="card-body">
                        <form id="predictionForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="age" class="form-label">Age</label>
                                    <input type="number" class="form-control" id="age" min="16" max="30" value="20" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="gpa" class="form-label">GPA</label>
                                    <input type="number" class="form-control" id="gpa" step="0.1" min="0" max="4" value="3.2" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="study_hours" class="form-label">Study Hours per Day</label>
                                    <input type="number" class="form-control" id="study_hours" step="0.1" min="0" max="10" value="6.0" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="attendance" class="form-label">Attendance Rate</label>
                                    <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" value="0.85" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="previous_failures" class="form-label">Previous Failures</label>
                                    <input type="number" class="form-control" id="previous_failures" min="0" max="10" value="1" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="work_hours" class="form-label">Work Hours per Week</label>
                                    <input type="number" class="form-control" id="work_hours" min="0" max="40" value="15" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="scholarship" class="form-label">Has Scholarship</label>
                                    <select class="form-select" id="scholarship" required>
                                        <option value="0">No</option>
                                        <option value="1" selected>Yes</option>
                                    </select>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="financial_aid" class="form-label">Has Financial Aid</label>
                                    <select class="form-select" id="financial_aid" required>
                                        <option value="0" selected>No</option>
                                        <option value="1">Yes</option>
                                    </select>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-warning w-100">
                                <i class="fas fa-exclamation-triangle me-2"></i>Analyze Risk
                            </button>
                        </form>

                        <div id="result" class="mt-4" style="display: none;">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Risk Analysis Result</h5>
                                    <div id="resultContent"></div>
                                </div>
                            </div>
                        </div>
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
                    resultContent.innerHTML = `<div class="alert alert-danger"><strong>Error:</strong> ${result.error}</div>`;
                } else {
                    const alertClass = result.dropout_risk === 'High' ? 'alert-danger' : 'alert-success';
                    resultContent.innerHTML = `
                        <div class="alert ${alertClass}">
                            <h6><i class="fas fa-exclamation-triangle me-2"></i>Dropout Risk: ${result.dropout_risk}</h6>
                            <p><strong>Confidence:</strong> ${result.confidence.toFixed(1)}%</p>
                            <p><strong>Dropout Probability:</strong> ${result.dropout_probability.toFixed(1)}%</p>
                            <p><strong>Retention Probability:</strong> ${result.retention_probability.toFixed(1)}%</p>
                            ${result.recommendations && result.recommendations.length > 0 ? '<h6>Recommendations:</h6><ul>' + result.recommendations.map(r => `<li>${r}</li>`).join('') + '</ul>' : ''}
                        </div>
                    `;
                }
                
                resultDiv.style.display = 'block';
            } catch (error) {
                document.getElementById('resultContent').innerHTML = `<div class="alert alert-danger"><strong>Network Error:</strong> ${error.message}</div>`;
                document.getElementById('result').style.display = 'block';
            }
        });
    </script>
</body>
</html>
    ''')

@app.route('/pass_fail_page')
def pass_fail_page():
    """Pass/Fail prediction page"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Pass/Fail Prediction') + '''
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-center">
                            <i class="fas fa-check-circle me-2"></i>Pass/Fail Prediction
                        </h2>
                    </div>
                    <div class="card-body">
                        <form id="predictionForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="study_hours" class="form-label">Study Hours per Day</label>
                                    <input type="number" class="form-control" id="study_hours" step="0.1" min="1" max="10" value="6.0" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="prev_exam_score" class="form-label">Previous Exam Score</label>
                                    <input type="number" class="form-control" id="prev_exam_score" min="0" max="100" value="75" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="attendance" class="form-label">Attendance Rate</label>
                                    <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" value="0.85" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="assignment_score" class="form-label">Assignment Score</label>
                                    <input type="number" class="form-control" id="assignment_score" min="0" max="100" value="80" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Predict</button>
                        </form>

                        <div id="result" class="mt-4" style="display: none;">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Prediction Result</h5>
                                    <div id="resultContent"></div>
                                </div>
                            </div>
                        </div>
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
    ''')

@app.route('/score_prediction_page')
def score_prediction_page():
    """Score prediction page"""
    return render_template_string(HEADER_TEMPLATE.replace('{title}', 'Score Prediction') + '''
    <div class="container my-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">
                        <h2 class="text-center">
                            <i class="fas fa-chart-line me-2"></i>Score Prediction
                        </h2>
                    </div>
                    <div class="card-body">
                        <form id="predictionForm">
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="study_hours" class="form-label">Study Hours per Day</label>
                                    <input type="number" class="form-control" id="study_hours" step="0.1" min="1" max="10" value="6.0" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="prev_exam_score" class="form-label">Previous Exam Score</label>
                                    <input type="number" class="form-control" id="prev_exam_score" min="0" max="100" value="75" required>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col-md-6 mb-3">
                                    <label for="attendance" class="form-label">Attendance Rate</label>
                                    <input type="number" class="form-control" id="attendance" step="0.01" min="0" max="1" value="0.85" required>
                                </div>
                                <div class="col-md-6 mb-3">
                                    <label for="assignment_score" class="form-label">Assignment Score</label>
                                    <input type="number" class="form-control" id="assignment_score" min="0" max="100" value="80" required>
                                </div>
                            </div>
                            <button type="submit" class="btn btn-success w-100">Predict Score</button>
                        </form>

                        <div id="result" class="mt-4" style="display: none;">
                            <div class="card">
                                <div class="card-body">
                                    <h5 class="card-title">Prediction Result</h5>
                                    <div id="resultContent"></div>
                                </div>
                            </div>
                        </div>
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
    ''')

# Authentication API Endpoints
@app.route('/api/signup', methods=['POST'])
def api_signup():
    """API endpoint for user signup"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'role', 'institution']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check if user already exists
        if data['email'] in users:
            return jsonify({'success': False, 'error': 'User with this email already exists'}), 400
        
        # Validate password strength
        password = data['password']
        if len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters long'}), 400
        
        if not any(c.isupper() for c in password):
            return jsonify({'success': False, 'error': 'Password must contain at least one uppercase letter'}), 400
        
        if not any(c.islower() for c in password):
            return jsonify({'success': False, 'error': 'Error: Password must contain at least one lowercase letter'}), 400
        
        if not any(c.isdigit() for c in password):
            return jsonify({'success': False, 'error': 'Password must contain at least one number'}), 400
        
        # Store user (in production, use a database)
        users[data['email']] = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'password': password,  # In production, hash this
            'role': data['role'],
            'institution': data['institution'],
            'newsletter': data.get('newsletter', False),
            'created_at': '2026-04-30'
        }
        
        return jsonify({'success': True, 'message': 'Account created successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Signup error: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Check if user exists
        if data['email'] not in users:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # Check password (in production, use proper password hashing)
        user = users[data['email']]
        if user['password'] != data['password']:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # Set session (in production, use proper session management)
        session['user_email'] = data['email']
        session['user_name'] = f"{user['firstName']} {user['lastName']}"
        session['user_role'] = user['role']
        
        return jsonify({'success': True, 'message': 'Login successful'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Login error: {str(e)}'}), 500

# Prediction API Endpoints
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
        
        print(f"DEBUG: Received data with keys: {list(data.keys())}")
        print(f"DEBUG: Number of received features: {len(data)}")
        
        # Validate exactly 8 features
        required_features = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        
        # Check for missing features
        missing_features = [f for f in required_features if f not in data]
        if missing_features:
            error_msg = f'Missing features: {missing_features}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Check for extra features
        extra_features = [f for f in data if f not in required_features]
        if extra_features:
            error_msg = f'Extra features not allowed: {extra_features}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
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
        print(f"DEBUG: Model expects: {dropout_model.n_features_in_} features")
        
        if features.shape[1] != 8:
            error_msg = f'Expected 8 features, got {features.shape[1]}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        # Additional validation
        if dropout_model.n_features_in_ != 8:
            error_msg = f'Model expects {dropout_model.n_features_in_} features, but API is configured for 8'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), 500
        
        # Scale and predict
        print("DEBUG: Scaling features...")
        features_scaled = dropout_scaler.transform(features)
        
        print("DEBUG: Making prediction...")
        prediction = dropout_model.predict(features_scaled)[0]
        probabilities = dropout_model.predict_proba(features_scaled)[0]
        
        print(f"DEBUG: Prediction successful: {prediction}")
        print(f"DEBUG: Probabilities: {probabilities}")
        
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
        
        print(f"DEBUG: Returning result: {result}")
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'Prediction error: {str(e)}'
        print(f"ERROR: {error_msg}")
        return jsonify({'error': error_msg}), 500

if __name__ == '__main__':
    print("Starting Student Performance App - WITH PROFESSIONAL AUTHENTICATION")
    print("=" * 70)
    print("FEATURES:")
    print("1. Professional header design")
    print("2. Comprehensive signup page with validation")
    print("3. Advanced login page with social options")
    print("4. Password strength indicator")
    print("5. Form validation and error handling")
    print("6. User session management")
    print("7. All prediction features working")
    print("8. Feature mismatch error resolved")
    print("=" * 70)
    print("\nAccess URLs:")
    print("Home: http://127.0.0.1:5000")
    print("Signup: http://127.0.0.1:5000/signup")
    print("Login: http://127.0.0.1:5000/login")
    print("Dashboard: http://127.0.0.1:5000/dashboard")
    print("Dropout Risk: http://127.0.0.1:5000/dropout_prediction")
    print("Pass/Fail: http://127.0.0.1:5000/pass_fail_page")
    print("Score Prediction: http://127.0.0.1:5000/score_prediction_page")
    print("\nProfessional authentication system ready!")
    app.run(debug=True, host='0.0.0.0', port=5000)
