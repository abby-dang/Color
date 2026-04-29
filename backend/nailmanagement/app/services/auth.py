from nailmanagement.app.db.supabase_client import supabase
class UserAuthentication:

    def sign_up(self, email: str, password: str, firstName: str, lastName: str, phone: str):
        auth = supabase.auth.sign_up(
            {
                "email": email, #format: email@example.com
                "password": password
            }
        )

        if auth.user is not None: 
            response = (
                supabase.table("users")
                .insert({"uuid": auth.user.id, "email": email, "first_name": firstName, "last_name": lastName, "phone": phone, "is_active": True})
                .execute()
            )
            return response
        
        #TODO: determine best return response
        #TODO: error handling for existing accounts or other errors

        return auth

    def login(self, email: str, password: str):
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
                "password": password
            }
        )

        #TODO: error handling for invalid login
        return response