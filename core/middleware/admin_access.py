# import logging
#
# from django.urls import reverse, NoReverseMatch
# from django.http import HttpResponseNotFound
# from django.shortcuts import redirect
#
# logger = logging.getLogger(__name__)
#
# class AdminAccessMiddleware():
#     def __init__(self, get_response):
#         self.get_response = get_response
#
#     def __call__(self, request):
#         try:
#             admin_url_prefix = reverse('admin:index')
#         except NoReverseMatch:
#             logger.error('admin url prefix not found')
#             admin_url_prefix = '/admin/'
#
#         if request.path.startswith(admin_url_prefix):
#             if request.user.is_authenticated and request.user.is_staff:
#                 pass
#             else:
#                 logger.info(f"Unauthorized access attempt to admin by user: {request.user.email if request.user.is_authenticated else 'Anonymous'}")
#                 return HttpResponseNotFound()
#
#         response = self.get_response(request)
#         return response