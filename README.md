🩺 Multiple Disease Prediction System (MDPS) - Streamlit ApplicationProject OverviewWelcome to the Multiple Disease Prediction System (MDPS), an interactive, web-based health application built entirely using Streamlit. MDPS provides users with immediate, data-driven predictions for three major chronic diseases (Diabetes, Heart Disease, and Parkinson's) based on user-input health parameters.The system features robust user authentication, personal BMI calculation and health categorization, secure data persistence using SQLite, and the ability to generate a comprehensive, personalized health report in PDF format with visual analytics.Key Features and FunctionalitiesSecure Authentication: User registration utilizes bcrypt hashing for secure password storage. Login validates credentials against the stored hash.Disease Prediction Suite: Integrates pre-trained Machine Learning models (Pickle objects) to offer diagnostics for:Diabetes PredictionHeart Disease PredictionParkinson's Disease PredictionBMI and Health Metrics: Automatically calculates the user's Body Mass Index (BMI) and provides instant health categorization (Underweight, Healthy, Overweight, Obese) with associated risks and diet suggestions.Personalized Diet & Nutrition Analysis: Integrates with the Nutritionix API to provide detailed macronutrient breakdowns (Calories, Protein, Fat, Carbs, Sugars, Fiber) for any queried food item.Prediction History & Analytics: Stores all user prediction results in an SQLite database. Users can view:A table of their entire test history.Bar Chart Visualization showing the frequency of positive detections.Timeline Graph tracing detection events over time.Custom Health Report Generation: Generates a professional, downloadable PDF Health Report for the user, containing profile information, full prediction history, and embedded analytical charts (using fpdf).Password Strength Validation: Implements backend validation using Python's re module to enforce strong password policies (min. 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special character).Technologies and Libraries UsedCategoryTools / LibrariesFront-End / UIstreamlit, streamlit_option_menuMachine Learningscikit-learn (for model training), pickle (for model loading), numpy, pandasData Visualizationmatplotlib, seabornData Persistencesqlite3 (for user and prediction data), bcrypt (for password hashing)External ServicesNutritionix API (managed with requests and python-dotenv)Reportingfpdf2 (for PDF generation), base64Generalos, re (for Regex validation)Environment Dependencies (requirements.txt)Plaintextfpdf2>=2.8.2
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
Project Structure (Deployment-Ready)The application maintains a clean, modular structure necessary for easy maintenance and deployment.MultipleDiseasePredictionSystem/
│
├── .devcontainer/             # (Development Environment Config)
├── All_Models/                # Contains pre-trained models (.sav files)
├── dejavu-fonts-ttf-2.37/     # (Font files—Note: Switched to Arial in fpdf for cross-platform stability)
├── app.py                     # Main Streamlit application file (All logic and UI)
├── users.db                   # SQLite Database for user credentials
├── results.db                 # SQLite Database for prediction history
├── .env                       # Environment variables for API keys
├── requirements.txt           # Python dependencies
└── ... (other config files)
Deployment InformationThe MDPS is designed for cloud-based deployment, taking advantage of Streamlit's simple hosting model.Platform: Streamlit Cloud (formerly Streamlit Sharing).Database Setup: Uses SQLite for simplicity, which persists data across sessions in Streamlit Cloud's single-server environment (note: this may be volatile on scaled/multi-instance deployments).Run Command (runtime.txt or equivalent): streamlit run app.pyAcknowledgments and Datasets UsedThe underlying machine learning models were trained using publicly available datasets commonly used in medical ML studies.Diabetes Prediction: Pima Indians Diabetes Database (UCI Machine Learning Repository)Heart Disease Prediction: Cleveland Heart Disease Dataset (UCI Machine Learning Repository)Parkinson's Prediction: Parkinson's Disease Speech Features Data Set (UCI Machine Learning Repository)Nutrition Data: Powered by the Nutritionix API.
