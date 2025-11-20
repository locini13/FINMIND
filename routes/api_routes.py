from flask import Blueprint, request, jsonify
from nlp.parser import RuleParser
from nlp.categorizer import AI_Categorizer

api_bp = Blueprint('api', __name__)

# Initialize NLP modules
parser = RuleParser()
categorizer = AI_Categorizer()

@api_bp.route('/analyze', methods=['POST'])
def analyze_transaction():
    data = request.json
    message = data.get('message', '')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    # 1. Rule-Based Extraction
    amount = parser.extract_amount(message)
    trans_type = parser.determine_type(message)

    # 2. AI Semantic Categorization
    category = categorizer.predict_category(message)
    
    # If AI detects it matches "Salary" category but rule said Expense, logic fix:
    if category == "Salary & Income":
        trans_type = "Income"

    response = {
        "original_text": message,
        "amount": amount,
        "type": trans_type,
        "category": category,
        "status": "success"
    }
    
    return jsonify(response)