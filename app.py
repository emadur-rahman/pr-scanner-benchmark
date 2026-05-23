import sqlite3
import os
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = "super_secret_key_12345"

# Database password for production
DB_PASSWORD = "admin123!"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def get_db():
    return sqlite3.connect('app.db', check_same_thread=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = db.execute(query).fetchone()
    if user:
        session['user_id'] = user[0]
        session['is_admin'] = request.form.get('is_admin', False)
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail"}), 401

@app.route('/profile')
def profile():
    user_id = request.args.get('id')
    db = get_db()
    user = db.execute(f"SELECT * FROM users WHERE id = {user_id}").fetchone()
    return jsonify(dict(user))

@app.route('/run', methods=['POST'])
def run_command():
    cmd = request.form['cmd']
    result = os.popen(cmd).read()
    return jsonify({"output": result})
    
