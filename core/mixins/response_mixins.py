from rest_framework import status
from rest_framework.response import Response

class APIResponseMixin(object):
    """
    A mixin that provides standardized API responses.
    Methods within this mixin are instance methods, allowing them to be called via 'self'.
    """
    def success_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Returns a JSON Success API response.
        :param data: The data payload for the response.
        :param message: A descriptive success message.
        :param status_code: The HTTP status code (default: 200 OK).
        """
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        return Response(response_data, status=status_code)

    def error_response(self, errors=None, message="An error occurred", status_code=status.HTTP_400_BAD_REQUEST):
        """
        Returns a standardized error API response.
        'errors' can be a dictionary (e.g., from serializer.errors) or a list of error details.
        'message' provides a high-level description of the error.
        """
        response_data = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {}
        }
        return Response(response_data, status=status_code)

    def validation_error_response(self, serializer_errors, message="Validation failed",
                                  status_code=status.HTTP_400_BAD_REQUEST):
        """
        Returns a standardized response for validation errors from a serializer.
        This method reuses the core error_response logic.
        :param serializer_errors: The errors dictionary obtained from serializer.errors.
        :param message: A descriptive message for the validation failure.
        :param status_code: The HTTP status code (default: 400 Bad Request).
        """
        # Calls the instance method error_response
        return self.error_response(
            errors=serializer_errors,
            message=message,
            status_code=status_code
        )