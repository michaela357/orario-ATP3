def get_calendar_navigation(year, month):
    """
    Calculates the previous and next month/year pagination values.

    Args:
        - year (int): The current year.
        - month (int): The current month.
    Returns:
        - tuple: (prev_year, prev_month, next_year, next_month)
    """
    if month > 1:
        prev_month, prev_year = month - 1, year
    else:
        prev_month, prev_year = 12, year - 1
    
    if month < 12:
        next_month, next_year = month + 1, year
    else:
        next_month, next_year = 1, year + 1
        
    return prev_year, prev_month, next_year, next_month