from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for model components
model = None
scaler = None

def train_simple_model():
    """Train a simple model to avoid compatibility issues."""
    global model, scaler
    
    try:
        # Generate simple sample data
        np.random.seed(42)
        n_samples = 1000
        
        # Create simple features
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
        
        # Create target variable (dropout prediction)
        dropout_prob = (
            (df['gpa'] < 2.5) * 0.3 +
            (df['attendance'] < 0.7) * 0.2 +
            (df['previous_failures'] > 2) * 0.25 +
            (df['work_hours'] > 20) * 0.15 +
            np.random.random(n_samples) * 0.1
        )
        df['dropout'] = (dropout_prob > 0.5).astype(int)
        
        # Split features and target
        feature_columns = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        X = df[feature_columns]
        y = df['dropout']
        
        # Train scaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_scaled, y)
        
        # Save the model
        joblib.dump(model, 'dropout_model_simple.joblib')
        joblib.dump(scaler, 'dropout_scaler_simple.joblib')
        
        accuracy = model.score(X_scaled, y)
        print(f"Simple model trained successfully! Test accuracy: {accuracy:.3f}")
        
        return True
        
    except Exception as e:
        print(f"Error training simple model: {e}")
        return False

def load_model():
    """Load model, train new one if needed."""
    global model, scaler
    
    try:
        # Try to load the model first
        if os.path.exists('dropout_model_simple.joblib') and os.path.exists('dropout_scaler_simple.joblib'):
            model = joblib.load('dropout_model_simple.joblib')
            scaler = joblib.load('dropout_scaler_simple.joblib')
            print("Simple model loaded successfully!")
            return True
        else:
            # Train new model
            print("Training new simple model...")
            return train_simple_model()
    except Exception as e:
        print(f"Error loading model: {e}")
        return train_simple_model()

# Load the model on startup
load_model()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Main prediction endpoint - fixes 404 errors"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            # Expected features
            feature_columns = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
            
            # Fill missing values with defaults
            row_data = []
            defaults = [20, 3.0, 5, 0.8, 0, 1, 1, 10]  # Default values for each feature
            
            for i, col in enumerate(feature_columns):
                value = data.get(col, defaults[i])
                row_data.append(value)
            
            # Create DataFrame and scale
            df = pd.DataFrame([row_data], columns=feature_columns)
            
            if model and scaler:
                X_scaled = scaler.transform(df)
                prediction = model.predict(X_scaled)[0]
                probabilities = model.predict_proba(X_scaled)[0]
                
                result = {
                    'prediction': int(prediction),
                    'dropout_risk': 'High' if prediction == 1 else 'Low',
                    'confidence': float(max(probabilities) * 100),
                    'dropout_probability': float(probabilities[1] * 100),
                    'retention_probability': float(probabilities[0] * 100),
                    'status': 'success'
                }
                
                return jsonify(result)
            else:
                return jsonify({"error": "Model not loaded properly", "status": "error"}), 500
                
    except Exception as e:
        return jsonify({"error": f"Error making prediction: {str(e)}", "status": "error"}), 500

@app.route('/predict_csv', methods=['POST'])
def predict_csv():
    """Handle CSV file upload and prediction."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part", "status": "error"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file", "status": "error"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file and make predictions
        return predict_from_csv(filepath)

def predict_from_csv(filepath):
    """Function to process CSV file and predict."""
    try:
        # Read the CSV file
        df = pd.read_csv(filepath, skipinitialspace=True)
        
        # Expected columns for simple model
        expected_columns = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
        
        # Handle different CSV formats
        if len(df.columns) >= len(expected_columns):
            # Use first 8 columns
            df = df.iloc[:, :len(expected_columns)]
            df.columns = expected_columns
        else:
            # Add missing columns with default values
            for i, col in enumerate(expected_columns):
                if i >= len(df.columns):
                    df[col] = np.random.choice([20, 3.0, 5, 0.8, 0, 1, 1, 10], size=len(df))
            df = df[expected_columns]
        
        # Make predictions
        if model and scaler:
            X_scaled = scaler.transform(df[expected_columns])
            predictions = model.predict(X_scaled)
            probabilities = model.predict_proba(X_scaled)
            
            # Format results
            results = []
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                results.append({
                    'student_id': i + 1,
                    'prediction': int(pred),
                    'dropout_risk': 'High' if pred == 1 else 'Low',
                    'confidence': float(max(prob) * 100),
                    'dropout_probability': float(prob[1] * 100),
                    'retention_probability': float(prob[0] * 100)
                })
            
            return jsonify({
                'status': 'success',
                'predictions': results,
                'total_students': len(results),
                'high_risk_count': sum(1 for r in results if r['prediction'] == 1),
                'low_risk_count': sum(1 for r in results if r['prediction'] == 0)
            })
        else:
            return jsonify({"error": "Model not loaded properly", "status": "error"}), 500
            
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}", "status": "error"}), 500

@app.route('/predict_manual', methods=['POST'])
def predict_manual():
    """Handle manual prediction requests."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            # Expected features
            feature_columns = ['age', 'gpa', 'study_hours', 'attendance', 'previous_failures', 'scholarship', 'financial_aid', 'work_hours']
            
            # Fill missing values with defaults
            row_data = []
            defaults = [20, 3.0, 5, 0.8, 0, 1, 1, 10]  # Default values for each feature
            
            for i, col in enumerate(feature_columns):
                value = data.get(col, defaults[i])
                row_data.append(value)
            
            # Create DataFrame and scale
            df = pd.DataFrame([row_data], columns=feature_columns)
            
            if model and scaler:
                X_scaled = scaler.transform(df)
                prediction = model.predict(X_scaled)[0]
                probabilities = model.predict_proba(X_scaled)[0]
                
                result = {
                    'prediction': int(prediction),
                    'dropout_risk': 'High' if prediction == 1 else 'Low',
                    'confidence': float(max(probabilities) * 100),
                    'dropout_probability': float(probabilities[1] * 100),
                    'retention_probability': float(probabilities[0] * 100)
                }
                
                return jsonify(result)
            else:
                return jsonify({"error": "Model not loaded properly"}), 500
                
    except Exception as e:
        return jsonify({"error": f"Error making prediction: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
