from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a strong secret key for session management

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Connect to the database and insert the new user
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("Username already exists.")
            return redirect(url_for('register'))

        # Insert the new user with hashed password
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                       (username, hashed_password))
        conn.commit()
        conn.close()

        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route (you'll implement this in the next steps)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the database and check user credentials
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):  # Assuming password is in the third column
            session['user_id'] = user[0]
            session['username'] = username
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.")
            return redirect(url_for('login'))

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))
    
    return render_template('dashboard.html')  # Ensure you have a dashboard.html template

# Run the app with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
