from nailmanagement.app.db.supabase_client import supabase

class Appointments:
    def get_appointments(self, shop_id):
        try:
            response = supabase.table("appointments").select("*").eq("shop_id", shop_id).execute()
            if response.data:
                return response.data
            else:
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None