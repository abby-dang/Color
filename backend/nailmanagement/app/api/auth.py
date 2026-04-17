import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.auth import UserAuthentication

auth = UserAuthentication()

#Add checks for duplicate emails/usernames
@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body["email"]
            password = body["password"]

            response = auth.sign_up(email, password)
            return JsonResponse({
                "id": str(response.user.id),
                "email": response.user.email,
                "token": response.session.access_token if response.session else None
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)
    