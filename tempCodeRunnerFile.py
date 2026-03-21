# streamlit_app.py

import streamlit as st
import joblib
import numpy as np

# Load the model, scaler, and label encoder at the start
try:
    model = joblib.load('air_quality_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    st.write("Model, Scaler, and Label Encoder loaded successfully.")
except Exception as e:
    st.write(f"Error loading model, scaler, or label encoder: {e}")

# Streamlit app UI
st.title('Air Quality Prediction')

# Input fields for pollutants
pm25 = st.number_input('PM2.5', min_value=0.0)
pm10 = st.number_input('PM10', min_value=0.0)
no2 = st.number_input('NO2', min_value=0.0)
so2 = st.number_input('SO2', min_value=0.0)
co = st.number_input('CO', min_value=0.0)
temperature = st.number_input('Temperature', min_value=-100.0, max_value=100.0)

# Prediction button
if st.button('Predict'):
    try:
        # Prepare features for prediction
        features = np.array([[pm25, pm10, no2, so2, co, temperature]])
        features_scaled = scaler.transform(features)

        # Predict AQI
        predicted_aqi = model.predict(features_scaled)

        # Decode the predicted AQI category using the label encoder
        predicted_category = label_encoder.inverse_transform([int(round(predicted_aqi[0]))])[0]

        st.write(f"The predicted Air Quality is: {predicted_category}")

    except ValueError as ve:
        st.write(f"Invalid input value: {ve}")
    except Exception as e:
        st.write(f"Error: {e}")

