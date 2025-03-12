from flask import Flask, render_template, jsonify, request, send_from_directory
import os
import requests
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder='static')

# Your Daily.co settings
DAILY_API_KEY = '078c49371d0577a614346b0aaf3f8110eaab590fcefc49cc8b4a3d077b112742'
DAILY_API_URL = 'https://api.daily.co/v1'
DAILY_SUBDOMAIN = 'translator'

@app.route('/static/signs/<path:filename>')
def serve_sign(filename):
    try:
        return send_from_directory('static/signs', filename)
    except Exception as e:
        print(f"Error serving sign image: {str(e)}")
        return jsonify({'error': 'Image not found'}), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/create-room', methods=['POST'])
def create_room():
    try:
        # Create a unique room name
        room_name = f'room-{datetime.now().strftime("%Y%m%d-%H%M%S")}'
        
        # Debug print
        print(f"Creating room: {room_name}")
        
        # Room settings - keep it simple for free plan
        properties = {
            'name': room_name,
            'privacy': 'public',
            'properties': {
                'exp': int((datetime.now() + timedelta(hours=1)).timestamp()),
                'enable_chat': True,
                'enable_screenshare': True
            }
        }
        
        # Debug print
        print(f"Request payload: {json.dumps(properties, indent=2)}")
        
        # Create the room
        headers = {
            'Authorization': f'Bearer {DAILY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Debug print
        print(f"Making request to: {DAILY_API_URL}/rooms")
        
        response = requests.post(
            f'{DAILY_API_URL}/rooms',
            json=properties,
            headers=headers
        )
        
        # Debug print
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            try:
                room_data = json.loads(response.text)
                room_url = f'https://{DAILY_SUBDOMAIN}.daily.co/{room_name}'
                return jsonify({
                    'success': True,
                    'room_url': room_url,
                    'room_name': room_name
                })
            except json.JSONDecodeError as e:
                error_message = f"Failed to parse response JSON: {str(e)}"
                print(f"Error: {error_message}")
                print(f"Response content was: {response.text}")
                return jsonify({
                    'success': False,
                    'error': error_message
                }), 500
        else:
            error_message = f"Failed to create room. Status: {response.status_code}, Response: {response.text}"
            print(f"Error: {error_message}")
            return jsonify({
                'success': False,
                'error': error_message
            }), 500
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/join/<room_name>')
def join_room(room_name):
    room_url = f'https://{DAILY_SUBDOMAIN}.daily.co/{room_name}'
    return render_template('room.html', room_name=room_name, room_url=room_url)

@app.route('/check-api', methods=['GET'])
def check_api():
    """Test endpoint to check API connection"""
    try:
        headers = {
            'Authorization': f'Bearer {DAILY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            f'{DAILY_API_URL}/rooms',
            headers=headers
        )
        
        return jsonify({
            'status': response.status_code,
            'response': response.json() if response.status_code == 200 else response.text
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Make sure the static/signs directory exists
    os.makedirs('static/signs', exist_ok=True)
    
    # Start the Flask app
    print("Starting Flask application...")
    print(f"Using Daily.co subdomain: {DAILY_SUBDOMAIN}")
    app.run(debug=True)