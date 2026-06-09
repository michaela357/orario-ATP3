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


@genai_bp.route('/flashcards', methods=['GET'])
@login_required
def flashcards_dashboard():
    """Renders the main flashcard control deck panel."""
    # 1. Get a distinct list of group names this user has created
    groups = db.session.query(Flashcard.group).filter_by(user_id=current_user.id).distinct().all()
    group_names = [g[0] for g in groups if g[0]]

    # 2. Check if the user is clicking to filter down into a specific study deck group
    selected_group = request.args.get('study_group')
    
    cards_to_render = []
    if selected_group:
        cards_to_render = Flashcard.query.filter_by(user_id=current_user.id, group=selected_group).all()

    return render_template(
        'flashcards.html', 
        group_names=group_names, 
        flashcards=cards_to_render,
        selected_group=selected_group
    )


@genai_bp.route('/generate-flashcards', methods=['POST'])
@login_required
def generate_flashcards():
    temp_path = None
    try:
        if 'study_file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded."}), 400
            
        uploaded_file = request.files['study_file']
        num_cards = request.form.get('num_cards', 5, type=int)
        group_name = request.form.get('group-name', '').strip() or 'Untitled Group'
        
        if uploaded_file.filename == '':
            return jsonify({"success": False, "error": "No file selected."}), 400

        temp_dir = os.path.join(current_app.root_path, 'static', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(temp_path)

        file_text = extract_text_from_file(temp_path)
        if not file_text or len(file_text.strip()) < 10:
            return jsonify({"success": False, "error": "Could not extract readable text."}), 400

        prompt = (
            "You are an elite study assistant. Analyse the provided text, extract core concepts, and turn them into flashcards. "
            "You must return your response inside a single root JSON object containing a key called 'flashcards' which points to an array. "
            "Use a mix of styles: definitions, true/false, and question-answer formats. "
            "Each flashcard item within the array must have exactly two string fields: 'front' and 'back'.\n\n"
            f"Make sure to generate exactly {num_cards} flashcards.\n\n"
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

        raw_json_string = response.choices[0].message.content
        data = json.loads(raw_json_string)
        flashcards_list = data.get('flashcards', [])

        for card in flashcards_list:
            db.session.add(Flashcard(
                user_id=current_user.id, 
                front=card['front'], 
                back=card['back'], 
                group=group_name
            ))
        db.session.commit()

        # Redirect the user straight to studying their newly minted deck group!
        return redirect(url_for('genai.flashcards_dashboard', study_group=group_name))

    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": str(e)}), 500



"""
@genai_bp.route('/generate-flashcards', methods=['POST'])
@login_required
def generate_flashcards():
    temp_path = None
    try:
        #check if a file was sent in the request
        if 'study_file' not in request.files:
            return jsonify({"success": False, "error": "No file uploaded."}), 400
            
        uploaded_file = request.files['study_file']
        num_cards = request.form.get('num_cards', 5, type=int)  # Get the number of flashcards from the form, default to 5
        
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
            "Use a mix of styles: definitions, true/false, and question-answer formats."
            "Each flashcard item within the array must have exactly two string fields: 'front' and 'back'.\n"
            "Example layout:\n"
            "{\n"
            "  \"flashcards\": [\n"
            "    {\"front\": \"What is Photosynthesis?\", \"back\": \"The process used by plants to convert light into chemical energy.\"}\n"
            "  ]\n"
            "}\n\n"
            "Make sure to generate exactly " + str(num_cards) + " flashcards based on the most important information in the text.\n\n"
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
            db.session.add(Flashcard(user_id=current_user.id, front=front_text, back=back_text, group=request.form.get('group-name', 'Untitled Group')))
        db.session.commit()

        
        #pass the live list array directly into html template to display them
        return render_template('flashcards.html', flashcards=flashcards_list)

    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"success": False, "error": str(e)}), 500
    
"""