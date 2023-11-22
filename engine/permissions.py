from rest_framework.permissions import BasePermission


class HaveCredits(BasePermission):
    message = 'You Have Exceeded Your Credits Limit Buy Credits : {}'.format("https://homelinked.tech/")

    def has_permission(self, request, view):
        if request.user.credits <= 0:
            return False
        return True
