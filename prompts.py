json_example = """
{
    "expense_amount": 50,
    "expense_name": "Mazapanes",
    "month_year": "2024-03-04",
    "exp_category_id": 1
}

"""
base_prompt = """
You are a helpful AI Financial Advisor/Assistant. Remember this app is intended so a user can create a budget and add their expenses via this chat interaction. Be very professional.
"""
add_expense = 'A user says: {user_input}. If the user wants to add an expense, extract the relevant details such as expense amount, expense name, category id and the date. If user does not specify a date assign current date. The category IDs are: 1 for Groceries, 2 for Rent, 3 for Utilities, 4 for Transportation. Your response must be a json in this format: {json_example}'
determine_intent = """
    Given the following user input, categorize the intention as either 'Adding an Expense' or 'General/financial purpose talk': 

    User Input: '{user_input}'

    Categories:
    1. Adding an Expense
    2. General/financial purpose talk

    Determine the category based on keywords and the structure of the message. If the input contains financial amounts, specific cost-related terms (e.g., 'spent', 'buy', 'cost'), or direct mentions of budgeting items, categorize it as 'Adding an Expense'. If the input discusses financial concepts, asks for advice, mentions planning without specific transaction details, or just want to talk about other topics categorize it as 'General/financial purpose talk'.
    Respond with the category number ONLY.
"""
expense_added = """
    Given the user has just added an expense to their budget, craft a positive and encouraging response informing them of the successful action. The response should make the user feel confident and in control of their financial journey. Include a suggestion for their next possible action to keep them engaged.
    Here are the details of the expense added: '{user_input}'
    Example of a good response:
    Fantastic! Your [expense name] of [expense amount] on [expense category] has been successfully added to your budget for [month]. Your diligence in tracking your expenses is key to achieving your financial goals. Would you like to review your current budget summary or add another expense?
"""
unclear_expense = """
It seems like the user wanted to add an expense to their budget but they're not providing the required information or maybe you though they wanted to add an expense and confused the intent with that. Give me a response to let them know you need more information such as the expense name and the amount they spent on it if they want to add an expense so they can try again.
"""