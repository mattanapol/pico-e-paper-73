from flask import Flask, send_from_directory, jsonify
import os
import google_calendar_fetcher

app = Flask(__name__)

# Replace 'your_file_directory' with the actual path to your files
UPLOAD_FOLDER = './'

@app.route('/files', methods=['GET'])
def get_files():
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify(files)

@app.route('/calendar', methods=['GET'])
def get_calendar_events():
    events, leave_events = google_calendar_fetcher.fetch_event()
    return jsonify(events)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
