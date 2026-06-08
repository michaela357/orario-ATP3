# Routes for AI feature
import os

from dotenv import load_dotenv
from flask import Blueprint, current_app, json, jsonify, render_template, request
from groq import Groq
from flask_login import current_user, login_required

from extensions import db
from models import Flashcard
from utils.utils import extract_text_from_file


load_dotenv()  # Load environment variables from .env file
genai_bp = Blueprint('genai', __name__)

# Safely loading the key from environment variables
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

@genai_bp.route('/generate-flashcards', methods=['POST'])
@login_required
def generate_flashcards():
    temp_path = None
    try:
        #check if a file was sent in the request
        if 'study_file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded."}), 400
            
        uploaded_file = request.files['study_file']
        
        if uploaded_file.filename == '':
            return jsonify({"success": False, "error": "No file selected."}), 400

        #securely save the file to a temporary location to process it
        temp_dir = os.path.join(current_app.root_path, 'static', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(temp_path)

        # extract text locally using helper function
        file_text = extract_text_from_file(temp_path)
        
        if not file_text or len(file_text.strip()) < 10:
            return jsonify({"success": False, "error": "Could not extract readable text from this file."}), 400

        # Explicitly instruct the model to output JSON
        prompt = (
            "You are an elite study assistant. Analyse the provided text, extract core concepts, and turn them into flashcards. "
            "You must return your response inside a single root JSON object containing a key called 'flashcards' which points to an array. "
            "Each flashcard item within the array must have exactly two string fields: 'front' and 'back'.\n"
            "Example layout:\n"
            "{\n"
            "  \"flashcards\": [\n"
            "    {\"front\": \"What is Photosynthesis?\", \"back\": \"The process used by plants to convert light into chemical energy.\"}\n"
            "  ]\n"
            "}\n\n"
            f"Source text content:\n\n{file_text}"
        )

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"}
        )

        if os.path.exists(temp_path):
            os.remove(temp_path)

        #convert the raw text response into a dictionary
        raw_json_string = response.choices[0].message.content
        data = json.loads(raw_json_string) # Turns the string into a real dictionary
        flashcards_list = data.get('flashcards', [])

        print(flashcards_list)  # For debugging purposes, to see the generated flashcards in the console

        for card in flashcards_list:
            front_text = card['front']
            back_text = card['back']
            db.session.add(Flashcard(user_id=current_user.id, front=front_text, back=back_text))
        db.session.commit()

        
        #pass the live list array directly into html template to display them
        return render_template('flashcards.html', flashcards=flashcards_list)

    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": str(e)}), 500