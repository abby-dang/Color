import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.shops import Shops

shops = Shops()


def register(request):
    if request.method == "POST":
        try: 
            body = json.loads(request.body)
            address = body["password"]
            phone = body["phone"]
            open_t = body["open_t"]
            close_t = body["close_t"]
            pin = body["pin"]
            email = body["email"]
            name = body["name"]
            close_d = body["close_d"]#need to edit this to give a range of closed days
            open_d = body["open_d"] #need to edit this to give a range of open days

            response = shops.register_shop(name, phone, pin, address, open_t, close_t, email, close_d, open_d)

            if response is None:
                return JsonResponse({"Error": "Shop registration failed"}, status = 400)

            return JsonResponse({
                "name": str(response.data[0]["name"]),
                "owner": str(response.data[0]["owner_id"]),
                "address": str(response.data[0]["address"]),
                "phone": str(response.data[0]["phone"]),
                "email": str(response.data[0]["email"]),
                "open_t": str(response.data[0]["open_t"]),
                "close_t": str(response.data[0]["close_t"]),
                "close_d": str(response.data[0]["close_d"]),
                "open_d": str(response.data[0]["open_d"])
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)