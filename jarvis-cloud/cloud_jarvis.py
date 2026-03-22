import os
import time
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='web')
CORS(app)

# Store connected PCs and commands
connected_pcs = {}
command_queue = {}

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/api/register', methods=['POST'])
def register_pc():
    data = request.json
    pc_id = data.get('pc_id')
    pc_name = data.get('pc_name')
    
    connected_pcs[pc_id] = {
        'name': pc_name,
        'connected': True,
        'last_seen': time.time()
    }
    
    print(f"✅ PC Registered: {pc_name} ({pc_id})")
    return jsonify({'status': 'registered', 'pc_id': pc_id})

@app.route('/api/pcs', methods=['GET'])
def get_pcs():
    return jsonify({'pcs': connected_pcs})

@app.route('/api/send_command', methods=['POST'])
def send_command():
    data = request.json
    pc_id = data.get('pc_id')
    command = data.get('command')
    
    if pc_id not in command_queue:
        command_queue[pc_id] = []
    
    command_id = str(time.time())
    command_queue[pc_id].append({
        'id': command_id,
        'command': command,
        'timestamp': time.time()
    })
    
    print(f"📨 Command sent to {pc_id}: {command}")
    return jsonify({'status': 'sent', 'command_id': command_id})

@app.route('/api/get_commands/<pc_id>', methods=['GET'])
def get_commands(pc_id):
    if pc_id not in command_queue:
        return jsonify({'commands': []})
    
    commands = command_queue[pc_id]
    command_queue[pc_id] = []
    
    # Update last seen
    if pc_id in connected_pcs:
        connected_pcs[pc_id]['last_seen'] = time.time()
    
    return jsonify({'commands': commands})

@app.route('/api/report_result', methods=['POST'])
def report_result():
    data = request.json
    print(f"📊 Result from {data.get('pc_id')}: {data.get('result')}")
    return jsonify({'status': 'ok'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'pcs': len(connected_pcs)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
