# import pytest
# from flask import g, session
# from .__init__ import client, app
# from ..src.utilities.global_utils import check_if_data_is_not_None

# @pytest.mark.parametrize(('data'), (
#     (''),
#     ([]),
#     (['']),
#     (['test', 'test123', 200]),
# ))
# def test_check_if_data_is_not_None(client, data):
#     try:
#         check_if_data_is_not_None(data)
#     except Exception as ex:
#         raise ex