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

            service_ids = []
            tech_ids = []
            for service in services:
                service_ids.append(service["service_id"])
                tech_ids.append(service["tech_id"])
                
            appointment = appointments.create_appointment(client_id, shop_id, notes, service_ids, status, date, time, tech_ids)

            return JsonResponse(appointment, safe = False)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=400)

def get_appointment_by_date(request, shop_id):
    if request.method == "GET":
        day = request.GET.get("day")
        uuid = request.supabase_user.user.id
        try:
            
            response = appointments.get_appointments_by_day(uuid, shop_id, day)

            return JsonResponse(response, safe = False)

        except Exception as e:

            return JsonResponse({"Error": str(e)}, status = 400)


def get_appointment_by_client(request, shop_id):
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


        