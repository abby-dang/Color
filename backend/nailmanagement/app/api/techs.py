import json
from urllib import response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.techs import Techs

tech = Techs()

def get_tech_shops(request):
    if request.method == "GET":
        try:
            uuid = request.supabase_user.user.id #gets the user's uuid
            response = tech.get_tech_shops(uuid)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving shops"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)
@csrf_exempt
def verify_tech_pin(request, user_id, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            pin = body["pin"]

            print(f"Verifying pin for tech {user_id} in shop {shop_id} with pin {pin}")
            response = tech.verify_pin(user_id, shop_id, pin)
            
            if response is None:
                return JsonResponse({"Error": "There was an issue verifying the pin"}, status = 400)

            return JsonResponse({"is_valid": response})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

@csrf_exempt
def change_pin(request, user_id, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            pin = body["pin"]
            current_pin = body.get("current_pin", None)
            response = tech.change_pin(user_id, shop_id, pin, current_pin)

            if response is None:
                return JsonResponse({"Error": "There was an issue updating the pin"}, status = 400)

            return JsonResponse({"message": "Pin updated successfully"})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)