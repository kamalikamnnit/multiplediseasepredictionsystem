import streamlit as st
import bcrypt
import sqlite3
import pickle
from streamlit_option_menu import option_menu
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import os
import requests
from dotenv import load_dotenv
import hashlib
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
from datetime import datetime
import os
import base64


# ----------------- DATABASE INITIALIZATION FIX -----------------
def init_db():
        """Create results.db and predictions table if not exist."""
        conn = sqlite3.connect('results.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        disease TEXT,
                        result TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
        ''')
        conn.commit()
        conn.close()

# ✅ Call this function immediately to ensure DB setup on startup
init_db()
#initialse the cookie manager



load_dotenv()
#loading the saved models

diabetes_model = pickle.load(open('All_Models/diabetes_model.sav', 'rb'))

heart_disease_model = pickle.load(open('All_Models/heart_disease_model.sav', 'rb'))

parkinsons_model = pickle.load(open('All_Models/parkinsons_model.sav', 'rb'))


class NutritionAnalyzer:
        def __init__(self):
                self.app_id = os.getenv('NUTRITIONIX_APP_ID')
                self.api_key = os.getenv('NUTRITIONIX_API_KEY')
                self.base_url = "https://trackapi.nutritionix.com/v2/"

        def get_nutrition(self, food_name, quantity=1, unit=""):
                """Get nutrition facts for a food item"""
                endpoint = "natural/nutrients"
                headers = {
                        "x-app-id": self.app_id,
                        "x-app-key": self.api_key,
                        "Content-Type": "application/json"
                }

                query = f"{quantity} {unit} {food_name}".strip() if unit else food_name

                payload = {"query": query, "timezone": "US/Eastern"}

                try:
                        response = requests.post(
                                f"{self.base_url}{endpoint}",
                                headers=headers,
                                json=payload
                        )
                        response.raise_for_status()

                        data = response.json()
                        if not data.get('foods'):
                                return {"error": "No nutrition data found for this food"}

                        food_data = data['foods'][0]

                        nutrition = {
                                "food_name": food_data.get('food_name', ''),
                                "serving_qty": food_data.get('serving_qty', 1),
                                "serving_unit": food_data.get('serving_unit', 'serving'),
                                "calories": food_data.get('nf_calories', 0),
                                "total_fat": food_data.get('nf_total_fat', 0),
                                "protein": food_data.get('nf_protein', 0),
                                "carbs": food_data.get('nf_total_carbohydrate', 0),
                                "sugars": food_data.get('nf_sugars', 0),
                                "fiber": food_data.get('nf_dietary_fiber', 0),
                        }

                        return nutrition

                except requests.exceptions.RequestException as e:
                        return {"error": f"API request failed: {str(e)}"}



# ----------------- DATABASE SETUP -----------------
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()


def create_users_table():
        c.execute('''CREATE TABLE IF NOT EXISTS users (
                                        username TEXT PRIMARY KEY,
                                        name TEXT,
                                        age INTEGER,
                                        height REAL,
                                        weight REAL,
                                        password TEXT
                                )''')
        conn.commit()

def add_user(username, name, age, height, weight, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        c.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                            (username, name, age, height, weight, hashed_password))
        conn.commit()

def login_user(username, password):
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[5]):
                return user
        return None


#prediction database

def save_result(username,disease,result):
        conn = sqlite3.connect('results.db', check_same_thread = False)
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        disease TEXT,
                        result TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
        ''')
        cursor.execute('''
                                    INSERT INTO predictions (username, disease, result)
                VALUES (?, ?, ?)
                ''',(username, disease, result))
        conn.commit()
        print("[DEBUG] Prediction saved successfully to results.db")
        conn.close()



def get_user_predictions(username):
        conn = sqlite3.connect('results.db')
        cursor = conn.cursor()
        cursor.execute('SELECT disease, result, timestamp FROM predictions WHERE username=?', (user[1],))
        data = cursor.fetchall()
        conn.close()
        return pd.DataFrame(data, columns=['Disease', 'Result', 'Timestamp'])






