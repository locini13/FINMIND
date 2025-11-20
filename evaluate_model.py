import pandas as pd
import torch
from sentence_transformers import SentenceTransformer, util
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, classification_report, f1_score, accuracy_score
import numpy as np

class AI_Categorizer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the transformer model (SentenceTransformer) on GPU if available.
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"🖥 Using device: {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)

    def encode_texts(self, texts):
        """
        Encode a list of texts into embeddings on the selected device.
        """
        return self.model.encode(texts, convert_to_tensor=True, device=self.device)

    def predict_category(self, user_embedding, knowledge_embeddings, df, min_score=0.25):
        """
        Predict category based on cosine similarity with knowledge embeddings.
        """
        cos_scores = util.cos_sim(user_embedding, knowledge_embeddings)[0]
        top_idx = torch.argmax(cos_scores).item()
        best_score = cos_scores[top_idx].item()

        predicted_category = df.iloc[top_idx]['category']

        # Handle low-confidence predictions
        if best_score < min_score:
            return "Uncategorized"
        return predicted_category

# ---------------- Evaluation Pipeline ---------------- #
def evaluate_model(csv_path='data/transaction.csv', n_splits=5):
    # Load dataset
    df = pd.read_csv(csv_path)
    df.columns = [c.lower().strip() for c in df.columns]

    if 'text' not in df.columns or 'category' not in df.columns:
        raise ValueError("CSV must contain 'text' and 'category' columns.")

    X = df['text'].tolist()
    y = df['category'].tolist()

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    all_true = []
    all_pred = []

    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y), 1):
        print(f"\n===== Fold {fold} =====")
        train_texts = [X[i] for i in train_idx]
        test_texts = [X[i] for i in test_idx]
        train_labels = [y[i] for i in train_idx]
        test_labels = [y[i] for i in test_idx]

        # Encode train embeddings
        categorizer = AI_Categorizer()
        knowledge_embeddings = categorizer.encode_texts(train_texts)

        # Predict on test set
        fold_preds = []
        for text in test_texts:
            user_embedding = categorizer.encode_texts([text])[0]
            pred = categorizer.predict_category(user_embedding, knowledge_embeddings, pd.DataFrame({'text': train_texts, 'category': train_labels}))
            fold_preds.append(pred)

        # Collect results
        all_true.extend(test_labels)
        all_pred.extend(fold_preds)

        # Fold metrics
        acc = accuracy_score(test_labels, fold_preds)
        f1 = f1_score(test_labels, fold_preds, average='macro')
        print(f"Fold Accuracy: {acc:.4f} | Fold F1 (macro): {f1:.4f}")

    # Overall metrics
    print("\n===== Overall Classification Report =====")
    print(classification_report(all_true, all_pred, digits=4))
    
    print("🧮 Confusion Matrix:")
    cm = confusion_matrix(all_true, all_pred, labels=list(sorted(set(y))))
    print(cm)

    acc = accuracy_score(all_true, all_pred)
    f1 = f1_score(all_true, all_pred, average='macro')
    print(f"\n✅ Overall Accuracy: {acc:.4f}")
    print(f"🏆 Overall F1 Score (macro): {f1:.4f}")


if __name__ == "__main__":
    evaluate_model(csv_path='data/transaction.csv', n_splits=5)
