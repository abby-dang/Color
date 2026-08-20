import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.shops import Shops
from nailmanagement.app.db.supabase_client import supabase

shops = Shops()

@csrf_exempt
def register(request):
    if request.method == "POST":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try: 
            body = json.loads(request.body)
    
            ownerId = (
                supabase.table("users")
                .select("user_id")
                .eq("uuid", uuid)
                .execute().data[0]["user_id"]
            )
            address = body["address"]
            phone = body["phone"]
            open_t = body["open_t"]
            close_t = body["close_t"]
            pin = body["pin"]
            email = body["email"]
            name = body["name"]
            close_d = body["close_d"]
            open_d = body["open_d"]

            response = shops.register_shop(name, phone, pin, address, open_t, close_t, email, close_d, open_d, ownerId)

            if response is None:
                return JsonResponse({"Error": "Shop registration failed"}, status = 400)

            return JsonResponse({
                "shopid": str(response["shop_id"]),
                "name": str(response["name"]),
                "owner": str(response["owner_id"]),
                "address": str(response["address"]),
                "phone": str(response["phone"]),
                "email": str(response["email"]),
                "open_t": str(response["open_t"]),
                "close_t": str(response["close_t"]),
                "close_d": str(response["close_d"]),
                "open_d": str(response["open_d"])
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)
        
def get_shops(request, owner_id):

    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try:
            response = shops.get_owner_shops(uuid, owner_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving shops"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)
        
def get_shop_info(request, shop_id):

    if request.method == "GET":

        uuid = request.supabase_user.user.id #gets the user's uuid 

        try:
            response = shops.get_shop_info(uuid, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving shop information"}, status = 400)

            return JsonResponse({
                "shop_id": str(response["shop_id"]),
                "owner_id": str(response["owner_id"]),
                "name": str(response["name"]),
                "address": str(response["address"]),
                "email": str(response["email"]),
                "phone": str(response["phone"]),
                "open_t": str(response["open_t"]),
                "close_t": str(response["close_t"]),
                "open_d": str(response["open_d"]),
                "close_d": str(response["close_d"])
            })

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)


@csrf_exempt
def update_shop_info(request, shop_id):

    if request.method == "PUT":
        uuid = request.supabase_user.user.id #gets the user's uuid
        
        try:
            body = json.loads(request.body)
            user_id = (
                supabase.table("users")
                .select("user_id")
                .eq("uuid", uuid)
                .execute().data[0]["user_id"]
            )
            name = body["name"]
            phone = body["phone"]
            address = body["address"]
            email = body["email"]
            open_t = body["open_t"]
            close_t = body["close_t"]
            open_d = body["open_d"]
            close_d = body["close_d"]
            pin = body["pin"]

            response = shops.update_shop_info(user_id, shop_id, pin, name, phone, address, email, open_t, close_t, close_d, open_d)

            if response is None:
                return JsonResponse({"Error":"There was an issue updating the shop information"})

            return JsonResponse({
                "shop_id": shop_id,
                "name": name,
                "phone": phone,
                "address": address,
                "email": email,
                "open_t": open_t,
                "close_t": close_t,
                "open_d": open_d,
                "close_d": close_d
            })
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

          
@csrf_exempt
def get_shop_commission_total(request, shop_id):
    
    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid
    
        try:
            response = shops.get_shop_commission_total(shop_id, uuid)

            if response is None:
                return JsonResponse({"Error":"There was an issue retrieving the total commissions"}, status = 400)

            return JsonResponse({
                "shop_id": shop_id,
                "totalCommissions": str(response) 
            })

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

def get_shop_techs(request, shop_id):

    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try:
            response = shops.get_shop_techs(uuid, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving the shop technicians"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)

def get_shop_services(request, shop_id):

    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try:
            response = shops.get_shop_services(uuid, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving the shop services"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)

def get_shop_skills(request, shop_id):

    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try:
            response = shops.get_shop_skills(uuid, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving the shop skills"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)

def get_shop_appointments(request, shop_id):

    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid

        try:
            response = shops.get_shop_appointments(uuid, shop_id)

            if response is None:
                return JsonResponse({"Error": "There was an issue retrieving the shop appointments"}, status = 400)

            return JsonResponse(response, safe=False)

        except Exception as e:
            return JsonResponse({"Error" : str(e)}, status = 400)
