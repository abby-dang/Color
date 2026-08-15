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
            pin = body.get("pin") #if registering as nail tech

            response = auth.sign_up(email, password, firstName, lastName, phone)

            if response is None or isinstance(response, dict):
                return JsonResponse({"Error": "Registration failed"}, status=400)

            #check if registering through invitation
            metadata = response
            shop_id = metadata.get("shop_id")
            commission_rate = metadata.get("commission_rate")

            if shop_id and commission_rate:
                tech = Techs()
                tech.register_tech(shop_id, response.data[0]["user_id"], commission_rate, pin)

            return JsonResponse({
                "userID": str(response.data[0]["user_id"]),
                "firstName": response.data[0]["first_name"],
                "lastName": response.data[0]["last_name"]
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)

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