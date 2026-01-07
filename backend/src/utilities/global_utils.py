from flask import request, session
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION

def check_if_data_is_not_None(args: list) -> None:
    """checks if any of the args is None, raises custom exception when is

    Args:
        args (list): list of args to get checked

    Raises:
        DATA_NOT_FOUND_EXCEPTION: Raised with custom error field to indicate that value is None
    """
    
    for arg in args:
        if not arg:
            raise DATA_NOT_FOUND_EXCEPTION(error='Data is None where it shouldn\'t be.')

def get_user_id():
    # Helper to get user_id from session or arguments
    if 'user_id' in session:
        return session['user_id']
    if request.args.get('user_id'):
        return request.args.get('user_id')
    # fallback for testing
    if request.json and 'user_id' in request.json:
        return request.json['user_id']
    return None