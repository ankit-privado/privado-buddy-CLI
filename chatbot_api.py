from flask import Flask, request, jsonify
from main import app

@app.route('/execute-script', methods=['POST'])
def execute_script():
    json_data = request.json
    query = json_data.get('query')
    return jsonify({'answer': answer})
