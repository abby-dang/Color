import json
from django.http import JsonResponse
from nailmanagement.app.services.auth import UserAuthentication

auth = UserAuthentication()

#Add checks for duplicate emails/usernames
def register(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body["email"]
        password = body["password"]

        response = auth.sign_up(email, password)
        return JsonResponse({"user": response.user, "token": response.session.access_token})
    