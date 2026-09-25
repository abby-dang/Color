from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.db_helpers import is_authorized
class Clients:
    def __init__(self):
        self.supabase = supabase

    def create_new_client(self, shop_id: int, first_name: str, last_name: str, email: str, phone: str, notes: str = None):
        """
        Creates a client in a shop, or returns the existing one with the same email.

        Args:
            shop_id (int): The shop's ID
            first_name (str): The client's first name
            last_name (str): The client's last name
            email (str): The client's email
            phone (str): The client's phone number
            notes (str): Optional notes about the client

        Returns:
            list: The new client record, or the existing matches if the email
                is already in the shop

        Raises:
            Exception: if the query or insert fails
        """
        try:

            client = (
                self.supabase.table("clients")
                .select("*")
                .eq("shop_id", shop_id)
                .eq("email", email)
                .execute()
            ).data
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

    def get_client(self, uuid: str, shop_id: int, client_id: int = None, last_name: str = None, first_name: str = None, email: str = None, phone: str = None):
        """
        Searches a shop's clients. Filters are combined; with none, every
        client in the shop is returned.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            client_id (int): Exact match
            last_name (str): Partial, case-insensitive match
            first_name (str): Partial, case-insensitive match
            email (str): Exact match
            phone (str): Exact match

        Returns:
            list: The matching client records

        Raises:
            ValueError: if the user is not authorized
            Exception: if the query fails
        """
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User not authorized")
            
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
        """
        Updates a client's details. Only the fields provided are changed.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            client_id (int): The client to update
            last_name (str): New last name
            first_name (str): New first name
            email (str): New email
            phone (str): New phone number

        Returns:
            dict: A "Message" saying whether the client was updated

        Raises:
            ValueError: if the user is not authorized or no fields are given
            Exception: if the update fails
        """
        try:
            if not is_authorized(uuid, shop_id):
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
    