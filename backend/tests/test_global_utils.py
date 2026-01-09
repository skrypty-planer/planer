
import pytest
from flask import Flask, session
from .conftests import app, client
from ..src.utilities.global_utils import check_if_data_is_not_None, get_user_id
from ..src.error_handling.exceptions import DATA_NOT_FOUND_EXCEPTION

@pytest.mark.parametrize("data, should_raise", [
    (['valid', 123, True], False),
    (['', 'valid'], True),
    ([None, 'valid'], True),
    ([], False), # Empty list of args itself is valid (loops 0 times)
    ([0], True), # 0 is falsy, check_if_data_is_not_None raises on falsy
    ([False], True) # False is falsy
])
def test_check_if_data_is_not_None(data, should_raise):
    if should_raise:
        with pytest.raises(DATA_NOT_FOUND_EXCEPTION):
            check_if_data_is_not_None(data)
    else:
        check_if_data_is_not_None(data)

def test_get_user_id(app: Flask, client):
    # 1. From Session
    with client.session_transaction() as sess:
        sess['user_id'] = 'session_user'

    with app.test_request_context():
        session['user_id'] = 'sess_id'
        assert get_user_id() == 'sess_id'

    # 2. From Args
    with app.test_request_context('/?user_id=arg_id'):
        assert get_user_id() == 'arg_id'

    # 3. From JSON
    with app.test_request_context(json={'user_id': 'json_id'}, content_type='application/json'):
        assert get_user_id() == 'json_id'
        
    # 4. Priority: Session > Args > JSON
    with app.test_request_context('/?user_id=arg_id', json={'user_id': 'json_id'}, content_type='application/json'):
        session['user_id'] = 'sess_id'
        assert get_user_id() == 'sess_id'
        
    with app.test_request_context('/?user_id=arg_id', json={'user_id': 'json_id'}, content_type='application/json'):
        assert get_user_id() == 'arg_id'

    # 5. None
    with app.test_request_context():
        assert get_user_id() is None