def create_pdf_report(user, df, chart_data, bar_chart_path, timeline_fig_path):
        # Initialize PDF
        pdf = FPDF()
        pdf.add_page()

        # Try to use DejaVu (Unicode support), fallback to Arial
        pdf.set_font("Arial", "", 12)
        df['Result'] = df['Result'].astype(str).str.replace("✅", "Yes").str.replace("❌", "No")

        # --- PDF Content Generation ---
        pdf.cell(200, 10, txt=f"Health Report for {user[1]}", ln=True)
        pdf.ln(5)

        # User info
        pdf.cell(200, 10, txt=f"Age: {user[2]}, Height: {user[3]} cm, Weight: {user[4]} kg", ln=True)

        # Prediction History
        pdf.ln(10)
        pdf.cell(200, 10, txt="Prediction History:", ln=True)
        for _, row in df.iterrows():
                timestamp = row['Timestamp'].strftime('%Y-%m-%d %H:%M') if hasattr(row['Timestamp'], 'strftime') else str(row['Timestamp'])
                disease = str(row['Disease'])
                result = str(row['Result'])
                text = f"{timestamp} - {disease} - {result}"
                pdf.cell(200, 10, txt=text, ln=True)

        # Add charts if they exist
        if os.path.exists(bar_chart_path):
                pdf.add_page()
                pdf.cell(200, 10, txt="Disease Probability Distribution", ln=True)
                pdf.image(bar_chart_path, w=180)

        if os.path.exists(timeline_fig_path):
                pdf.add_page()
                pdf.cell(200, 10, txt="Detection Timeline", ln=True)
                pdf.image(timeline_fig_path, w=180)

        # Return PDF as bytes (for download)
        return pdf.output(dest='S')
# ----------------- MAIN APP -----------------
st.set_page_config(page_title="Multiple Disease Prediction", layout="wide")
create_users_table()

if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

st.title("🩺 Multiple Disease Prediction System")

# ----------------- SIDEBAR -----------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if not st.session_state.logged_in:

        if choice == "Register":
                st.subheader("Create New Account")
                username = st.text_input("Username")
                name = st.text_input("Full Name")
                age = st.number_input("Age", min_value=1)
                height = st.number_input("Height (cm)")
                weight = st.number_input("Weight (kg)")
                password = st.text_input("Password", type='password')

                if st.button("Register"):
                        try:
                                add_user(username, name, age, height, weight, password)
                                st.success("Registered successfully! Please log in.")
                        except:
                                st.error("Username already exists. Try a different one.")

        elif choice == "Login":
                st.subheader("Login to Your Account")
                username = st.text_input("Username")
                password = st.text_input("Password", type='password')

                if st.button("Login"):
                        user = login_user(username, password)
                        if user:
                                st.success(f"Welcome {user[1]} 👋")
                                st.session_state.logged_in = True
                                st.session_state.user_data = user
                                st.rerun()
                        else:
                                st.error("Invalid credentials. Please try again.")

