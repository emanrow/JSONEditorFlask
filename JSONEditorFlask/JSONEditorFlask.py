from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import shutil
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'src/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/files', methods=['GET'])
def list_files():
    files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return jsonify(files)

@app.route('/files', methods=['POST'])
def new_file():
    base_name = "new_file"
    counter = 1
    file_name = f"{base_name}{counter}.json"
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], file_name)):
        counter += 1
        file_name = f"{base_name}{counter}.json"

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    with open(file_path, 'w') as file:
        json.dump({}, file)  # Create an empty JSON file
    return jsonify({'message': 'File created', 'file_name': file_name})

@app.route('/files/<filename>', methods=['GET'])
def open_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            file_content = json.load(file)
        return jsonify(file_content)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/files/<filename>/rename', methods=['PUT'])
def rename_file(filename):
    new_name = request.json.get('new_name')
    if not new_name:
        return jsonify({'error': 'New name is required'}), 400

    old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_name)

    if os.path.exists(old_file_path):
        os.rename(old_file_path, new_file_path)
        return jsonify({'message': 'File renamed successfully'})
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/files/<filename>/duplicate', methods=['POST'])
def duplicate_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        counter = 1
        file_name, file_extension = os.path.splitext(filename)
        new_file_name = f"{file_name}_{counter}{file_extension}"
        new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_file_name)

        while os.path.exists(new_file_path):
            counter += 1
            new_file_name = f"{file_name}_{counter}{file_extension}"
            new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_file_name)

        shutil.copy(file_path, new_file_path)
        return jsonify({'message': 'File duplicated successfully', 'new_file_name': new_file_name})
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/files/<filename>/delete', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'message': 'File deleted successfully'})
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
    file.save(file_path)

    # Load and return the file content as JSON
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return jsonify(json_data)
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON file'}), 400

@app.route('/files/<filename>/update', methods=['PUT'])
def update_file(filename):
    if not request.is_json:
        print("Received data is not JSON")
        return jsonify({'error': 'Invalid or no JSON data received'}), 400

    json_data = request.json
    print("Received JSON data:", json_data)  # Log the received JSON data
    print("File name:", filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print("File path:", file_path)

    try:
        with open(file_path, 'w') as file:
            json.dump(json_data, file)
        return jsonify({'message': 'File updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
