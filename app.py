# ===========================
# IMPORTS
# ===========================
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os

# ===========================
# FLASK APP INITIALIZATION
# ===========================
app = Flask(__name__, static_folder='.')

# ===========================
# SIMPLE CORS
# ===========================
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# ===========================
# DATABASE SETUP
# ===========================
DATABASE = 'database.db'

def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            village TEXT NOT NULL,
            diarrhea INTEGER NOT NULL,
            fever INTEGER NOT NULL,
            rainfall TEXT NOT NULL,
            risk TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ===========================
# RULE-BASED LOGIC
# ===========================
def calculate_risk(diarrhea, rainfall):
    if diarrhea > 10 and rainfall == 'High':
        return 'High Risk'
    elif 5 <= diarrhea <= 10:
        return 'Medium Risk'
    else:
        return 'Safe'

# ===========================
# STATIC + FRONTEND
# ===========================
@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory('.', filename)

# ===========================
# API ENDPOINTS
# ===========================
@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit_data():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        data = request.get_json()
        village = data.get('village')
        diarrhea = int(data.get('diarrhea'))
        fever = int(data.get('fever'))
        rainfall = data.get('rainfall')

        risk = calculate_risk(diarrhea, rainfall)
        date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO health_data
            (village, diarrhea, fever, rainfall, risk, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (village, diarrhea, fever, rainfall, risk, date))
        conn.commit()
        conn.close()

        return jsonify(success=True, risk=risk), 201

    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/data', methods=['GET'])
def get_data():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM health_data ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            "id": r[0],
            "village": r[1],
            "diarrhea": r[2],
            "fever": r[3],
            "rainfall": r[4],
            "risk": r[5],
            "date": r[6]
        })

    return jsonify(result), 200

# ===========================
# RAILWAY STARTUP (ONLY ONE)
# ===========================
if __name__ == "__main__":
    init_database()
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
