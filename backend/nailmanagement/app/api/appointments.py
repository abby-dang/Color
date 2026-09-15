import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.appointments import Appointments

appointments = Appointments()

@csrf_exempt
def create_appointment(request, shop_id):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            client_name = body["client_name"]
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
                
            appointment = appointments.create_appointment(client_name, shop_id, notes, service_ids, status, date, time, tech_ids)

            return JsonResponse(appointment)
        except Exception as e:
            return JsonResponse({"Error": str(e)}, status=400)