else:
        # ----------------- USER  -----------------
        user = st.session_state.user_data
        st.sidebar.success(f"Logged in as {user[0]}")

        # ----------------- MAIN TABS -----------------
        tab = st.selectbox("🔍 What would you like to explore?", 
                                            ["Disease Predictions", "Diet & Nutrition", "Logout"])

        if tab == "Disease Predictions":
                st.subheader("🔬 Disease Prediction")
                with st.sidebar:

                        selected = option_menu('Multiple Disease Prediction System', 

                                                                    [ '🧮 BMI',
                                                                        'Diabetes Prediction',
                                                                    'Heart Disease Prediction',
                                                                    'Parkinsons Prediction',
                                                                        'User Profile'],  # Added new option   
                                                                    icons = ['🧮','activity','heart','person'],
                                                                    default_index = 0)



                # Diabetes Prediction Page
                if selected == 'Diabetes Prediction':

                        # page title
                        st.title('Diabetes Prediction using ML')

                        # getting the input data from the user
                        col1, col2, col3 = st.columns(3)

                        with col1:
                                Pregnancies = st.text_input('Number of Pregnancies')

                        with col2:
                                Glucose = st.text_input('Glucose Level')

                        with col3:
                                BloodPressure = st.text_input('Blood Pressure value')

                        with col1:
                                SkinThickness = st.text_input('Skin Thickness value')

                        with col2:
                                Insulin = st.text_input('Insulin Level')

                        with col3:
                                BMI = st.text_input('BMI value')

                        with col1:
                                DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')

                        with col2:
                                Age = st.text_input('Age of the Person')


                        # code for Prediction
                        diab_diagnosis = ''

                        # creating a button for Prediction

                        if st.button('Diabetes Test Result'):

                                user_input = [Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin,
                                                            BMI, DiabetesPedigreeFunction, Age]

                                user_input = [float(x) for x in user_input]

                                diab_prediction = diabetes_model.predict([user_input])

                                if diab_prediction[0] == 1:
                                        diab_diagnosis = 'The person is diabetic'
                                else:
                                        diab_diagnosis = 'The person is not diabetic'

                                st.success(diab_diagnosis)
                                save_result(username=user[1], disease="Diabetes", result=diab_diagnosis)

                # Heart Disease Prediction Page
                if selected == 'Heart Disease Prediction':

                        # page title
                        st.title('Heart Disease Prediction using ML')

                        col1, col2, col3 = st.columns(3)

                        with col1:
                                age = st.text_input('Age')

                        with col2:
                                sex = st.text_input('Sex')

                        with col3:
                                cp = st.text_input('Chest Pain types')

                        with col1:
                                trestbps = st.text_input('Resting Blood Pressure')

                        with col2:
                                chol = st.text_input('Serum Cholestoral in mg/dl')

                        with col3:
                                fbs = st.text_input('Fasting Blood Sugar > 120 mg/dl')

                        with col1:
                                restecg = st.text_input('Resting Electrocardiographic results')

                        with col2:
                                thalach = st.text_input('Maximum Heart Rate achieved')

                        with col3:
                                exang = st.text_input('Exercise Induced Angina')

                        with col1:
                                oldpeak = st.text_input('ST depression induced by exercise')

                        with col2:
                                slope = st.text_input('Slope of the peak exercise ST segment')

                        with col3:
                                ca = st.text_input('Major vessels colored by flourosopy')

                        with col1:
                                thal = st.text_input('thal: 0 = normal; 1 = fixed defect; 2 = reversable defect')

                        # code for Prediction
                        heart_diagnosis = ''

                        # creating a button for Prediction

                        if st.button('Heart Disease Test Result'):

                                user_input = [age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal]

                                user_input = [float(x) for x in user_input]

                                heart_prediction = heart_disease_model.predict([user_input])

                                if heart_prediction[0] == 1:
                                        heart_diagnosis = 'The person is having heart disease'
                                else:
                                        heart_diagnosis = 'The person does not have any heart disease'

                                st.success(heart_diagnosis)
                                save_result(username=user[1], disease="Heart Disease", result=heart_diagnosis)


                if selected == '🧮 BMI':
                        #title
                        st.title("💪 BMI Calculator with Health Insights & Diet Tips")


                        #user input
                        st.header("📋 Enter Your Info")
                        weight = st.number_input("Weight (kg)", min_value=1.0, step  = 0.1)
                        height = st.number_input("Height (cm)", min_value=1.0, step = 0.1)

                        if st.button("Calculate BMI"):
                                height_m = height/100
                                bmi = weight / (height_m ** 2)
                                st.subheader(f"🧮 Your BMI is: `{bmi:.2f}`")

                                if bmi < 18.5:
                                 category = "Underweight"
                                 risks = "- Malnutrition\n- Weakened immunity\n- Osteoporosis"
                                 diet = """
                                 🍽️ **Diet Suggestions**:
                                 - Eat calorie-rich meals (nuts, dry fruits, whole milk)
                                 - Add more protein (eggs, legumes, lean meats)
                                 - Healthy fats: avocado, cheese, peanut butter
                                 - Frequent small meals & smoothies
                                    """
                                 color = "yellow"
                                elif 18.5 <= bmi < 24.9:
                                 category = "Normal"
                                 risks = "- Low risk (stay consistent!)"
                                 diet = """
                                 🍽️ **Diet Suggestions**:
                                 - Balanced diet with whole grains, fruits & vegetables
                                 - Lean protein: tofu, chicken, fish
                                 - Regular exercise & hydration
                                """
                                 color = "green"
                                elif 25 <= bmi < 29.9:
                                 category = "Overweight"
                                 risks = "- High blood pressure\n- Type 2 diabetes\n- Joint pain"
                                 diet = """
                                 🍽️ **Diet Suggestions**:
                                 - Cut back on sugar & processed foods
                                 - Include more fiber-rich veggies
                                 - Use olive oil instead of butter
                                 - Start a light cardio workout routine
                                """
                                 color = "orange"
                        else:
                                category = "Obese"
                                risks = "- Heart disease\n- Diabetes\n- Sleep apnea\n- Fatty liver"
                                diet = """
                                🍽️ **Diet Suggestions**:
                                - High-fiber, low-carb meals
                                - Avoid fried and sugary foods
                                - Consult a dietician if needed
                                - Begin with walking or yoga daily
                                """
                                color = "red"

                                #Display results
                        st.markdown(f"### 📊 Category: **{category}**")
                        st.markdown(f"#### ⚠️ Possible Health Risks:")
                        st.markdown(f"<div style='color:{color};font-size:16px'>{risks}</div>", unsafe_allow_html=True)
                        st.markdown("---")
                        st.markdown(diet)


                # Parkinson's Prediction Page
                if selected == "Parkinsons Prediction":

                        # page title
                        st.title("Parkinson's Disease Prediction using ML")

                        col1, col2, col3, col4, col5 = st.columns(5)

                        with col1:
                                fo = st.text_input('MDVP:Fo(Hz)')

                        with col2:
                                fhi = st.text_input('MDVP:Fhi(Hz)')

                        with col3:
                                flo = st.text_input('MDVP:Flo(Hz)')

                        with col4:
                                Jitter_percent = st.text_input('MDVP:Jitter(%)')

                        with col5:
                                Jitter_Abs = st.text_input('MDVP:Jitter(Abs)')

                        with col1:
                                RAP = st.text_input('MDVP:RAP')

                        with col2:
                                PPQ = st.text_input('MDVP:PPQ')

                        with col3:
                                DDP = st.text_input('Jitter:DDP')

                        with col4:
                                Shimmer = st.text_input('MDVP:Shimmer')

                        with col5:
                                Shimmer_dB = st.text_input('MDVP:Shimmer(dB)')

                        with col1:
                                APQ3 = st.text_input('Shimmer:APQ3')

                        with col2:
                                APQ5 = st.text_input('Shimmer:APQ5')

                        with col3:
                                APQ = st.text_input('MDVP:APQ')

                        with col4:
                                DDA = st.text_input('Shimmer:DDA')

                        with col5:
                                NHR = st.text_input('NHR')

                        with col1:
                                HNR = st.text_input('HNR')

                        with col2:
                                RPDE = st.text_input('RPDE')

                        with col3:
                                DFA = st.text_input('DFA')

                        with col4:
                                spread1 = st.text_input('spread1')

                        with col5:
                                spread2 = st.text_input('spread2')

                        with col1:
                                D2 = st.text_input('D2')

                        with col2:
                                PPE = st.text_input('PPE')

                        # code for Prediction
                        parkinsons_diagnosis = ''

                        # creating a button for Prediction    
                        if st.button("Parkinson's Test Result"):

                                user_input = [fo, fhi, flo, Jitter_percent, Jitter_Abs,
                                                            RAP, PPQ, DDP,Shimmer, Shimmer_dB, APQ3, APQ5,
                                                            APQ, DDA, NHR, HNR, RPDE, DFA, spread1, spread2, D2, PPE]

                                user_input = [float(x) for x in user_input]

                                parkinsons_prediction = parkinsons_model.predict([user_input])

                                if parkinsons_prediction[0] == 1:
                                        parkinsons_diagnosis = "The person has Parkinson's disease"
                                else:
                                        parkinsons_diagnosis = "The person does not have Parkinson's disease"

                                st.success(parkinsons_diagnosis)
                                save_result(username=user[1], disease="Parkinsons Disease", result=parkinsons_diagnosis) 


                if selected == 'User Profile':
                            st.title("User Profile & History")
                            
