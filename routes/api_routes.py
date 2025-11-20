from flask import Blueprint, request, jsonify
from nlp.categorizer import AI_Categorizer

api_bp = Blueprint('api', __name__)

# Initialize single instance
brain = AI_Categorizer()

@api_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "Empty message"}), 400

        # Process with AI
        result = brain.predict(message)
        
        # Add simple backend-side alert logic (optional, mostly handled in JS)
        if result['intent'] == 'transaction' and result['amount'] > 5000 and result['type'] == 'Expense':
            result['alert'] = "⚠️ High value transaction detected."

        result['status'] = 'success'
        return jsonify(result)

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500