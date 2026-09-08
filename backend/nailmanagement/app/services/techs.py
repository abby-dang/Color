from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.utils import hash_pin, verify_pin
from nailmanagement.app.services.db_helpers import get_user_id, get_owner_id, is_tech
class Techs:

    def register_tech(self, shop_id: int, user_id: int, commission_rate: int, pin: str = None):
        """
        Registers a tech for a specific shop by inserting the tech information into the database table
        
        Args:
            shop_id (int): The ID of the shop
            user_id (int): The ID of the tech user
            commission_rate (int): The commission rate for the tech
            pin (str, optional): The PIN for the tech. Defaults to None.
                
        Returns:
            dict: Newly registered tech record
        
        Raises:
            Exception: If there is an error during the registration process
        """
        #check if tech already exists
        try:
            tech = (
                supabase.table("techs")
                .select("user_id, shop_id")
                .eq("user_id", user_id)
                .eq("shop_id", shop_id)
                .execute().data
            )

            if tech:
                return 
            
            pin_hash = None
            if pin:
                pin_hash = hash_pin(pin)
            response = (
                supabase.table("techs")
                .insert({
                    "shop_id": shop_id,
                    "user_id": user_id,
                    "commission_rate": commission_rate,
                    "pin_hash": pin_hash
                    
                })
                .execute()
            )

            return response

        except Exception as e:
            print(f"Error registering tech for shop {shop_id}")
            raise e

    def change_pin(self, user_id: int, tech_id: int, shop_id: int, pin: str):
        try:
            tech = (
                supabase.table("techs")
                .select("user_id")
                .eq("shop_id", shop_id)
                .eq("tech_id", tech_id)
                .execute().data[0]["user_id"]
            )

            if user_id != tech:
                raise ValueError("Unauthorized access")

            if len(pin) != 4:
                raise ValueError("Pin must be exactly 4 digits long")

            hashed_pin = hash_pin(pin)

            response = (
                supabase.table("techs")
                .update({"pin_hash": hashed_pin})
                .eq("tech_id", tech_id)
                .execute()
            )

            return response

        except Exception as e:
            print("There was an error updating tech pin")
            raise e

    def get_tech_shops(self, uuid: str):
        """
        Retrieves the shops associated with a specific tech user by querying the database table
        
        Args:
            uuid (str): The UUID of the tech user
            
        Returns:
            list: List of shops associated with the tech user
            
        Raises:
            Exception: If there is an error during the retrieval process
        """
        try:
            userID = get_user_id(uuid)

            if userID == -1:
                raise ValueError("User not found")
            
            response = (
                supabase.table("techs")
                .select("shop_id, commission_rate, shops(name)")
                .eq("user_id", userID)
                .execute()
            )

            if not response.data:
                return []

            return response.data
        
        except Exception as e:
            print(f"Error retrieving shops for tech {uuid}")
            raise e