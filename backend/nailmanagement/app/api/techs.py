import json
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

