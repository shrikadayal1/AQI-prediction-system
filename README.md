# AQI Prediction System

An end-to-end Machine Learning project that predicts Air Quality Index (AQI) levels using environmental and pollution-related parameters. The project includes data preprocessing, model training, performance evaluation, and an interactive web application built with Streamlit.

## Project Overview

Air pollution has become a major environmental concern worldwide. This project leverages Machine Learning algorithms to predict AQI values based on air quality indicators, helping users assess environmental conditions and make informed decisions.

The system processes pollution data, trains multiple models, compares performance, and deploys the best-performing model through a user-friendly web interface.

---

## Features

- Data Cleaning and Preprocessing
- Feature Engineering
- Multiple ML Models Comparison
- AQI Prediction
- Model Evaluation and Visualization
- Streamlit Web Application
- Real-time User Input Predictions

---

## Tech Stack

### Programming Language
- Python

### Machine Learning
- Scikit-Learn
- Random Forest
- Gradient Boosting

### Data Processing
- Pandas
- NumPy

### Visualization
- Matplotlib
- Seaborn

### Deployment
- Streamlit

---

## Dataset

The model is trained using air pollution data containing environmental indicators used for AQI prediction.

Features include:

- PM2.5
- PM10
- NO₂
- SO₂
- CO
- O₃
- Other pollution-related parameters

---

## Machine Learning Pipeline

```text
Data Collection
      │
      ▼
Data Cleaning
      │
      ▼
Feature Engineering
      │
      ▼
Train-Test Split
      │
      ▼
Model Training
      │
      ▼
Model Evaluation
      │
      ▼
Best Model Selection
      │
      ▼
Streamlit Deployment
```

---

## Models Used

- Random Forest Regressor
- Gradient Boosting Regressor

Model files:

- rf_model.pkl
- gb_model.pkl
- scaler.pkl
- label_encoder.pkl

---

## Project Structure

```text
AQI-prediction-system/
│
├── app.py
├── streamlit_app.py
├── updated_pollution_dataset.csv
├── requirements.txt
│
├── rf_model.pkl
├── gb_model.pkl
├── air_quality_model.pkl
├── scaler.pkl
├── label_encoder.pkl
│
├── confusion_matrix.png
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/AQI-prediction-system.git
cd AQI-prediction-system
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Streamlit Application

```bash
streamlit run streamlit_app.py
```

---

## Results

The trained models were evaluated using standard Machine Learning metrics to identify the best-performing AQI prediction model.

Evaluation metrics include:

- Accuracy
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- R² Score

---

## Future Improvements

- Deep Learning-based AQI Prediction
- Live Air Quality Data Integration
- Weather API Integration
- Cloud Deployment
- Mobile Application Support

---

## Applications

- Smart Cities
- Environmental Monitoring
- Public Health Awareness
- Pollution Analysis
- Government Air Quality Monitoring

---

## Author

**Shrika Dayal**

B.Tech CSE & Business Systems, VIT Vellore

AI/ML Enthusiast | Software Developer | Finance & Technology Enthusiast
