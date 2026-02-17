# FINMIND – Your Smart Finance Buddy

FINMIND is an AI-powered personal finance assistant that helps you effortlessly track expenses, set budgets, receive smart alerts, and uncover spending insights—all through natural language chat.

---

## Features

- **Set Budgets Easily**  
  Allocate budgets by category (e.g., Food ₹500, Shopping ₹1000) stored securely in Firebase.

- **Chat to Log Expenses**  
  Simply type natural sentences like “Burger King 250” to log transactions with automatic merchant and category detection.

- **Smart Alerts & Reminders**  
  Get notified when you approach budget limits or when unusual spending happens.

- **Spend Anomaly Detection**  
  Detects and alerts you about unusual transactions to avoid surprises.

- **Daily Spending Heatmap**  
  Visualize your daily spend patterns with intuitive color-coded heatmaps.

- **Summary Reports**  
  Receive quick daily or weekly spend summaries showing totals, category breakdowns, and remaining budgets.

- **Autocorrect & Vendor Detection**  
  Advanced ML and fuzzy matching ensure merchant names are accurately recognized, reducing errors.

- **Reset Data Command**  
  Clear budgets, transactions, and alerts with a simple “Reset everything” command.

---

## Project Structure

'''
FINMIND/
├── data/
│ ├── corrected_expenses.csv
│ └── transaction.csv
├── models/
│ ├── category_classifier.pkl
│ └── type_classifier.pkl
├── nlp/
│ ├── auto_correction.py
│ ├── categorizer.py
│ ├── category_mapping.py
│ ├── parser.py
│ ├── spend_anomaly.py
│ ├── spending_analytics.py
│ └── train_models.py
├── routes/
│ ├── api_routes.py
│ └── graphql_routes.py
├── static/
├── templates/
│ └── index.html
├── venv/
├── .env
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
└── serviceAccountKey.json

'''

Usage

Set budgets via the landing page or skip to chat directly.
Log expenses by typing natural sentences (e.g., “Starbucks 300”).
Ask for summaries, heatmaps, or reset your data anytime.
Receive intelligent alerts to stay on track
