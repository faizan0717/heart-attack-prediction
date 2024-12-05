from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import joblib
import os
import google.generativeai as genai
import re

# Load the model and scaler
model = joblib.load('heart_disease_model.pkl')
scaler = joblib.load('scaler.pkl')

genai.configure(api_key="")

# Create the model
generation_config = {
"temperature": 1,
"top_p": 0.95,
"top_k": 40,
"max_output_tokens": 8192,
"response_mime_type": "text/plain",
}

gemanimodel = genai.GenerativeModel(
model_name="gemini-1.5-flash",
generation_config=generation_config,
)

chat_session = gemanimodel.start_chat(
history=[
]
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    flash('Invalid credentials', 'danger')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/start_question')
def start_question():
    session.clear()  # Clear session data for a fresh start
    return redirect(url_for('question_age'))

# Define total number of questions
TOTAL_QUESTIONS = 13

@app.route('/question/age', methods=['GET', 'POST'])
def question_age():
    if request.method == 'POST':
        session['age'] = request.form['age']
        return redirect(url_for('question_cholesterol'))
    progress = int((1 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your age?", field_name="age", field_type="number", progress_percentage=progress)

@app.route('/question/cholesterol', methods=['GET', 'POST'])
def question_cholesterol():
    if request.method == 'POST':
        session['cholesterol'] = request.form['cholesterol']
        return redirect(url_for('question_bp'))
    progress = int((2 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your cholesterol level (mg/dL)?", field_name="cholesterol", field_type="number", progress_percentage=progress)

@app.route('/question/bp', methods=['GET', 'POST'])
def question_bp():
    if request.method == 'POST':
        session['bp'] = request.form['bp']
        return redirect(url_for('question_smoking'))
    progress = int((3 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your blood pressure (mmHg)?", field_name="bp", field_type="number", progress_percentage=progress)

@app.route('/question/smoking', methods=['GET', 'POST'])
def question_smoking():
    if request.method == 'POST':
        session['smoking'] = request.form['smoking']
        return redirect(url_for('question_activity'))
    progress = int((4 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="Do you smoke?", field_name="smoking", field_type="select", options=["yes", "no"], progress_percentage=progress)

@app.route('/question/activity', methods=['GET', 'POST'])
def question_activity():
    if request.method == 'POST':
        session['activity'] = request.form['activity']
        return redirect(url_for('question_diabetes'))
    progress = int((5 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your physical activity level?", field_name="activity", field_type="select", options=["sedentary", "moderate", "active"], progress_percentage=progress)

@app.route('/question/diabetes', methods=['GET', 'POST'])
def question_diabetes():
    if request.method == 'POST':
        session['diabetes'] = request.form['diabetes']
        return redirect(url_for('question_family_history'))
    progress = int((6 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="Do you have diabetes?", field_name="diabetes", field_type="select", options=["yes", "no"], progress_percentage=progress)

@app.route('/question/family_history', methods=['GET', 'POST'])
def question_family_history():
    if request.method == 'POST':
        session['family_history'] = request.form['family_history']
        return redirect(url_for('question_diet'))
    progress = int((7 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="Do you have a family history of heart disease?", field_name="family_history", field_type="select", options=["yes", "no"], progress_percentage=progress)

@app.route('/question/diet', methods=['GET', 'POST'])
def question_diet():
    if request.method == 'POST':
        session['diet'] = request.form['diet']
        return redirect(url_for('question_exercise'))
    progress = int((8 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your typical diet?", field_name="diet", field_type="select", options=["healthy", "unhealthy"], progress_percentage=progress)

@app.route('/question/exercise', methods=['GET', 'POST'])
def question_exercise():
    if request.method == 'POST':
        session['exercise'] = request.form['exercise']
        return redirect(url_for('question_sleep'))
    progress = int((9 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="How often do you exercise?", field_name="exercise", field_type="select", options=["daily", "weekly", "never"], progress_percentage=progress)

@app.route('/question/sleep', methods=['GET', 'POST'])
def question_sleep():
    if request.method == 'POST':
        session['sleep'] = request.form['sleep']
        return redirect(url_for('question_alcohol'))
    progress = int((10 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="How many hours of sleep do you get?", field_name="sleep", field_type="select", options=["<6", "6-8", ">8"], progress_percentage=progress)

@app.route('/question/alcohol', methods=['GET', 'POST'])
def question_alcohol():
    if request.method == 'POST':
        session['alcohol'] = request.form['alcohol']
        return redirect(url_for('question_sex'))
    progress = int((11 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="Do you consume alcohol?", field_name="alcohol", field_type="select", options=["yes", "no"], progress_percentage=progress)

@app.route('/question/sex', methods=['GET', 'POST'])
def question_sex():
    if request.method == 'POST':
        session['sex'] = request.form['sex']
        return redirect(url_for('question_stress'))
    progress = int((12 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your sex?", field_name="sex", field_type="select", options=["male", "female"], progress_percentage=progress)

@app.route('/question/stress', methods=['GET', 'POST'])
def question_stress():
    if request.method == 'POST':
        session['stress'] = request.form['stress']
        print("here")
        return redirect(url_for('result'))
    progress = int((13 / TOTAL_QUESTIONS) * 100)
    return render_template('question.html', question="What is your stress level?", field_name="stress", field_type="select", options=["low", "medium", "high"], progress_percentage=progress)

@app.route('/result')
def result():
    try:
        # Collect all data from the session
        age = int(session.get('age', 0))
        sex = 'Male' if session.get('sex', 'male') == 'male' else 'Female'
        cholesterol = int(session.get('cholesterol', 0))
        bp = int(session.get('bp', 0))
        smoking = 'Yes' if session.get('smoking', 'no') == 'yes' else 'No'
        activity = session.get('activity', 'Sedentary').lower()
        diabetes = 'Yes' if session.get('diabetes', 'no') == 'yes' else 'No'
        family_history = 'Yes' if session.get('family_history', 'no') == 'yes' else 'No'
        diet = 'Unhealthy' if session.get('diet', 'healthy') == 'unhealthy' else 'Healthy'
        exercise = session.get('exercise', 'Never').lower()
        sleep = session.get('sleep', '<6')
        alcohol = 'Yes' if session.get('alcohol', 'no') == 'yes' else 'No'
        stress = session.get('stress', 'low').lower()

        # Normalize activity and exercise inputs
        activity_list = ['sedentary', 'moderate', 'active']
        exercise_list = ['never', 'weekly', 'daily']
        stress_list = ['low', 'medium', 'high']
        sleep_list = ['<6', '6-8', '>8']

        # Handle normalization issues
        activity_index = activity_list.index(activity) if activity in activity_list else 0
        exercise_index = exercise_list.index(exercise) if exercise in exercise_list else 0
        stress_index = stress_list.index(stress) if stress in stress_list else 0
        sleep_index = sleep_list.index(sleep) if sleep in sleep_list else 0

        # Combine features into an array
        features = np.array([age, 1 if sex == 'Male' else 0, cholesterol, bp, 1 if smoking == 'Yes' else 0,
                             activity_index, 
                             1 if diabetes == 'Yes' else 0, 1 if family_history == 'Yes' else 0, 
                             1 if diet == 'Unhealthy' else 0, 
                             exercise_index, 
                             sleep_index, 1 if alcohol == 'Yes' else 0, 
                             stress_index]).reshape(1, -1)

        # Scale the features
        features_scaled = scaler.transform(features)

        # Predict risk using the ML model
        prediction = model.predict(features_scaled)[0]
        risk = "High" if prediction == 1 else "Low"

        # Summary dictionary for UI display
        summary = {
            "Age": age,
            "Sex": sex,
            "Cholesterol Level": cholesterol,
            "Blood Pressure": bp,
            "Smoking": smoking,
            "Physical Activity": activity.capitalize(),
            "Diabetes": diabetes,
            "Family History": family_history,
            "Diet": diet,
            "Exercise Frequency": exercise.capitalize(),
            "Sleep Duration": sleep,
            "Alcohol Consumption": alcohol,
            "Stress Level": stress.capitalize()
        }

        # Prepare input for generative AI
        summary_text = " - ".join(f"{key}: {value}" for key, value in summary.items())
        prompt = f"Based on the following details, give me dos and don'ts to avoid a heart attack based on the following detail, address the response to me:\n{summary_text}"

        # Use Generative AI to generate advice
        response = chat_session.send_message(prompt)
        advice = re.sub(r'\*\*(.*?)\:\*\*', r'\1: >>', response.text)
        # Render the result page
        return render_template('result.html', risk=risk, summary=summary, advice=advice.split("\n"))

    except Exception as e:
        print(f"An error occurred: {e}", "danger")
        return redirect(url_for('start_question'))



@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
