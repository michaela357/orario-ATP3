# Routes for AI feature
import os

from dotenv import load_dotenv
from flask import (Blueprint, current_app, json, jsonify, redirect,
                   render_template, request, url_for)
from flask_login import current_user, login_required
from groq import Groq

from extensions import db
from models import Flashcard
from utils.utils import extract_text_for_ai

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

        if uploaded_file.filename == '':
            return jsonify({"success":False,"error":"No file selected."}),400

        num_cards = request.form.get("num_cards",5,type=int)

        # Check duplicate group names
        group_name = request.form.get("group-name","").strip() or "Untitled Group"

        existing_groups = (
            db.session.query(Flashcard.group)
            .filter_by(user_id=current_user.id)
            .distinct()
            .all()
        )

        existing_groups = [g[0] for g in existing_groups if g[0]]

        if group_name in existing_groups:
            return jsonify({
                "success":False,
                "error":"A group with this name already exists."
            }),400

        # Save uploaded file
        temp_dir = os.path.join(current_app.root_path,"static","temp")
        os.makedirs(temp_dir,exist_ok=True)
        filename = f"{current_user.id}_{uploaded_file.filename}"

        temp_path = os.path.join(temp_dir,filename)

        uploaded_file.save(temp_path)

        file_text = extract_text_for_ai(temp_path, allowed_directory=temp_dir)

        if not file_text or len(file_text.strip()) < 10:
            return jsonify({"success": False, "error": "Could not extract readable text or file was completely empty."}), 400
        
        custom_user_message = request.form.get("custom-message","").strip()

        base_prompt = (
            "You are an elite study assistant. Analyse the provided text, extract core concepts, and turn them into flashcards. "
            "You must return your response inside a single root JSON object containing a key called 'flashcards' which points to an array. "
            "Use a mix of styles: definitions, true/false, and question-answer formats unless specified. "
            "Each flashcard item within the array must have exactly two string fields: 'front' and 'back'.\n\n"
            f"Make sure to generate exactly {num_cards} flashcards. No more, no less. If you can't, duplicate some flashcards until you have that EXACT amount.\n\n"
        )

        # Only append user styling instructions cleanly if they entered them
        if custom_user_message and custom_user_message.strip():
            prompt += f"User Modification Criteria: {custom_user_message.strip()}\n\n"

        base_prompt += f"--- begin source content ---\n{file_text}\n ---end---"

        # Primary AI call
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role":"user","content":base_prompt}],
            temperature=0.2,
            response_format={"type":"json_object"}
        )

        raw_json_string = response.choices[0].message.content
        data = json.loads(raw_json_string)
        flashcards_list = data.get('flashcards', [])

        # Remove invalid cards
        flashcards_list = [
            c for c in flashcards_list
            if isinstance(c,dict)
            and c.get("front")
            and c.get("back")
        ]

        # if there are too many flashcards
        flashcards_list = flashcards_list[:num_cards]

        # if there are not enough flashcards
        if len(flashcards_list) < num_cards:

            missing = num_cards - len(flashcards_list)

            second_prompt = (
                f"Generate EXACTLY {missing} MORE flashcards "
                "using the same notes.\n"
                "Return ONLY JSON in the form:\n"
                "{\"flashcards\":[{\"front\":\"...\",\"back\":\"...\"}]}\n\n"
                f"{file_text}"
            )

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role":"user","content":second_prompt}],
                temperature=0.2,
                response_format={"type":"json_object"}
            )

            extra = json.loads(
                response.choices[0].message.content
            ).get("flashcards",[])

            extra = [
                c for c in extra
                if isinstance(c,dict)
                and c.get("front")
                and c.get("back")
            ]

            flashcards_list.extend(extra)

        # Final guarantee
        flashcards_list = flashcards_list[:num_cards]

        # Save cards
        for card in flashcards_list:
            db.session.add(Flashcard(
                user_id=current_user.id, 
                front=card['front'], 
                back=card['back'], 
                group=group_name
            ))
        db.session.commit()

        validation_message = f'Successfully created the deck "{group_name}"'

        # Return a JSON object containing the target URL path instead of a redirect response
        return jsonify({
            "success": True, 
            "redirect": url_for('genai.flashcards_dashboard', study_group=group_name),
            "message": validation_message
        }), 200

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "success":False,
            "error":str(e)
        }),500

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
    
@genai_bp.route('/api/edit_flashcard/<int:flashcard_id>', methods=['POST'])
def edit_flashcard(flashcard_id):
    flashcard = Flashcard.query.get(flashcard_id)
    data = request.form

    if not flashcard or flashcard.user_id != current_user.id:
        return jsonify({
            "success": False,
            "error": "Flashcard not found or access unauthorised"
        }), 404

    try:
        if 'front' in data:
            flashcard.front = data.get('front')

        if 'back' in data:
            flashcard.back = data.get('back')

        db.session.commit()
        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Database mutation crash: {str(e)}"
        }), 500

@genai_bp.route('/delete-group/<group_name>', methods=['POST'])
@login_required
def remove_group(group_name):    
    try:
        # FIX: Changed the left side filter parameter from group_name to group
        flashcards = db.session.query(Flashcard).filter_by(
            group=group_name,
            user_id=current_user.id
        ).all()
        
        # If no matching cards are found under this group name, return a 404
        if not flashcards:
            return jsonify({
                "success": False, 
                "error": "Flashcard group not found or unauthorised."
            }), 404

        # Loop through and delete each card individually 
        for card in flashcards:
            db.session.delete(card)
            
        # Commit the changes to your database file
        db.session.commit()
        
        return jsonify({"success": True}), 200

    except Exception as e:
        db.session.rollback()
        
        # This will still log to your terminal console if anything else goes wrong
        print("!!! DELETION CRASH ERROR !!!:", str(e)) 
        
        return jsonify({
            "success": False, 
            "error": f"Database Error: {str(e)}"
        }), 500