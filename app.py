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

        # Validate that username and password are not empty
        if not username or not password:
            flash("Both username and password are required.")
            return redirect(url_for('register'))

        # Connect to the database and check for existing username
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            flash("Username already exists. Please choose another.")
            return redirect(url_for('register'))

        # Hash the password securely
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
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

        # Check if both username and password are provided
        if not username or not password:
            flash("Both username and password are required.")
            return redirect(url_for('login'))

        # Connect to the database to validate credentials
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        # Validate user credentials
        if user and check_password_hash(user[2], password):  # Assuming the password is stored as a hash
            session['username'] = username
            session['user_id'] = user[0]  # Assuming the first column is the user's ID
            flash("Logged in successfully!")
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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        flash("Please log in to access the dashboard.")
        return redirect(url_for('login'))
    
    # Get search and filter parameters from the request
    filter_status = request.args.get('status')
    search_query = request.args.get('query')

    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    
    # Base SQL query
    query = "SELECT * FROM job_applications WHERE user_id = ?"
    params = [session['user_id']]

    # Apply search filter if provided
    if search_query:
        query += " AND (company_name LIKE ? OR position LIKE ?)"
        params.extend([f'%{search_query}%', f'%{search_query}%'])

    # Apply status filter if provided
    if filter_status:
        query += " AND status = ?"
        params.append(filter_status)

    # Execute the query
    cursor.execute(query, params)
    applications = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html', applications=applications, filter_status=filter_status, search_query=search_query)


@app.route('/add_application', methods=['GET', 'POST'])
def add_application():
    # Ensure the user is logged in
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

        # Insert into the existing table 'job_applications'
        cursor.execute("""
            INSERT INTO job_applications (user_id, company_name, position, application_date, status)
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_id'], company_name, position, application_date, status))
        
        conn.commit()
        conn.close()

        flash("Job application added successfully!")
        return redirect(url_for('dashboard'))

    return render_template('add_application.html')

@app.route('/edit_application/<int:id>', methods=['GET', 'POST'])
def edit_application(id):
    # Ensure the user is logged in
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
    # Ensure the user is logged in
    if 'user_id' not in session:
        flash("Please log in to delete a job application.")
        return redirect(url_for('login'))

    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()

    # Ensure the application exists and belongs to the logged-in user
    cursor.execute("SELECT * FROM job_applications WHERE id = ? AND user_id = ?", (id, session['user_id']))
    application = cursor.fetchone()

    if not application:
        conn.close()
        flash("Job application not found or you don't have permission to delete it.")
        return redirect(url_for('dashboard'))

    # Delete the application
    cursor.execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()

    flash("Job application deleted successfully!")
    return redirect(url_for('dashboard'))


# Run the app with debug mode enabled
if __name__ == '__main__':
    app.run(debug=True)
