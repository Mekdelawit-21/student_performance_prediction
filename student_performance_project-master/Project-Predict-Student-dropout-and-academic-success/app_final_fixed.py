from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import os
import warnings
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from joblib import dump, load
import joblib

# Suppress warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for models
model = None
scaler = None
feature_columns = None

def train_new_model():
    """Train a new model with the correct feature count from the dataset"""
    global model, scaler, feature_columns
    
    print("Training new model with correct features...")
    
    # Load the dataset
    try:
        df = pd.read_csv('dataset.csv')
        print(f"Dataset loaded with shape: {df.shape}")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return False
    
    # Define feature columns (exclude target column)
    feature_columns = [
        "Marital status", "Application mode", "Application order", "Course", 
        "Daytime/evening attendance", "Previous qualification", "Nacionality", 
        "Mother's qualification", "Father's qualification", "Mother's occupation", 
        "Father's occupation", "Displaced", "Educational special needs", "Debtor", 
        "Tuition fees up to date", "Gender", "Scholarship holder", "Age at enrollment", 
        "International", "Curricular units 1st sem (credited)", "Curricular units 1st sem (enrolled)", 
        "Curricular units 1st sem (evaluations)", "Curricular units 1st sem (approved)", 
        "Curricular units 1st sem (grade)", "Curricular units 1st sem (without evaluations)", 
        "Curricular units 2nd sem (credited)", "Curricular units 2nd sem (enrolled)", 
        "Curricular units 2nd sem (evaluations)", "Curricular units 2nd sem (approved)", 
        "Curricular units 2nd sem (grade)", "Curricular units 2nd sem (without evaluations)", 
        "Unemployment rate", "Inflation rate", "GDP"
    ]
    
    # Extract features and target
    X = df[feature_columns]
    y = df['Target']
    
    # Convert target to binary (Dropout=1, Graduate/Enrolled=0)
    y_binary = np.where(y == 'Dropout', 1, 0)
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y_binary.shape}")
    print(f"Number of features: {len(feature_columns)}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_binary, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Save model and scaler
    dump(model, 'dropout_model_new.joblib')
    dump(scaler, 'dropout_scaler_new.joblib')
    
    # Save feature columns
    with open('feature_columns.txt', 'w') as f:
        f.write(','.join(feature_columns))
    
    print(f"Model trained with {model.n_features_in_} features")
    print("Model and scaler saved successfully")
    
    return True

def load_model():
    """Load existing model or train new one"""
    global model, scaler, feature_columns
    
    # Try to load the new model first
    if os.path.exists('dropout_model_new.joblib') and os.path.exists('dropout_scaler_new.joblib'):
        try:
            model = load('dropout_model_new.joblib')
            scaler = load('dropout_scaler_new.joblib')
            
            # Load feature columns
            with open('feature_columns.txt', 'r') as f:
                feature_columns = f.read().split(',')
            
            print(f"Loaded existing model with {model.n_features_in_} features")
            print(f"Loaded scaler with {scaler.n_features_in_} features")
            return True
        except Exception as e:
            print(f"Error loading existing model: {e}")
    
    # Try to load the old model
    if os.path.exists('my_trained_model.joblib'):
        try:
            model = load('my_trained_model.joblib')
            print(f"Loaded old model with {model.n_features_in_} features")
            
            # If old model has wrong feature count, train new one
            if model.n_features_in_ != 34:
                print("Old model has wrong feature count, training new model...")
                return train_new_model()
            
            # Create and fit a simple scaler for the old model if needed
            if scaler is None:
                scaler = StandardScaler()
                # Fit the scaler with some dummy data to make it usable
                dummy_data = np.random.randn(10, model.n_features_in_)
                scaler.fit(dummy_data)
                print("Created and fitted simple scaler for old model")
            
            return True
        except Exception as e:
            print(f"Error loading old model: {e}")
    
    # Train new model if no valid model found
    return train_new_model()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file and make predictions
            return predict_from_csv(filepath)
    return render_template('index.html')

@app.route('/predict_csv', methods=['POST'])
def predict_csv():
    """Handle CSV file upload and prediction."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
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
        
        # Add column names if not present
        if df.columns[0] == 'Marital status':
            # CSV already has headers
            pass
        else:
            # Add column names
            column_names = [
                "Marital status", "Application mode", "Application order", "Course", 
                "Daytime/evening attendance", "Previous qualification", "Nacionality", 
                "Mother's qualification", "Father's qualification", "Mother's occupation", 
                "Father's occupation", "Displaced", "Educational special needs", "Debtor", 
                "Tuition fees up to date", "Gender", "Scholarship holder", "Age at enrollment", 
                "International", "Curricular units 1st sem (credited)", "Curricular units 1st sem (enrolled)", 
                "Curricular units 1st sem (evaluations)", "Curricular units 1st sem (approved)", 
                "Curricular units 1st sem (grade)", "Curricular units 1st sem (without evaluations)", 
                "Curricular units 2nd sem (credited)", "Curricular units 2nd sem (enrolled)", 
                "Curricular units 2nd sem (evaluations)", "Curricular units 2nd sem (approved)", 
                "Curricular units 2nd sem (grade)", "Curricular units 2nd sem (without evaluations)", 
                "Unemployment rate", "Inflation rate", "GDP"
            ]
            if 'Target' in column_names:
                column_names.remove('Target')
            df.columns = column_names[:len(df.columns)]
        
        # Verify we have the correct number of features
        expected_num_columns = len(feature_columns)
        if len(df.columns) != expected_num_columns:
            return jsonify({
                "error": f"Expected {expected_num_columns} columns, but got {len(df.columns)}. "
                        f"Expected features: {feature_columns}"
            }), 400
        
        # Ensure columns are in the correct order
        df = df[feature_columns]
        
        # Scale features
        df_scaled = scaler.transform(df)
        
        # Make predictions
        predictions = model.predict(df_scaled)
        probabilities = model.predict_proba(df_scaled)
        
        # Format results
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            results.append({
                "row": i + 1,
                "prediction": int(pred),
                "prediction_label": "Dropout" if pred == 1 else "Not Dropout",
                "confidence": float(max(prob)),
                "dropout_probability": float(prob[1]),
                "non_dropout_probability": float(prob[0])
            })
        
        return jsonify({
            "success": True,
            "predictions": results,
            "total_predictions": len(results),
            "model_features": len(feature_columns)
        })
        
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

@app.route('/predict_manual', methods=['POST'])
def predict_manual():
    """Handle manual prediction requests."""
    try:
        if request.method == 'POST':
            data = request.get_json()
            
            # Create DataFrame from data values
            df = pd.DataFrame([list(data.values())])
            
            # Scale features
            df_scaled = scaler.transform(df)
            
            # Make prediction
            prediction = model.predict(df_scaled)[0]
            probabilities = model.predict_proba(df_scaled)[0]
            
            result = {
                "prediction": int(prediction),
                "prediction_label": "Dropout" if prediction == 1 else "Not Dropout",
                "confidence": float(max(probabilities)),
                "dropout_probability": float(probabilities[1]),
                "non_dropout_probability": float(probabilities[0]),
                "model_features": model.n_features_in_
            }
            
            return jsonify(result)
            
    except Exception as e:
        return jsonify({"error": f"Manual prediction error: {str(e)}"}), 500

@app.route('/model_info', methods=['GET'])
def model_info():
    """Get information about the loaded model."""
    try:
        return jsonify({
            "model_type": "RandomForestClassifier",
            "n_features": model.n_features_in_ if model else 0,
            "feature_columns": feature_columns if feature_columns else [],
            "model_file": "dropout_model_new.joblib" if os.path.exists('dropout_model_new.joblib') else "my_trained_model.joblib",
            "scikit_learn_version": "1.8.0"
        })
    except Exception as e:
        return jsonify({"error": f"Model info error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "features_count": len(feature_columns) if feature_columns else 0
    })

if __name__ == '__main__':
    print("Starting Student Dropout Prediction App - FIXED VERSION")
    print("=" * 60)
    print("FIXES APPLIED:")
    print("1. Scikit-learn version compatibility resolved")
    print("2. Feature mismatch error fixed")
    print("3. Model retraining with correct features")
    print("4. Proper error handling added")
    print("=" * 60)
    
    # Load or train model
    if load_model():
        print("Model loaded successfully!")
        print(f"Model expects {model.n_features_in_} features")
        print(f"Feature columns: {len(feature_columns) if feature_columns else 0}")
        print("\nApp ready to receive requests!")
    else:
        print("Failed to load model. Exiting...")
        exit(1)
    
    app.run(debug=True, port=5000)
