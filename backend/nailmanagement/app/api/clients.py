import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.clients import Clients

clients = Clients()

@csrf_exempt
def create_new_client(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            first_name = body["first_name"]
            last_name = body["last_name"]
            email = body["email"]
            phone = body["phone"]
            notes = body.get("notes", None)

            client = clients.create_new_client(shop_id, first_name, last_name, email, phone, notes)

            return JsonResponse(client, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)