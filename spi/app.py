import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('gas_data.db')  
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GasLevels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            gas_level INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
init_db()



from twilio.rest import Client
from flask import Flask, request, render_template, jsonify
import requests

app = Flask(__name__)

# add your details here

TWILIO_ACCOUNT_SID = ''
TWILIO_AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''
USER_PHONE_NUMBER = '' 


THINGSPEAK_WRITE_API_KEY = ''
THINGSPEAK_CHANNEL_ID = ''

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

latest_gas_level = 0

def log_to_database(gas_level):
    conn = sqlite3.connect('gas_data.db')
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO GasLevels (timestamp, gas_level) VALUES (?, ?)", 
                   (datetime.now(), gas_level))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['GET'])
def update():
    global latest_gas_level
    gas_level = request.args.get('gasLevel', default=0, type=int)
    print(f"Gas Level received: {gas_level}")
    

    latest_gas_level = gas_level

    log_to_database(gas_level)
    log_to_thingspeak(gas_level)

    if gas_level > 320:
        send_sms_alert("Warning! Smoke Detected! Please evacuate the building immediately.")
    if gas_level > 325:
        make_call_alert()

    return jsonify({"status": "success", "gasLevel": gas_level})
    response.headers['Content-Type'] = 'application/json'  # Ensure the content type is application/json

    return response

@app.route('/history', methods=['GET'])
def history():
    conn = sqlite3.connect('gas_data.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT timestamp, gas_level FROM GasLevels ORDER BY timestamp DESC LIMIT 100")
    data = cursor.fetchall()
    
    conn.close()
    
    history_data = [{"timestamp": row[0], "gas_level": row[1]} for row in data]
    
    return jsonify(history_data)

@app.route('/latest_gas_level', methods=['GET'])
def latest_gas_level_endpoint():
    return jsonify({"gasLevel": latest_gas_level})
@app.route('/history')
def history_page():
    return render_template('history.html')

def send_sms_alert(message):
    try:
        message = client.messages.create(
            body=message, 
            from_=TWILIO_PHONE_NUMBER,
            to=USER_PHONE_NUMBER 
        )
        print(f"SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def make_call_alert():
    try:
        call = client.calls.create(
            to=USER_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url="http://demo.twilio.com/docs/voice.xml"  
        )
        print(f"Call initiated successfully: {call.sid}")
    except Exception as e:
        print(f"Error making call: {e}")


def log_to_thingspeak(gas_level):

    url = f'https://api.thingspeak.com/update?api_key=27ZGJY27TXFP9MX0&field1={gas_level}'


    response = requests.get(url, params={
        'field1': gas_level,  
    })
    
    if response.status_code == 200:
        print("Successfully logged data to ThingSpeak")
    else:
        print(f"Failed to log data to ThingSpeak: {response.status_code}")

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=8080, debug=True)
