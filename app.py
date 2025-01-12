from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from note import process_latex_input  # Import the refactored function
import os

app = Flask(__name__)
CORS(app)

def cleanup_files(directory, max_files=9):
    # Get a list of files in the directory sorted by modification time
    files = [os.path.join(directory, f) for f in os.listdir(directory)]
    files.sort(key=lambda x: os.path.getmtime(x))

    # Check if the number of files exceeds the maximum allowed
    while len(files) > max_files:
        os.remove(files.pop(0))

def home():
    print("Hello World")

@app.route('/run-code', methods=['POST'])
def run_code():
    data = request.json
    latex_code = data.get('latex_code', '')

    if not latex_code:
        return jsonify({"error": "No LaTeX code provided"}), 400

    # Process the LaTeX code into a DataFrame
    df = process_latex_input(latex_code)
    
    # Check if the DataFrame is empty
    if df.empty:
        return jsonify({"output": "No data to display"}), 204

    # Define the path for the Excel file
    # if not os.path.exists(output_folder):
    #     os.makedirs(output_folder)
    output_folder = 'static'  # Make sure this directory exists
    cleanup_files(output_folder)
    output_path = os.path.join(output_folder, 'output.xlsx')
    
    # Save the DataFrame to an Excel file
    df.to_excel(output_path, index=False)

    # Send the Excel file as a downloadable response
    try:
        return send_file(output_path, as_attachment=True, download_name='output.xlsx')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)