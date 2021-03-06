def response_checker(item, ret_val, res_code=200, err_msg: str = 'no data found', err_num: int = 404):
    additional = {'Access-Control-Allow-Origin': '*'}
    if item is None:
        return {'message': err_msg}, err_num, additional
    else:
        return ret_val, res_code, additional
