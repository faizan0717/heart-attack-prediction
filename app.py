from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# In-memory users storage for simplicity
users_db = {}

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = users_db.get(username)
    if user and check_password_hash(user['password'], password):
        session['user'] = username
        flash('Login successful!', 'success')
        return redirect(url_for('home'))
    flash('Invalid credentials', 'danger')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        
        if username in users_db:
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        
        users_db[username] = {'username': username, 'password': password}
        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'user' not in session:
        flash('Please login first', 'danger')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Collecting form data
        age = request.form.get('age')
        cholesterol = request.form.get('cholesterol')
        bp = request.form.get('bp')
        smoking = request.form.get('smoking')
        activity = request.form.get('activity')
        diabetes = request.form.get('diabetes')
        family_history = request.form.get('family_history')
        
        # Mock prediction logic (randomized)
        risk_factors = [smoking, diabetes, family_history, activity]
        risk_level = random.choice(['Low', 'Medium', 'High'])
        
        # Increase risk if user has diabetes, family history, or is a smoker
        if any(factor == 'yes' for factor in risk_factors):
            risk_level = 'High' if random.random() > 0.5 else 'Medium'
        
        # Decrease risk if user is active
        if activity == 'active':
            risk_level = 'Low' if risk_level == 'Medium' else risk_level
        
        return render_template('result.html', risk=risk_level)
    
    return render_template('home.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

