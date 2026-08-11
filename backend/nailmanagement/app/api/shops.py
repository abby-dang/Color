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
        
@csrf_exempt
def getCommissionTotal(request):
    
    if request.method == "GET":
        uuid = request.supabase_user.user.id #gets the user's uuid
        try:
            body = json.loads(request.body)
            shopID = body["shop_id"]
            response = shops.get_shop_commission_total(shopID, uuid)

            if response is None:
                return JsonResponse({"Error":"There was an issue retrieving the total commissions"}, status = 400)

            return JsonResponse({
                "shop_id": shopID,
                "totalCommissions": str(response) 
            })

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)