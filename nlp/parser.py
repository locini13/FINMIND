import re

class RuleParser:
    def extract_amount(self, text):
        # Regex for currency (e.g., 2500, 2,500, 150.50)
        # Looks for digits optionally followed by decimals
        match = re.search(r'[\₹\$€]?\s?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+)', text)
        if match:
            # Remove commas and currency symbols to get pure float
            clean_amount = match.group(1).replace(',', '')
            return float(clean_amount)
        return 0.0

    def determine_type(self, text):
        text = text.lower()
        income_keywords = ['received', 'credited', 'bonus', 'salary', 'earned', 'income']
        expense_keywords = ['paid', 'spent', 'bought', 'bill', 'purchase', 'debit']
        
        # Simple keyword matching
        if any(word in text for word in income_keywords):
            return 'Income'
        elif any(word in text for word in expense_keywords):
            return 'Expense'
        return 'Expense' # Default to expense if unsure