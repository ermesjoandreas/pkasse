import os
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from modules import bildeanalyse

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FlaskServer")

UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """
    Endpoint for analyzing an uploaded image.
    Expected multipart/form-data with key 'image'.
    """
    if 'image' not in request.files:
        return jsonify({"error": "No image part"}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Image received and saved to {filepath}. Analyzing...")
        
        try:
            # Reuse existing MVP module logic
            results = bildeanalyse.analyser_bilde(filepath)
            
            # Serialize results
            json_results = []
            for pk_id, kap_enum in results:
                json_results.append({
                    "id": pk_id,
                    "kapasitet_klasse": kap_enum.name # "LITEN", "STANDARD", "STOR"
                })
            
            response = {
                "success": True,
                "filename": filename,
                "postkasser": json_results,
                "count": len(json_results)
            }
            logger.info(f"Analysis success. Found {len(json_results)} mailboxes.")
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return jsonify({"error": str(e)}), 500
            
    return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg"}), 400

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running", "message": "Postkasse Vision API Ready"}), 200

if __name__ == "__main__":
    # Host on 0.0.0.0 to enable access from devices on the same network
    print("\nStarting Flask Server...")
    print("Ensure your iPhone is on the same Wi-Fi.")
    print("Endpoint: http://<YOUR_IP>:5001/analyze\n")
    app.run(host='0.0.0.0', port=5001, debug=True)
