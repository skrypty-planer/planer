from ..error_handling.logger import logger
from ..error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION

def singleton(class_):
    instance = None
    
    def get_instance(args: list):
        if instance is None:
            instance = class_(*args)
        return instance
    
    return get_instance

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