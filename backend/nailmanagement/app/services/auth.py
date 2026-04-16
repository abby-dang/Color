from nailmanagement.app.db.supabase_client import supabase
class UserAuthentication:

    def sign_up(self, email: str, password: str):
        response = supabase.auth.sign_up(
            {
                "email": email, #format: email@example.com
                "password": password 
            }
        )
        return response
