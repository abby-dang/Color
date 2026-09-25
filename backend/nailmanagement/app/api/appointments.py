import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.appointments import Appointments
from nailmanagement.app.db.supabase_client import supabase
appointments = Appointments()

@csrf_exempt
def create_appointment(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            client_id = body["client_id"]
            notes = body.get("notes", "")
            date = body.get("date")
            time = body.get("time")
            services = body.get("services")
            status = body.get("status", "pending")
   
            appointment = appointments.create_appointment(client_id, shop_id, notes, services, status, date, time)

            return JsonResponse(appointment, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=400)

def get_appointments_by_date(request, shop_id):
    if request.method == "GET":
        day = request.GET.get("day")
        uuid = request.supabase_user.user.id
        try:
            
            response = appointments.get_appointments_by_day(uuid, shop_id, day)

            return JsonResponse(response, safe = False)

        except Exception as e:

            return JsonResponse({"Error": str(e)}, status = 400)


def get_appointments_by_client(request, shop_id):
    if request.method == "GET":
        client_id = request.GET.get("client_id", None)
        first_name = request.GET.get("first_name", None)
        last_name = request.GET.get("last_name", None)
        phone = request.GET.get("phone", None)
        email = request.GET.get("email", None)
        uuid = request.supabase_user.user.id
        try:

            response = appointments.get_appointments_by_client(uuid, shop_id, client_id = client_id, first_name=first_name, last_name=last_name, phone=phone,email=email)

            return JsonResponse(response, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)


def get_appointments_by_tech(request, shop_id):
    if request.method == "GET":
        uuid = request.supabase_user.user.id
        tech_id = request.GET.get("tech_id", None)

        try:
            response = appointments.get_appointments_by_tech(uuid, shop_id, tech_id)

            return JsonResponse(response, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

def get_appointment(request, shop_id: int, appointment_id: int):
    if request.method == "GET":
        uuid = request.supabase_user.user.id

        try:
            response = appointments.get_appointment(uuid, shop_id, appointment_id)

            return JsonResponse(response, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)

@csrf_exempt
def update_appointment(request, shop_id: int, appointment_id: int):
    if request.method == "PUT":
        uuid = request.supabase_user.user.id

        try:
            body = json.loads(request.body)
            notes = body.get("notes", None)
            services = body.get("services", None)
            status = body.get("status", None)
            date = body.get("date", None)
            time = body.get("time", None)

            response = appointments.update_appointment(uuid, shop_id, appointment_id, notes=notes, services=services, status=status, date=date, time=time)

            return JsonResponse(response, safe = False)

        except Exception as e:
            return JsonResponse({"Error": str(e)}, status = 400)