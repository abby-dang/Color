import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.auth import UserAuthentication
from nailmanagement.app.services.techs import Techs

auth = UserAuthentication()

@csrf_exempt #remove after testing from Postman
def register(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body["email"]
            password = body["password"]
            firstName = body["firstName"]
            lastName = body["lastName"]
            phone = body["phone"]
            
            response = auth.sign_up(email, firstName, lastName, phone, password = password)

            if response is None:
                return JsonResponse({"Error": "Registration failed"}, status=400)

            return JsonResponse({
                "userID": str(response["user_id"]),
                "firstName": response["first_name"],
                "lastName": response["last_name"]
            })
        
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)
        
@csrf_exempt
def complete_invite(request):
    if request.method == "POST":
        body = json.loads(request.body)

        email = body["email"]
        firstName = body["firstName"]
        lastName = body["lastName"]
        phone = body["phone"]
        uuid = request.supabase_user.user.id
        try:

            response = auth.sign_up(email, firstName, lastName, phone, uuid=uuid)

            if response is None:
                return JsonResponse({"Error": "Registration failed"}, status=400)
            
            pin = body["pin"]
            metadata = request.supabase_user.user.user_metadata
            
            shop_id = metadata.get("shop_id")
            commission_rate = metadata.get("commission_rate")

            tech = Techs()

            tech_response = tech.register_tech(shop_id, response["user_id"], commission_rate, pin)

            if tech_response is None:
                return JsonResponse({"Error": "Tech registration failed"}, status=400)

            return JsonResponse(response, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

        
@csrf_exempt #remove after testing from Postman
def sign_in(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            email = body["email"]
            password = body["password"]

            response = auth.login(email, password)
            return JsonResponse({
                "id": str(response.user.id),
                "email": response.user.email,
                "token": response.session.access_token if response.session else None
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)
        
@csrf_exempt
def sign_out(request):

    if request.method == "POST":
        try:
            response = auth.logout()
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 500)
    else:
        return JsonResponse({"error": "Method not allowed"}, status = 405)