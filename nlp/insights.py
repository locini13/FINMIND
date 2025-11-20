def generate_insight(transactions, budgets):
    # Simple logic to analyze spending vs budget
    total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    
    warnings = []
    
    # Check overall budget (if a general budget exists)
    if 'General' in budgets:
        limit = budgets['General']
        if total_expense > limit:
            warnings.append(f"⚠️ You have exceeded your total budget of ${limit}!")
        elif total_expense > limit * 0.8:
            warnings.append(f"⚠️ Careful! You are at 80% of your budget.")

    # Spending patterns
    if total_expense == 0:
        return "No spending data yet. Add an expense!"
    
    msg = f"Total spending: ${total_expense:.2f}. "
    if warnings:
        msg += " ".join(warnings)
    else:
        msg += "You are within safe limits. Keep saving!"
        
    return msg