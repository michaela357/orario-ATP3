# Routes for AI feature

from flask import Blueprint, render_template, jsonify, current_app
import os

from google import genai
from google.genai import types

genai_bp = Blueprint('genai', __name__)

client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY', 'YOUR_HARDCODED_KEY_IF_NEEDED'))

@genai_bp.route('/make-flashcard')
def make_flashcard():
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents='Why is the sky blue?',
            config=types.GenerateContentConfig(
                temperature=0,
                top_p=0.95,
                top_k=20,
            ),
        )
        return render_template('flashcard.html', flashcard=response.text)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@genai_bp.route('/test-file-summary')
def test_file_summary():
    try:
        # Use current_app.root_path to find the absolute path to your static folder
        local_file_path = os.path.join(current_app.root_path, 'static', 'genai_test.txt')
        
        if not os.path.exists(local_file_path):
            return jsonify({"success": False, "error": f"File not found at {local_file_path}"}), 404

        # 1. Upload the file to the Gemini API
        uploaded_file = client.files.upload(file=local_file_path)

        # 2. Pass the uploaded file object directly into contents
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=['Could you summarize this file?', uploaded_file]
        )

        # 3. Clean up the file from Google's servers after you're done (Good practice!)
        client.files.delete(name=uploaded_file.name)

        return render_template('flashcard.html', flashcard=response.text)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500