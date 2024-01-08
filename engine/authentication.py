# import json
# import os
#
# from django.http import JsonResponse
# from django.conf import settings
# import hashlib
# import hmac
# from functools import wraps
#
#
# def validate_signature(payload, signature):
#     """
#     Validate the incoming payload's signature against our expected signature.
#     """
#     # Ensure the payload is encoded to bytes
#     payload_bytes = payload.encode('utf-8')
#
#     expected_signature = hmac.new(
#         bytes(os.getenv("APP_SECRET"), 'utf-8'),  # Encoding the key as well
#         msg=payload_bytes,
#         digestmod=hashlib.sha256
#     ).hexdigest()
#
#     print(expected_signature, signature)
#
#     return hmac.compare_digest(expected_signature, signature)
#
#
# def signature_required(view_func):
#     """
#     Decorator for class-based views to ensure that the incoming requests are valid and signed with the correct signature.
#     """
#     @wraps(view_func)
#     def _wrapped_view(request, *args, **kwargs):
#         signature_header = request.META.get('HTTP_X_HUB_SIGNATURE_256')
#         if signature_header:
#             signature = signature_header[7:]  # Removing 'sha256='
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Missing signature'}, status=403)
#
#         if not validate_signature(json.dumps(request.data), signature):
#             return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=403)
#
#         return view_func(request, *args, **kwargs)
#
#     return _wrapped_view
import json
import os
import hmac
import time
import hashlib
from users.models import User
from rest_framework import exceptions, authentication


def create_sha256_signature(payload, signature):

    # Ensure the payload is encoded to bytes
    payload_bytes = json.dumps(payload)

    # expected_signature = hmac.new(
    #     bytes(os.getenv("APP_SECRET"), 'utf-8'),  # Encoding the key as well
    #     msg=str(payload).encode('utf-8'),
    #     digestmod=hashlib.sha256
    # ).hexdigest()
    # print(expected_signature, signature)
    # print(hmac.compare_digest(expected_signature, signature))
    # # return hmac.compare_digest(expected_signature, signature)
    # return True

    # Create a SHA256 HMAC object using the secret
    hmac_object = hmac.new(os.getenv("APP_SECRET").encode('utf-8'), payload_bytes.encode('utf-8'), hashlib.sha256)
    # Generate the hex digest of the HMAC object
    generated_signature = hmac_object.hexdigest()
    print(generated_signature, signature)
    return generated_signature == signature


class HMACAuthentication(authentication.BaseAuthentication):
    """
    Custom Authentication to secure APIs
    """

    def authenticate(self, request):
        # We'll get the token from header with key 'Authorization'
        # We are expecting token to be in format: "Token (Actual encrypted key)"
        token = request.META.get('HTTP_X_HUB_SIGNATURE_256')

        print(token)
        # print(request.data)
        signature = token[7:]
        print(signature)
        create_sha256_signature(request.data, signature)