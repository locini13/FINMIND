import pandas as pd
import torch
import re
import os
from sentence_transformers import SentenceTransformer, util

class AI_Categorizer:
    def __init__(self, csv_path='data\\transaction.csv'):
        print("⚡ Initializing AI Brain...")
        
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🚀 Running on: {self.device.upper()}")
        
        self.model = SentenceTransformer('all-MiniLM-L6-v2', device=self.device)
        
        # Load CSV
        self.df = pd.DataFrame()
        self.knowledge_embeddings = None
        self.load_data(csv_path)

    def load_data(self, csv_path):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            full_path = os.path.join(project_root, csv_path)

            if os.path.exists(full_path):
                self.df = pd.read_csv(full_path)
                self.df.columns = [c.lower().strip() for c in self.df.columns]
                self.knowledge_embeddings = self.model.encode(
                    self.df['text'].tolist(), 
                    convert_to_tensor=True,
                    device=self.device
                )
                print(f"✅ Loaded {len(self.df)} patterns.")
            else:
                print(f"⚠️ CSV not found at {full_path}.")
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")

    def parse_amount(self, text):
        # Fix 3: Robust Regex for amounts (e.g., 8000, 8,000, 8000.50)
        # Look for a number pattern that might have commas, optionally followed by decimals
        # We strip currency symbols in the regex look-behind or just ignore them
        match = re.search(r'[₹$€]?\s?([\d,]+(?:\.\d{1,2})?)', text)
        if match:
            clean_str = match.group(1).replace(',', '')
            try:
                return float(clean_str)
            except ValueError:
                return 0.0
        return 0.0

    def detect_intent(self, text):
        text = text.lower()
        
        # 1. RESET
        if text.strip() == "reset" or "reset data" in text:
            return "reset", None

        # 2. BUDGET / SAVINGS GOALS (Fix 2)
        # If user talks about saving or setting a budget, it's NOT a transaction.
        budget_keywords = ["save", "saving", "budget", "goal", "target", "limit"]
        if any(w in text for w in budget_keywords) and not "spent" in text:
            # "I spent 500 from savings" -> Transaction
            # "I want to save 500" -> Budget Goal
            return "budget_goal", "general"

        # 3. QUERY (Fix 4)
        query_keywords = [
            "how much", "balance", "total", "spent", "left", "report", 
            "biggest", "highest", "show me", "ledger", "history", "breakdown", 
            "spending", "income", "expense"
        ]
        
        # If it looks like a question OR contains query keywords but NO amount (usually), it's a query
        has_amount = bool(re.search(r'\d', text))
        
        if any(k in text for k in query_keywords):
            if "balance" in text or "left" in text or "money" in text:
                return "query", "balance"
            if "biggest" in text or "highest" in text:
                return "query", "highest_expense"
            if "report" in text or "breakdown" in text or "ledger" in text:
                return "query", "report"
            # Fallback for vague queries
            return "query", "general"

        # 4. TRANSACTION (Default)
        return "transaction", None

    def determine_type_and_category(self, text, amount):
        lower_text = text.lower()
        
        # --- TYPE DETECTION (Fix 1) ---
        
        # Explicit OVERRIDE rules take precedence over AI
        income_keywords = ['received', 'credited', 'bonus', 'salary', 'earned', 'sold', 'sale', 'sell']
        expense_keywords = ['paid', 'bought', 'spent', 'purchase', 'bill', 'deducted', 'cost', 'rent', 'emi', 'dinner', 'lunch']

        trans_type = "Expense" # Default safe assumption
        
        # 1. Check Income Keywords
        if any(w in lower_text for w in income_keywords):
            trans_type = "Income"
            
        # 2. Check Expense Keywords (Can override income if context implies spending "income tax")
        # But generally, if "bought" or "paid" is there, it is 100% Expense.
        if any(w in lower_text for w in expense_keywords):
            trans_type = "Expense"

        # --- CATEGORY DETECTION ---
        category = "General"
        
        if not self.df.empty and self.knowledge_embeddings is not None:
            user_emb = self.model.encode(text, convert_to_tensor=True, device=self.device)
            scores = util.cos_sim(user_emb, self.knowledge_embeddings)[0]
            best_idx = torch.argmax(scores).item()
            best_score = scores[best_idx].item()

            if best_score > 0.25: 
                category = self.df.iloc[best_idx]['category']

        # --- FINAL LOGIC CHECKS ---
        
        # Logic Fix: If the category matches "Salary" or "Income", ensure Type is Income
        if "salary" in category.lower() or "income" in category.lower():
             # Unless user said "Paid Income Tax" -> Expense
             if "tax" not in lower_text and "paid" not in lower_text:
                 trans_type = "Income"

        # Logic Fix: If user said "Bought/Paid", ensure Type is Expense, even if Category was weird
        if any(w in lower_text for w in expense_keywords):
            trans_type = "Expense"
            # If AI wrongly picked 'Other Income' for 'Bought books', force it to 'Shopping' or 'General'
            if category == "Other Income" or category == "Salary & Income":
                category = "Shopping" # Fallback correction

        # Logic Fix: "Sold" items should be Income / Other Income
        if "sold" in lower_text or "sell" in lower_text:
            trans_type = "Income"
            category = "Other Income"

        return trans_type, category

    def predict(self, text):
        intent, query_type = self.detect_intent(text)
        
        response = {
            "intent": intent,
            "original_text": text,
            "query_type": query_type,
            "amount": 0,
            "category": "Uncategorized",
            "type": "Expense",
            "alert": None
        }

        if intent == "transaction":
            response['amount'] = self.parse_amount(text)
            if response['amount'] > 0:
                t_type, t_cat = self.determine_type_and_category(text, response['amount'])
                response['type'] = t_type
                response['category'] = t_cat
        
        elif intent == "budget_goal":
            # Parse amount for budget setting
            response['amount'] = self.parse_amount(text)
            # We categorize what they are budgeting for
            _, t_cat = self.determine_type_and_category(text, 0)
            response['category'] = t_cat

        return response