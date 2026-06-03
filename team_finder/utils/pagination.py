from team_finder.constants import QueryParam


def build_query_prefix(request):
    params = request.GET.copy()
    params.pop(QueryParam.PAGE, None)
    prefix = params.urlencode()
    if prefix:
        prefix += '&'
    return prefix
