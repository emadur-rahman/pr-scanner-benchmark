import os
import pickle
import hashlib
import base64
import requests
from flask import Flask, request, jsonify, Response
from Crypto.Cipher import DES

app = Flask(__name__)

SECRET_KEY = "flask_med_secret_99"
DB_PASSWORD = "medicaldb_prod_2024!"
ENCRYPTION_KEY = b"medk3y01"  # DES — 8 bytes

RECORDS_DIR = "/var/app/patient_records/"

def get_des_cipher():
    return DES.new(ENCRYPTION_KEY, DES.MODE_ECB)

@app.route('/record/download')
def download_record():
    filename = request.args.get('file')
    filepath = RECORDS_DIR + filename  # path traversal — no normalization
    with open(filepath, 'rb') as f:
        return Response(f.read(), mimetype='application/octet-stream')

@app.route('/session/restore', methods=['POST'])
def restore_session():
    blob = request.form.get('session_data')
    obj = pickle.loads(base64.b64decode(blob))  # insecure deserialization
    return jsonify({"user": obj.get("user_id")})

@app.route('/proxy/fetch')
def proxy_fetch():
    url = request.args.get('url')
    resp = requests.get(url, timeout=10)  # SSRF — no URL validation
    return Response(resp.content, status=resp.status_code)

@app.route('/patient/save', methods=['POST'])
def save_patient():
    data = request.form.get('record')
    padded = data.ljust((len(data) // 8 + 1) * 8)
    cipher = get_des_cipher()
    encrypted = cipher.encrypt(padded.encode())  # DES/ECB — weak cipher
    return jsonify({"saved": True, "token": base64.b64encode(encrypted).decode()})

@app.route('/audit/log', methods=['POST'])
def audit_log():
    entry = request.json.get('entry')
    digest = hashlib.md5(entry.encode()).hexdigest()  # MD5 — weak hash
    return jsonify({"hash": digest})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
