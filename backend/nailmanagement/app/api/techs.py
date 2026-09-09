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
def verify_tech_pin(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            pin = body["pin"]

            response = tech.verify_pin(request.supabase_user.user.id, shop_id, pin)
            
            if response is None:
                return JsonResponse({"Error": "There was an issue verifying the pin"}, status = 400)

            return JsonResponse({"is_valid": response})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

@csrf_exempt
def generate_new_pin(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            current_pin = body.get("current_pin", None)
            response = tech.generate_new_pin(request.supabase_user.user.id, shop_id, current_pin)

            if response is None:
                return JsonResponse({"Error": "There was an issue generating the new pin"}, status = 400)

            return JsonResponse({"message": "Pin generated successfully"})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)
@csrf_exempt
def clock_in_tech(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            pin = body["pin"]
            response = tech.clock_in_tech(request.supabase_user.user.id, shop_id, pin)

            if response is None:
                return JsonResponse({"Error": "There was an issue signing in the tech"}, status = 400)

            return JsonResponse({"message": "Tech signed in successfully"})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

@csrf_exempt
def clock_out_tech(request, shop_id):
    if request.method == "POST":
        try:
            response = tech.clock_out_tech(request.supabase_user.user.id, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue signing out the tech"}, status = 400)

            return JsonResponse({"message": "Tech signed out successfully"})

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)