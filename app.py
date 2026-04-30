from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Load all models
rf_model = pickle.load(open("random_forest_regression_retrainmodel.pkl", "rb"))
xgb_model = pickle.load(open("xgboost_aqi_model.pkl", "rb"))
dt_model = pickle.load(open("decision_tree_aqi_model.pkl", "rb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        pm25 = float(data.get('pm25'))
        pm10 = float(data.get('pm10'))
        no2 = float(data.get('no2'))
        co = float(data.get('co'))
        o3 = float(data.get('o3'))

        # Feature order must match training
        features = np.array([[pm25, pm10, no2, co, o3]])

        # Predictions from all models
        rf_pred = rf_model.predict(features)[0]
        xgb_pred = xgb_model.predict(features)[0]
        dt_pred = dt_model.predict(features)[0]

        return jsonify({
            "random_forest": int(rf_pred),
            "xgboost": int(xgb_pred),
            "decision_tree": int(dt_pred),

            "rf_status": get_aqi_category(rf_pred),
            "xgb_status": get_aqi_category(xgb_pred),
            "dt_status": get_aqi_category(dt_pred)
        })

    except Exception as e:
        return jsonify({"error": str(e)})


def get_aqi_category(aqi):
    if aqi <= 50:
        return "Good 🟢"
    elif aqi <= 100:
        return "Moderate 🟡"
    elif aqi <= 200:
        return "Poor 🟠"
    elif aqi <= 300:
        return "Very Poor 🔴"
    else:
        return "Severe ⚫"
    
if __name__ == "__main__":
    app.run(debug=True)