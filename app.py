# ===========================
# IMPORTS
# ===========================
from flask import Flask, request, jsonify, send_from_directory
import sqlite3
from datetime import datetime

# ===========================
# FLASK APP INITIALIZATION
# ===========================
app = Flask(__name__)

# Simple CORS headers (alternative to flask-cors)
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
    """Initialize SQLite database with health_data table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
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
    print("Database initialized successfully!")

# ===========================
# RULE-BASED AI LOGIC
# ===========================
def calculate_risk(diarrhea, rainfall):
    """
    Rule-based AI algorithm for risk prediction
    
    Logic:
    - High Risk: Diarrhea > 10 AND Rainfall is High
    - Medium Risk: Diarrhea between 5-10
    - Safe: Diarrhea < 5
    """
    if diarrhea > 10 and rainfall == 'High':
        return 'High Risk'
    elif 5 <= diarrhea <= 10:
        return 'Medium Risk'
    else:
        return 'Safe'

# ===========================
# API ENDPOINTS
# ===========================

# Serve static HTML files
@app.route('/')
def serve_index():
    """Serve index.html as home page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve other static files (HTML, CSS, JS)"""
    return send_from_directory('.', path)

# POST endpoint to submit health data
@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit_data():
    """
    Submit health data to database
    
    Expected JSON:
    {
        "village": "Village Name",
        "diarrhea": 12,
        "fever": 8,
        "rainfall": "High"
    }
    """
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        # Get data from request
        data = request.get_json()
        
        # Extract fields
        village = data.get('village')
        diarrhea = int(data.get('diarrhea'))
        fever = int(data.get('fever'))
        rainfall = data.get('rainfall')
        
        # Calculate risk using AI logic
        risk = calculate_risk(diarrhea, rainfall)
        
        # Get current date
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        # Insert into database
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO health_data (village, diarrhea, fever, rainfall, risk, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (village, diarrhea, fever, rainfall, risk, current_date))
        conn.commit()
        conn.close()
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Data submitted successfully',
            'risk': risk
        }), 201
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error submitting data'
        }), 500

# GET endpoint to retrieve all data
@app.route('/data', methods=['GET'])
def get_data():
    """
    Retrieve all health data from database
    
    Returns JSON array of all records
    """
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Fetch all records
        cursor.execute('SELECT * FROM health_data ORDER BY id DESC')
        rows = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'village': row[1],
                'diarrhea': row[2],
                'fever': row[3],
                'rainfall': row[4],
                'risk': row[5],
                'date': row[6]
            })
        
        return jsonify(data), 200
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify([]), 500

# ===========================
# ===========================
# RUN APPLICATION (RAILWAY SAFE)
# ===========================
if __name__ == "__main__":
    import os

    init_database()

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
