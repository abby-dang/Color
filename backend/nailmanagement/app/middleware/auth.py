from nailmanagement.app.db.supabase_client import supabase
import json
from django.http import JsonResponse

class AuthMiddleware:
    def __init__ (self, get_response):
        self.get_response = get_response

    def __call__ (self, request):
        
        #Exclude the register and sign_in as these do not need a token to request
        excluded_routes = ["/api/auth/register/", "/api/auth/login/"]

        if request.path in excluded_routes:
            return self.get_response(request)
        
        print(f"Path: {request.path}") #remove after testing

        token = request.headers.get("Authorization", "").replace("Bearer ", "")

        print(f"Token: {token}")#remove after testing
    
        if token:
            try:
                user = supabase.auth.get_user(token)
                
                request.supabase_user = user

                print(f"User set: {user}") #remove after testing
            except Exception as e:

                print(f"Auth error: {e}") #remove after testing
                
                return JsonResponse({"error": "Invalid or expired token"}, status=401)

        return self.get_response(request)