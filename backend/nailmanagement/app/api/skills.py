import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.skills import Skills
from nailmanagement.app.db.supabase_client import supabase


skills = Skills()

@csrf_exempt #remove after testing from Postman
def add_skill(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body["name"]

            uuid = request.supabase_user.user.id #gets the user's uuid
            response = skills.add_skill(uuid, name)

            return JsonResponse({
                "skill_id": str(response["skill_id"]),
                "name": response["name"]
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)

def get_skills(request):
    if request.method == "GET":
        try:
            uuid = request.supabase_user.user.id #gets the user's uuid
            response = skills.get_skills()

            return JsonResponse({
                "skills": response
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)

@csrf_exempt #remove after testing from Postman
def get_skills_by_name(request, name):
    if request.method == "GET":
        try:
            uuid = request.supabase_user.user.id #gets the user's uuid
            response = skills.get_skill_by_name(name)

            return JsonResponse({
                "skills": response
            })
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status = 400)