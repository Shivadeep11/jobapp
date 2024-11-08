import sqlite3

def init_db():
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    
    # Create 'users' table for storing user credentials
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')

    # Create 'job_applications' table for storing job applications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            company_name TEXT NOT NULL,
            position TEXT NOT NULL,
            application_date DATE,
            status TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database and tables created.")
