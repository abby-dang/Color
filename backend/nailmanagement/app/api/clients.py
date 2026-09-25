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

def get_client(request, shop_id):
    if request.method == "GET":
        uuid = request.supabase_user.user.id
        try:
            client_id = request.GET.get("client_id")
            last_name = request.GET.get("last_name")
            first_name = request.GET.get("first_name")
            email = request.GET.get("email")
            phone = request.GET.get("phone")

            response = clients.get_client(uuid, shop_id, client_id= client_id, last_name=last_name, first_name=first_name, email=email, phone= phone)

            return JsonResponse(response, safe = False)

        except Exception as e:

            return JsonResponse({"Error": str(e)}, status = 400)

@csrf_exempt
def update_client(request, shop_id, client_id):
    if request.method == "PUT":
        try:
            uuid = request.supabase_user.user.id

            body = json.loads(request.body)
            first_name = body.get("first_name")
            last_name = body.get("last_name")
            email = body.get("email")
            phone = body.get("phone")

            response = clients.update_client(uuid, shop_id, client_id, last_name=last_name, first_name=first_name, email=email, phone=phone)

            return JsonResponse(response, safe = False)

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)
        

    