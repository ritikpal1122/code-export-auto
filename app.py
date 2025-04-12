from flask import Flask, request, jsonify, send_file, Response
import subprocess
import json
import os
from flask_cors import CORS
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load environment variables
app.config['AUTH_TOKEN'] = os.getenv('AUTH_TOKEN', 'default_token')

# Store status updates in memory (in production, use a proper database)
status_updates = {}
logs = []

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/styles.css')
def styles():
    return send_file('styles.css')

@app.route('/api/logs/update', methods=['POST'])
def update_logs():
    try:
        data = request.json
        message = data.get('message')
        timestamp = data.get('timestamp')
        
        if not message:
            return jsonify({'error': 'Missing message'}), 400
            
        logs.append({
            'message': message,
            'timestamp': timestamp
        })
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error updating logs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    return jsonify({'logs': logs})

@app.route('/api/status/update', methods=['POST'])
def update_status():
    try:
        data = request.json
        test_id = data.get('test_id')
        status = data.get('status')
        
        if not test_id or not status:
            return jsonify({'error': 'Missing test_id or status'}), 400
            
        status_updates[test_id] = {'status': status}
        app.logger.info(f"Status update for {test_id}: {status}")
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Error updating status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/run-automation', methods=['POST'])
def run_automation():
    try:
        data = request.json
        auth_token = data.get('auth_token')
        test_ids = data.get('test_ids', [])

        if not auth_token or not test_ids:
            return jsonify({
                'error': 'Missing required parameters',
                'details': 'Both auth_token and test_ids are required'
            }), 400

        # Log the request
        app.logger.info(f"Processing automation request for test IDs: {test_ids}")

        # Prepare input for the automation script
        input_data = {
            'auth_token': auth_token,
            'test_ids': test_ids
        }

        # Run the automation script
        process = subprocess.Popen(
            ['python3', 'test_automation.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Send input data to the script
        stdout, stderr = process.communicate(input=json.dumps(input_data))

        if process.returncode != 0:
            app.logger.error(f"Automation failed: {stderr}")
            return jsonify({
                'error': 'Automation failed',
                'details': stderr
            }), 500

        # Parse the script output
        try:
            result = json.loads(stdout)
            app.logger.info(f"Automation completed successfully: {result}")
            return jsonify(result)
        except json.JSONDecodeError:
            app.logger.error(f"Invalid response from automation script: {stdout}")
            return jsonify({
                'error': 'Invalid response from automation script',
                'details': stdout
            }), 500

    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'Unexpected error',
            'details': str(e)
        }), 500

@app.route('/api/status/<test_id>')
def get_status(test_id):
    def generate():
        while True:
            if test_id in status_updates:
                yield f"data: {json.dumps(status_updates[test_id])}\n\n"
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download-logs')
def download_logs():
    try:
        log_file = request.args.get('file')
        if not log_file or not os.path.exists(log_file):
            app.logger.error(f"Log file not found: {log_file}")
            return jsonify({
                'error': 'Log file not found'
            }), 404

        return send_file(
            log_file,
            as_attachment=True,
            download_name=log_file
        )

    except Exception as e:
        app.logger.error(f"Failed to download logs: {str(e)}")
        return jsonify({
            'error': 'Failed to download logs',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 