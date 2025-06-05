import logging
import time

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        method = request.method
        path = request.path
        full_path = request.get_full_path()
        remote_addr = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', 'N/A')
        content_type = request.META.get('CONTENT_TYPE', 'N/A')
        user_id = request.user.id if request.user.is_authenticated else 'Anonymous'

        logger.info(
            f"Incoming Request | User: {user_id} | Method: {method} | Path: {full_path} | "
            f"IP: {remote_addr} | Agent: {user_agent} | Content-Type: {content_type}"
        )

        response = self.get_response(request)

        duration = time.time() - start_time
        logger.info(
            f"Outgoing Response | User: {user_id} | Method: {method} | Path: {full_path} | "
            f"Status: {response.status_code} | Duration: {duration:.4f}s"
        )

        return response