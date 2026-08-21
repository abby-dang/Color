import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.db.supabase_client import supabase