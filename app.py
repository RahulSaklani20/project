from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import init_db, get_db
from auth import register_user, login_user, get_user_profile
from credit import reset_credits, deduct_credit, request_credits, approve_credits
from document import upload_document, get_matching_documents
from admin import get_analytics
import sqlite3
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure key
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists('database.db'):
    init_db()

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('profile'))
    return render_template('index.html')

# User registration
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if register_user(username, password):
            return redirect(url_for('login'))
        else:
            return "Registration failed. Username may already exist."
    return render_template('register.html')

# User login
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = login_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('profile'))
        else:
            return "Login failed. Invalid credentials."
    return render_template('login.html')

# User profile
@app.route('/user/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = get_user_profile(session['user_id'])
    return render_template('profile.html', user=user)

# Document upload and scan
@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        file = request.files['file']
        print(file, "file")
        if file and file.filename.endswith('.txt'):
            print("printing")
            # import uuid
            filename = str(uuid.uuid4())
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            if deduct_credit(session['user_id']):
                upload_document(session['user_id'], file_path)
                # conn = sqlite3.connect('database.db')
                conn = get_db()
                c = conn.cursor()
                c.execute('SELECT id FROM documents WHERE file_path = ?', (file_path,))
                print("executed")
                doc_id = c.fetchone()[0]
                # print(doc_id)
                matching_docs = get_matching_documents(doc_id)
                c.execute('INSERT INTO scans (user_id, document_id) VALUES (?, ?)', (session['user_id'], doc_id))
                # print("inserted")
                # Return the matching documents
                conn.commit()
                conn.close()
                return jsonify({
                    "message": "Document uploaded and scanned successfully",
                    "matching_documents": matching_docs
                })
            else:
                return "Insufficient credits."
        else:
            return "Invalid file format. Only .txt files are allowed."
    return render_template('scan.html')

# Get matching documents
@app.route('/matches/<int:doc_id>')
def matches(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    matching_docs = get_matching_documents(doc_id)
    return jsonify(matching_docs)

# Credit request
@app.route('/credits/request', methods=['GET', 'POST'])
def credit_request():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        requested_credits = int(request.form['credits'])
        request_credits(session['user_id'], requested_credits)
        return render_template('credit_request_success.html')
    return render_template('credit_request.html')

# Admin dashboard
@app.route('/admin/analytics')
def admin_analytics():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    analytics = get_analytics()
    return render_template('admin.html', analytics=analytics)

# Approve credit requests
@app.route('/admin/approve', methods=['POST'])
def admin_approve():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    request_id = int(request.form['request_id'])
    approve_credits(request_id)
    return "Credit request approved."

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/credit-requests')
def admin_credit_requests():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Fetch pending credit requests with usernames
    c.execute('''
        SELECT credit_requests.id, users.username, credit_requests.requested_credits
        FROM credit_requests
        JOIN users ON credit_requests.user_id = users.id
        WHERE credit_requests.status = 'pending'
    ''')
    pending_requests = c.fetchall()
    conn.close()
    
    return render_template('approve_credits.html', pending_requests=pending_requests)

@app.route('/admin/approve-request/<int:request_id>')
def approve_request(request_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Approve the request
    c.execute('UPDATE credit_requests SET status = "approved" WHERE id = ?', (request_id,))
    
    # Add credits to the user's account
    c.execute('''
        UPDATE users
        SET credits = credits + (SELECT requested_credits FROM credit_requests WHERE id = ?)
        WHERE id = (SELECT user_id FROM credit_requests WHERE id = ?)
    ''', (request_id, request_id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_credit_requests'))

@app.route('/admin/deny-request/<int:request_id>')
def deny_request(request_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Deny the request
    c.execute('UPDATE credit_requests SET status = "denied" WHERE id = ?', (request_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('admin_credit_requests'))

if __name__ == '__main__':
    app.run(debug=True)