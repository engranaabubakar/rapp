#!/usr/bin/env python3
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'component': 'rapp-core'})

@app.route('/metrics', methods=['GET'])
def metrics():
    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'core_status': 'operational',
        'n2_link_utilization': 45.0,
        'n3_xhaul_utilization': 87.0
    })

if __name__ == '__main__':
    print('[rApp-Core] Starting core-side controller on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=False)