# Show basic info
                            st.subheader("Welcome, " + user[1])
                            st.write(f"Age: {user[2]}, Height: {user[3]} cm, Weight: {user[4]} kg")
                            # ----------------- BMI CALCULATION -----------------
                            height_m = user[3] / 100
                            bmi = round(user[4] / (height_m ** 2), 2)
                            st.write(f"**BMI:** {bmi}")

                            if bmi < 18.5:
                               st.warning("Underweight")
                            elif 18.5 <= bmi < 24.9:
                               st.success("Healthy")
                            elif 25 <= bmi < 29.9:
                               st.warning("Overweight")
                            else:
                               st.error("Obese")

# Fetch prediction history
                            df = get_user_predictions(user[0])  # user[0] is the username

                            if df.empty:
                                st.warning("No prediction data found.")
                            else:
                                st.subheader("Prediction History")

        # Show as a table
                                st.dataframe(df)

        # Convert result text to categorical label
                                df['Label'] = df['Result'].apply(lambda x: 1 if "not" not in x.lower() else 0)

        # Plot bar chart: Number of disease detections
                                chart_data = df.groupby('Disease')['Label'].sum().reset_index()

                                st.subheader("Disease Detection Summary")

                                fig, ax = plt.subplots()
                                sns.barplot(x='Disease', y='Label', data=chart_data, ax=ax)
                                ax.set_ylabel("Number of Positive Detections")
                                st.pyplot(fig)

        # Optional: Line graph for timeline
                                df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                                df_sorted = df.sort_values(by='Timestamp')

                                st.subheader("Detection Timeline")
                                fig2, ax2 = plt.subplots()
                                sns.lineplot(x='Timestamp', y='Label', hue='Disease', data=df_sorted, marker="o", ax=ax2)
                                ax2.set_ylabel("Positive (1) / Negative (0)")
                                st.pyplot(fig2)

                                timeline_fig_path = "timeline_chart.png"
                                fig2.savefig(timeline_fig_path)

                                bar_chart_path = "bar_chart.png"
                                fig.savefig(bar_chart_path)


                                if st.button("📄 Generate PDF Report"):
       
                                    try:
                                 # Generate PDF (returns bytes)
                                        pdf_bytes = create_pdf_report(user, df_sorted, chart_data, bar_chart_path, timeline_fig_path)

                # Create download link (NO .encode() on pdf_bytes!)
                                        st.success("✅ Report generated! Click below to download.")
                                        st.markdown(
                                        f'<a href="data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode()}" download="health_report.pdf">📥 Download Report</a>',
                                        unsafe_allow_html=True)
                
                                    except Exception as e:
                                        st.error(f"Error generating PDF: {str(e)}")





        elif tab == "Diet & Nutrition":
                st.subheader("🍽️ Diet Recommendations & Nutrient Analysis")
                analyzer = NutritionAnalyzer()

                col1, col2, col3 = st.columns(3)

                with col1:
                        food_item = st.text_input('Food Item', placeholder='e.g., banana, chicken breast')

                with col2:
                        quantity = st.number_input('Quantity', min_value=0.1, value=1.0, step=0.1)

                with col3:
                        unit = st.selectbox('Unit', ['', 'g', 'oz', 'cup', 'tbsp', 'tsp', 'ml', 'serving'])

                if st.button('Analyze Nutrition'):
                        if not food_item:
                                st.error("Please enter a food item")
                        else:
                                with st.spinner('Analyzing nutrition...'):
                                        result = analyzer.get_nutrition(food_item, quantity, unit)

                                        if "error" in result:
                                                st.error(result["error"])
                                        else:
                                                st.success(f"Nutrition Facts for {result['food_name']} ({quantity}{unit if unit else ' serving'})")

                                                # Display results in a clean format
                                                st.subheader("Macronutrients")
                                                col1, col2, col3 = st.columns(3)
                                                col1.metric("Calories", f"{result['calories']} kcal")
                                                col2.metric("Protein", f"{result['protein']}g")
                                                col3.metric("Carbohydrates", f"{result['carbs']}g")

                                                st.subheader("Detailed Information")
                                                st.write(f"**Total Fat:** {result['total_fat']}g")
                                                st.write(f"**Sugars:** {result['sugars']}g")
                                                st.write(f"**Fiber:** {result['fiber']}g")

                                                # Add a visual element
                                                st.progress(result['calories'] / 2000)  # Assuming 2000 kcal as reference
                                                st.caption(f"{result['calories']} kcal ({result['calories']/2000:.0%} of daily 2000 kcal reference)")


        elif tab == "Logout":
                st.session_state.logged_in = False
                st.session_state.user_data = None
                st.success("You have been logged out.")
                st.rerun()

        





