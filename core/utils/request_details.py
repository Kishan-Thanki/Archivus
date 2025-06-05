def get_request_details(request):
    """
    Extracts and organizes key details from an incoming request.
    """
    details = {
        'method': request.method,
        'path': request.path,
        'full_path': request.get_full_path(),
        'remote_addr': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT', 'N/A'),
        'content_type': request.META.get('CONTENT_TYPE', 'N/A'),
        'content_length': request.META.get('CONTENT_LENGTH', '0'),
        'http_host': request.META.get('HTTP_HOST'),
        'accept_header': request.META.get('HTTP_ACCEPT'),
        'is_authenticated': request.user.is_authenticated,
        'user_id': request.user.id if request.user.is_authenticated else None,
    }
    return details