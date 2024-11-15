from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  

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
    
    # Retrieve job applications for the logged-in user
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_applications WHERE user_id = ?", (session['user_id'],))
    applications = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', applications=applications)

@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    if 'user_id' not in session:
        flash("Please log in to add a job application.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        company_name = request.form['company_name']
        position = request.form['position']
        application_date = request.form['application_date']
        status = request.form['status']

        # Insert the new job application into the database
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO job_applications (user_id, company_name, position, application_date, status) VALUES (?, ?, ?, ?, ?)",
                       (session['user_id'], company_name, position, application_date, status))
        conn.commit()
        conn.close()

        flash("Job application added successfully!")
        return redirect(url_for('dashboard'))

    return render_template('add_application.html')
@app.route('/edit_application/<int:id>', methods=['GET', 'POST'])
def edit_application(id):
    if 'user_id' not in session:
        flash("Please log in to edit a job application.")
        return redirect(url_for('login'))

    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()

    # Retrieve the existing application details
    cursor.execute("SELECT * FROM job_applications WHERE id = ? AND user_id = ?", (id, session['user_id']))
    application = cursor.fetchone()

    if not application:
        flash("Job application not found or you don't have permission to edit it.")
        conn.close()
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Get updated information from the form
        company_name = request.form['company_name']
        position = request.form['position']
        application_date = request.form['application_date']
        status = request.form['status']

        # Update the job application in the database
        cursor.execute("""
            UPDATE job_applications
            SET company_name = ?, position = ?, application_date = ?, status = ?
            WHERE id = ? AND user_id = ?
        """, (company_name, position, application_date, status, id, session['user_id']))
        conn.commit()
        conn.close()

        flash("Job application updated successfully!")
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_application.html', application=application)
@app.route('/delete_application/<int:id>', methods=['POST'])
def delete_application(id):
    if 'user_id' not in session:
        flash("Please log in to delete a job application.")
        return redirect(url_for('login'))

    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()

    # Check if the application exists and belongs to the logged-in user
    cursor.execute("SELECT * FROM job_applications WHERE id = ? AND user_id = ?", (id, session['user_id']))
    application = cursor.fetchone()

    if not application:
        flash("Job application not found or you don't have permission to delete it.")
        conn.close()
        return redirect(url_for('dashboard'))

    # Delete the job application
    cursor.execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()

    flash("Job application deleted successfully.")
    return redirect(url_for('dashboard'))

# Run the app with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
