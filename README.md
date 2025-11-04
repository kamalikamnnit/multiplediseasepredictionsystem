[README (2).md](https://github.com/user-attachments/files/23342509/README.2.md)

# Project Title

# 🩺 Multiple Disease Prediction System (MDPS) - Streamlit App

[![Contributors](https://img.shields.io/badge/Contributors-1-blue)]() 
[![Stars](https://img.shields.io/github/stars/kamalikamnnit/multiplediseasepredictionsystem?style=social)](https://github.com/kamalikamnnit/multiplediseasepredictionsystem)


## Project Overview

Welcome to the **Multiple Disease Prediction System (MDPS)**, an interactive, web-based health application built entirely using **Streamlit**. MDPS provides users with immediate, data-driven predictions for three major chronic diseases based on personalized health parameters.

The system features robust user authentication, personal health categorization (BMI), secure data persistence using SQLite, and the ability to generate a comprehensive, personalized health report in **PDF format** with visual analytics.

## 🚀 Key Features and Functionalities

The application consolidates several core functionalities into one seamless user experience:

| Feature Category | Description | Key Technologies |
| :--- | :--- | :--- |
| **Authentication** | Secure user registration and login management with password complexity enforcement. | `bcrypt`, `sqlite3`, `re` |
| **Prediction Suite** | Provides diagnostics for Diabetes, Heart Disease, and Parkinson's Disease. | `scikit-learn`, `pickle` |
| **Personal Health** | Calculates BMI, categorizes risk (Underweight, Healthy, Obese), and provides diet suggestions. | Python Logic |
| **Nutrition Analyzer** | Real-time analysis of macronutrients (Calories, Protein, Fat, Carbs) for queried food items via external API. | **Nutritionix API**, `requests` |
| **Analytics & History** | Stores test history, displays prediction frequency charts, and tracks detection events over time. | `pandas`, `matplotlib`, `seaborn`, `sqlite3` |
| **PDF Reporting** | Generates a professional, personalized health report including profile, history, and embedded analytical charts. | `fpdf2` |

## 🛠️ Technologies Used

| Category | Libraries / Frameworks |
| :--- | :--- |
| **Core App** | **Streamlit** (1.44.1+), `streamlit_option_menu` |
| **Machine Learning** | `scikit-learn`, `pickle` |
| **Data Handling** | `pandas`, `numpy` |
| **Visualization** | `matplotlib`, `seaborn` |
| **Persistence & Security** | `sqlite3`, `bcrypt`, `re` |
| **Integrations** | **Nutritionix API**, `requests`, `python-dotenv` |
| **Reporting** | `fpdf2` |

### Environment Dependencies (`requirements.txt`)

```txt
fpdf2>=2.8.2
matplotlib>=3.8.2
numpy>=1.26.4
pandas>=2.2.3
Pillow>=11.2.1
python-dotenv>=1.1.0
requests>=2.32.3
seaborn>=0.13.2
streamlit>=1.44.1
streamlit_option_menu>=0.4.0
tensorflow>=2.18.0
scikit-learn>=1.0.0
bcrypt==4.0.1


📊 Project Structure
Each project follows a consistent structure for easy navigation and understanding:

MultipleDiseasePredictionSystem/
│
├── All_Models/                # Trained ML models (.sav files)
├── data/                      # (Location for future datasets)
├── app.py                     # Main Streamlit application file (UI & Logic)
├── users.db                   # SQLite Database for user credentials
├── results.db                 # SQLite Database for prediction history
├── .env                       # Environment variables for API keys
└── requirements.txt           # Python dependencies


🌍 Deployment
The MDPS is currently deployed on the Streamlit Cloud platform for public access.

Platform: Streamlit Cloud

Run Command: streamlit run app.py


📚 Datasets and Models
The underlying models were trained on publicly accessible health datasets:

Diabetes Prediction: [Dataset](https://www.kaggle.com/datasets/mathchi/diabetes-data-set)

Heart Disease Prediction: [Dataset](https://www.kaggle.com/datasets/mahatiratusher/heart-disease-risk-prediction-dataset)

Parkinson's Disease Prediction : [Dataset](https://www.kaggle.com/datasets/jukurishashank/parkinsons-disease-prediction-dataset)
