from flask import Flask, render_template, request, jsonify
import logging
import pickle
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load the machine learning components
try:
    with open('tpot_automl_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('shap_explainer.pkl', 'rb') as f:
        explainer = pickle.load(f)
    logging.info("All models loaded successfully.")
except FileNotFoundError as e:
    logging.error(f"File not found: {e}")
    model, scaler, explainer = None, None, None
except Exception as e:
    logging.error(f"Error loading components: {e}")
    model, scaler, explainer = None, None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None or scaler is None:
        return jsonify({'error': 'Model not loaded properly.'}), 500

    try:
        data = request.get_json()
        input_df = pd.DataFrame([data])
        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)[0]

        # SHAP values (best effort)
        try:
            shap_values = explainer.shap_values(input_scaled)
            sv = np.array(shap_values[0] if isinstance(shap_values, list) else shap_values)
            shap_values_json = (sv[:, :9].tolist() if sv.ndim == 2 else sv[:9].tolist())
        except Exception:
            shap_values_json = [0.0] * 9

        return jsonify({'predicted_gtu_mark': float(prediction), 'shap_values': shap_values_json})

    except Exception as e:
        app.logger.error(f'Prediction error: {e}')
        return jsonify({'error': 'Failed to make prediction'}), 500

if __name__ == '__main__':
    app.run(debug=False, port=5001)
