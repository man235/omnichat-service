
def pagination_list_data(data, limit, offset):
    if data:
        limit_req = limit
        offset_req = offset
        if not limit_req:
            limit_req = 10
        if not offset_req:
            offset_req = 1
        _end = int(offset_req) * int(limit_req)
        _start = int(_end) - int(limit_req)
        data_result = {
            "count": len(data),
            "data": data[_start:_end]
        }
        return data_result
    else:
        return data_result
