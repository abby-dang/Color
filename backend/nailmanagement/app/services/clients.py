from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.db_helpers import get_user_id
class Clients:
    def __init__(self):
        self.supabase = supabase

    def create_new_client(self, shop_id: int, first_name: str, last_name: str, email: str, phone: str, notes: str = None):
        """
        """
        try:

            client = self.get_client(shop_id, email = email)
            if not client:
            #search client email, if no email proceed to create new client
                response = (
                    self.supabase.table("clients")
                    .insert({
                        "shop_id": shop_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": phone,
                        "notes": notes
                            })
                        .execute()
                )
            
                return response.data
            
            return client
        except Exception as e:
            print(f"Error inserting client data")
            raise e

    def get_client(self, shop_id: int, client_id: int = None, last_name: str = None, first_name: str = None, email: str = None, phone: str = None):
        """

        """
        try:
            query = self.supabase.table("clients").select("*").eq("shop_id", shop_id)

            if client_id:
                query = query.eq("client_id", client_id)
            if last_name:
                query = query.ilike("last_name", f"%{last_name}%")
            if first_name:
                query = query.ilike("first_name", f"%{first_name}%")
            if email:
                query = query.eq("email", email)
            if phone:
                query = query.eq("phone", phone)

            response = query.execute()
            
            return response.data
        except Exception as e:
            print(f"Error searching for client")
            raise e

    def update_client(self, uuid: str, shop_id: int, client_id: int, last_name: str = None, first_name: str = None, email: str = None, phone: str = None):

        try:
            user_id = get_user_id(uuid)
            if user_id == -1:
                raise ValueError("Unauthorized access")

            update_data = {}

            if first_name is not None:
                update_data["first_name"] = first_name
            if last_name is not None:
                update_data["last_name"] = last_name
            if email is not None:
                update_data["email"] = email
            if phone is not None:
                update_data["phone"] = phone

            if not update_data:
                raise ValueError("No fields to update provided")

            response = (
                self.supabase.table("clients")
                .update(update_data)
                .eq("shop_id", shop_id)
                .eq("client_id", client_id)
                .execute()
            )

            if response.data:
                return {"Message": "Client updated successfully"}
            else:
                return{"Message": "Client not found or no changes have been made"}

        except Exception as e:
            print(f"Error updating client: {e}")
            raise e
    