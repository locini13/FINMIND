import pandas as pd
import torch
import os
from sentence_transformers import SentenceTransformer, util


class AI_Categorizer:
    def __init__(self, csv_path='data\\transaction.csv', model_name='all-MiniLM-L6-v2'):
        """
        Initializes the AI model and loads transaction data from CSV.
        
        Args:
            csv_path: Relative path to the CSV file from the project root.
            model_name: Name of the SentenceTransformer model to load.
        """
        print("⚡ Initializing AI Categorizer...")

        # Device setup: use GPU if available
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥 Using device: {self.device}")

        # Load the Pre-trained Transformer Model on the selected device
        self.model = SentenceTransformer(model_name, device=self.device)

        self.df = pd.DataFrame()
        self.knowledge_embeddings = None

        # Resolve CSV file path robustly
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        full_path = os.path.join(project_root, csv_path)

        try:
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"CSV file not found at: {full_path}")

            print(f"📂 Loading data from: {full_path}")
            self.df = pd.read_csv(full_path)
            
            # Normalize column names
            self.df.columns = [c.lower().strip() for c in self.df.columns]

            # Validate required columns
            if 'text' not in self.df.columns or 'category' not in self.df.columns:
                raise ValueError("CSV must contain 'text' and 'category' columns.")

            # Pre-compute embeddings on the correct device
            print("🧠 Encoding transaction patterns...")
            self.knowledge_embeddings = self.model.encode(
                self.df['text'].tolist(), 
                convert_to_tensor=True,
                device=self.device
            )
            print(f"✅ AI is ready! Learned {len(self.df)} transaction patterns.")

        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            print("⚠️ Defaulting to 'General' category for all predictions.")

    def predict_category(self, user_message, min_score=0.25):
        """
        Predict the category of a user message using semantic similarity.
        
        Args:
            user_message (str): The input message to classify.
            min_score (float): Minimum similarity threshold to assign a category.
        
        Returns:
            str: Predicted category or 'Uncategorized'.
        """
        # Safety: CSV didn't load
        if self.knowledge_embeddings is None or self.df.empty:
            return "General"

        # Encode the user's message on the correct device
        user_embedding = self.model.encode(user_message, convert_to_tensor=True, device=self.device)

        # Compute cosine similarity
        cos_scores = util.cos_sim(user_embedding, self.knowledge_embeddings)[0]

        # Get the best match
        top_match_idx = torch.argmax(cos_scores).item()
        best_score = cos_scores[top_match_idx].item()

        predicted_category = self.df.iloc[top_match_idx]['category']
        matched_text = self.df.iloc[top_match_idx]['text']

        # Debug info
        print(f"🔎 Input: '{user_message}'")
        print(f"   ↳ Matched with: '{matched_text}' (Score: {best_score:.4f})")
        print(f"   ↳ Category: {predicted_category}")

        # Threshold check
        if best_score < min_score:
            return "Uncategorized"

        return predicted_category
