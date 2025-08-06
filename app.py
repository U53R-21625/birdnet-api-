from flask import Flask, request, jsonify
import subprocess
import os
import uuid

app = Flask(__name__)

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    uid = str(uuid.uuid4())
    audio_path = f'{uid}.wav'
    file.save(audio_path)

    output_path = f'{uid}.json'

    cmd = [
        'python3', 'BirdNET-Analyzer/analyze.py',
        '--i', audio_path,
        '--o', '.', '--lat', '28.6139', '--lon', '77.2090',  # Example: Delhi
        '--sensitivity', '0.5', '--threads', '1', '--locale', 'en'
    ]

    subprocess.run(cmd, check=True)

    try:
        with open(f'{uid}.BirdNET.results.json') as f:
            lines = f.readlines()
        os.remove(audio_path)
        os.remove(f'{uid}.BirdNET.results.json')
        if not lines:
            return jsonify({'result': 'No birds detected'})
        result_line = lines[1].split('\t')  # skip header
        return jsonify({
            'common_name': result_line[3],
            'scientific_name': result_line[4],
            'confidence': float(result_line[2])
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
