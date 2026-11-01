import pickle
import traceback
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Feature names in the exact chronological order used during StandardScaler training
FEATURE_NAMES = [
    'ALLSKY_SFC_SW_DWN',
    'ALLSKY_SFC_SW_DNI',
    'T2M',
    'T2MDEW',
    'T2MWET',
    'T2M_MAX',
    'T2M_MIN',
    'RH2M',
    'QV2M',
    'WS2M',
    'GWETTOP'
]

# Load ML artifacts at startup
print("Loading Model and Scaler...")
try:
    with open('final_scaler.pkl', 'rb') as f:
        scaler = pickle.load(f)
    with open('final_model.pkl', 'rb') as f:
        model = pickle.load(f)
    print("Successfully loaded XGBoost model and standard scaler!")
except Exception as e:
    print(f"Error loading model artifacts: {e}")
    scaler = None
    model = None

@app.route('/')
def index():
    """Render the main interactive dashboard."""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health():
    """Service health and model readiness probe."""
    is_ready = model is not None and scaler is not None
    return jsonify({
        "status": "healthy" if is_ready else "degraded",
        "model_loaded": is_ready,
        "algorithm": "XGBoost Regressor (300 estimators, max_depth=6)",
        "features_count": len(FEATURE_NAMES)
    }), 200 if is_ready else 503

@app.route('/api/info', methods=['GET'])
def api_info():
    """Return model metadata, benchmark metrics, and feature schemas."""
    return jsonify({
        "project": "PrecipiCast AI & Rainwater Harvesting Engine",
        "version": "1.0.0",
        "algorithm": "XGBoost Regressor",
        "metrics": {
            "test_r2": 0.467,
            "train_r2": 0.838,
            "test_rmse_mm": 7.181,
            "test_mae_mm": 4.478
        },
        "features": [
            {"id": "sw_down", "column": "ALLSKY_SFC_SW_DWN", "unit": "W/m²", "description": "Downwelling Shortwave Solar Irradiance"},
            {"id": "sw_direct", "column": "ALLSKY_SFC_SW_DNI", "unit": "W/m²", "description": "Direct Normal Solar Irradiance"},
            {"id": "temp_avg", "column": "T2M", "unit": "°C", "description": "Average Air Temperature at 2m"},
            {"id": "temp_dew", "column": "T2MDEW", "unit": "°C", "description": "Dew Point Temperature at 2m"},
            {"id": "temp_wet", "column": "T2MWET", "unit": "°C", "description": "Wet Bulb Temperature at 2m"},
            {"id": "temp_max", "column": "T2M_MAX", "unit": "°C", "description": "Maximum Air Temperature at 2m"},
            {"id": "temp_min", "column": "T2M_MIN", "unit": "°C", "description": "Minimum Air Temperature at 2m"},
            {"id": "humidity_rel", "column": "RH2M", "unit": "%", "description": "Relative Humidity at 2m"},
            {"id": "humidity_spec", "column": "QV2M", "unit": "g/kg", "description": "Specific Humidity at 2m"},
            {"id": "wind_speed", "column": "WS2M", "unit": "m/s", "description": "Wind Speed at 2m"},
            {"id": "soil_wetness", "column": "GWETTOP", "unit": "0.0 - 1.0", "description": "Surface Soil Wetness Ratio"}
        ]
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Predict rainfall (mm/day) from 11 meteorological parameters."""
    if model is None or scaler is None:
        return jsonify({"error": "Model files are missing on server (final_model.pkl, final_scaler.pkl)."}), 500
        
    try:
        data = request.get_json(force=True) if request.is_json else request.form
        if not data:
            return jsonify({"error": "No input payload provided."}), 400
        
        # Extract features in strict order matching scaler.feature_names_in_
        feature_values = [
            float(data.get('sw_down', 18.5)),
            float(data.get('sw_direct', 10.2)),
            float(data.get('temp_avg', 27.5)),
            float(data.get('temp_dew', 24.1)),
            float(data.get('temp_wet', 25.8)),
            float(data.get('temp_max', 30.1)),
            float(data.get('temp_min', 25.0)),
            float(data.get('humidity_rel', 85.5)),
            float(data.get('humidity_spec', 19.1)),
            float(data.get('wind_speed', 2.5)),
            float(data.get('soil_wetness', 0.85))
        ]
        
        # Build DataFrame with proper feature names to avoid sklearn feature_name warnings
        input_df = pd.DataFrame([feature_values], columns=FEATURE_NAMES)
        
        # Scale and predict
        scaled_input = scaler.transform(input_df)
        raw_prediction = model.predict(scaled_input)[0]
        
        # Non-negative rectification: precipitation cannot be below zero
        prediction_mm = max(0.0, float(raw_prediction))
        
        # Rain classification category
        if prediction_mm < 0.1:
            category = "No Rain"
            intensity_desc = "Clear skies and dry atmospheric conditions."
        elif prediction_mm < 10.0:
            category = "Light Rain"
            intensity_desc = "Scattered drizzle or light showers expected."
        elif prediction_mm < 35.0:
            category = "Moderate Rain"
            intensity_desc = "Steady, significant rainfall across catchment areas."
        elif prediction_mm < 75.0:
            category = "Heavy Rain"
            intensity_desc = "Intense precipitation; strong rainwater harvesting yields."
        else:
            category = "Torrential / Storm Rain"
            intensity_desc = "Severe storm event; monitor catchment overflow buffers."

        return jsonify({
            "success": True,
            "prediction_mm": round(prediction_mm, 2),
            "category": category,
            "intensity_description": intensity_desc
        })
        
    except ValueError as e:
        return jsonify({"error": f"Invalid numerical value: {str(e)}"}), 400
    except Exception as e:
        print("Prediction Error:", traceback.format_exc())
        return jsonify({"error": f"Internal prediction error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
