from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Load models
# Load all models
rf_model = pickle.load(open("random_forest_regression_retrainmodel.pkl", "rb"))
xgb_model = pickle.load(open("xgboost_aqi_model.pkl", "rb"))
dt_model = pickle.load(open("decision_tree_aqi_model.pkl", "rb"))


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

        features = np.array([[
            float(data["pm25"]),
            float(data["pm10"]),
            float(data["no2"]),
            float(data["co"]),
            float(data["o3"])
        ]])

        rf = int(rf_model.predict(features)[0])
        xgb = int(xgb_model.predict(features)[0])
        dt = int(dt_model.predict(features)[0])

        def get_status(aqi):
            if aqi <= 50: return "Good"
            elif aqi <= 100: return "Moderate"
            elif aqi <= 200: return "Unhealthy"
            elif aqi <= 300: return "Very Unhealthy"
            else: return "Hazardous"

        return jsonify({
            "random_forest": rf,
            "xgboost": xgb,
            "decision_tree": dt,
            "rf_status": get_status(rf),
            "xgb_status": get_status(xgb),
            "dt_status": get_status(dt)
        })

    except Exception as e:
        return jsonify({"error": str(e)})
if __name__ == "__main__":
    app.run(debug=True)