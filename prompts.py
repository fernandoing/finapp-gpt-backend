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
add_expense = 'A user says: {user_input}. If the user wants to add an expense, extract the relevant details such as expense amount, expense name, category id and the date. If user does not specify a date assign current date, here it is: {current_date}. If user inputs a date such as yesterday or last month, use the current date info as reference. The category IDs are in this json: {categories}. Determine the best category for the expense. Your response must be a json in this format: {json_example}. Return the json using double quotes for the keys and the values.'
determine_intent = """
    Given the following user input, categorize the intention as either '1. Adding an Expense', '2. View/See Expenses' or '3. General/financial purpose talk': 

    User Input: '{user_input}'

    Categories:
    1. Adding an Expense
    2. View/See Expenses
    3. General/financial purpose talk

    Determine the category based on keywords and the structure of the message. If the input contains financial amounts, specific cost-related terms (e.g., 'spent', 'buy', 'cost'), or direct mentions of budgeting items, categorize it as '1. Adding an Expense'. If the input intends to review, see or retrieve the expenses, categorize it as '2. View/See Expenses'. If the input discusses financial concepts, asks for advice, mentions planning without specific transaction details, or just want to talk about other topics categorize it as '3. General/financial purpose talk'.
    Respond with the category number ONLY.
"""
expense_added = """
    Given the user has just added an expense to their budget, craft a response informing them of the successful action. The response should have criteria of a professional finances advisor to let the user know if this exepnse was a correct decision or no. Make it concise. Include a suggestion for their next possible action to keep them engaged.
    Here are the details of the expense added: '{user_input}'. Use them to craft the response.
    Example of a good response:
    Fantastic! Your expense has been successfully added to your budget for. Would you like to review your current budget summary or add another expense?
"""
unclear_expense = """
It seems like the user wanted to add an expense to their budget but they're not providing the required information or maybe you though they wanted to add an expense and confused the intent with that. Give me a response to let them know you need more information such as the expense name and the amount they spent on it if they want to add an expense so they can try again.
"""
structure_expenses = 'Given the user wants to see their expenses, this is the user input: {user_input} return a formatted response with the list of expenses and its information. Do not respond with IDs. Here is the information with the expenses: {expenses}. On the date field, just show month and year, not day. This has to be a response for the final user.'