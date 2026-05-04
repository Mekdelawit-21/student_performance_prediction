import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import shap
import warnings
warnings.filterwarnings('ignore')

def train_model():
    """Train a machine learning model for student performance prediction."""
    
    # Generate sample training data
    np.random.seed(42)
    n_samples = 1000
    
    # Features for student performance
    data = {
        'study_hours': np.random.uniform(1, 10, n_samples),
        'prev_exam_score': np.random.uniform(0, 100, n_samples),
        'attendance_rate': np.random.uniform(0.5, 1.0, n_samples),
        'assignment_score': np.random.uniform(0, 100, n_samples),
        'sleep_hours': np.random.uniform(4, 10, n_samples),
        'stress_level': np.random.uniform(1, 10, n_samples),
        'social_activities': np.random.uniform(0, 20, n_samples),
        'previous_gpa': np.random.uniform(2.0, 4.0, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate target variable (final exam score)
    df['final_score'] = (
        df['prev_exam_score'] * 0.3 + 
        df['assignment_score'] * 0.25 + 
        df['study_hours'] * 6 + 
        df['attendance_rate'] * 15 + 
        df['sleep_hours'] * 2 + 
        df['previous_gpa'] * 10 - 
        df['stress_level'] * 1.5 - 
        df['social_activities'] * 0.3 + 
        np.random.normal(0, 3, n_samples)
    )
    
    # Clip scores to 0-100 range
    df['final_score'] = np.clip(df['final_score'], 0, 100)
    
    # Prepare features and target
    feature_columns = [
        'study_hours', 'prev_exam_score', 'attendance_rate', 
        'assignment_score', 'sleep_hours', 'stress_level', 
        'social_activities', 'previous_gpa'
    ]
    
    X = df[feature_columns]
    y = df['final_score']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Create SHAP explainer
    explainer = shap.TreeExplainer(model)
    
    print(f"Model trained successfully!")
    print(f"Training R² score: {model.score(X_train, y_train):.3f}")
    print(f"Test R² score: {model.score(X_test, y_test):.3f}")
    
    return model, explainer

def get_expected_features():
    """Return the list of expected features for the model."""
    return [
        'study_hours', 'prev_exam_score', 'attendance_rate', 
        'assignment_score', 'sleep_hours', 'stress_level', 
        'social_activities', 'previous_gpa'
    ]

if __name__ == "__main__":
    # Train and save the model
    model, explainer = train_model()
    joblib.dump({
        'model': model, 
        'explainer': explainer
    }, 'my_model.joblib')
    print("Model saved successfully!")
