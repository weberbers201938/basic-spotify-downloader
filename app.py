# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import subprocess
import uuid

app = Flask(__name__)

# Set up a directory for downloaded music
DOWNLOAD_DIR = 'downloads'

@app.route('/')
def home():
    return render_template('index.html')  # Serve the HTML page

@app.route('/download', methods=['POST'])
def download_song():
    data = request.json
    spotify_url = data.get('url')

    if not spotify_url:
        return jsonify({'error': 'No URL provided'}), 400

    # Generate a unique download directory for each request
    unique_id = str(uuid.uuid4())
    download_path = os.path.join(DOWNLOAD_DIR, unique_id)
    os.makedirs(download_path, exist_ok=True)

    # Run spotDL to download the song or playlist
    try:
        download_command = f"spotdl {spotify_url} -o {download_path}"
        subprocess.run(download_command, shell=True, check=True)

        # Get the downloaded file name
        downloaded_files = os.listdir(download_path)
        if not downloaded_files:
            return jsonify({'error': 'No song downloaded'}), 500

        song_path = os.path.join(download_path, downloaded_files[0])

        # Return the song download link
        return jsonify({'file_path': f'/download_file/{unique_id}/{downloaded_files[0]}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download_file/<unique_id>/<file_name>', methods=['GET'])
def download_file(unique_id, file_name):
    file_path = os.path.join(DOWNLOAD_DIR, unique_id, file_name)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    app.run(host="0.0.0.0", port=5000, debug=True)
