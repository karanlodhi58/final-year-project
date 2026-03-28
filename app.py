from flask import Flask, request, jsonify , render_template
from flask_cors import CORS
import pickle
import numpy as np

app = Flask(__name__)
CORS(app)

# Load trained model
model = pickle.load(open("random_forest_regression_model.pkl", "rb"))

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        # Get values from frontend
        pm25 = float(data.get('pm25'))
        pm10 = float(data.get('pm10'))
        no2 = float(data.get('no2'))
        co = float(data.get('co'))
        o3 = float(data.get('o3'))
        so2 = float(data.get('so2'))
        temp = float(data.get('temp'))
        humidity = float(data.get('humidity'))

        # IMPORTANT: Order must match training
        features = np.array([[pm25, pm10, no2, co, o3, so2, temp, humidity]])

        # Predict
        prediction = model.predict(features)[0]

        return jsonify({
            "aqi": int(prediction),
            "status": get_aqi_category(prediction)
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