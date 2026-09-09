from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.utils import generate_tech_pin, hash_pin, verify_pin
from nailmanagement.app.services.db_helpers import get_user_id, get_owner_id, is_tech
import datetime
class Techs:

    def register_tech(self, shop_id: int, user_id: int, commission_rate: int):
        """
        Registers a tech for a specific shop by inserting the tech information into the database table
        
        Args:
            shop_id (int): The ID of the shop
            user_id (int): The ID of the tech user
            commission_rate (int): The commission rate for the tech
                
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

            pin = generate_tech_pin()
            hashed_pin = hash_pin(pin)

            print(f"Generated pin for tech {user_id} in shop {shop_id}: {pin}")

            response = (
                supabase.table("techs")
                .insert({
                    "shop_id": shop_id,
                    "user_id": user_id,
                    "commission_rate": commission_rate,
                    "pin_hash": hashed_pin
                })
                .execute()
            )

            return response

        except Exception as e:
            print(f"Error registering tech for shop {shop_id}")
            raise e

    def verify_pin(self, user_id: int, shop_id: int, pin: str) -> bool:
        """
        Verifies the provided pin for a specific tech user in a specific shop by comparing it with the stored pin hash in the database
        
        Args:
            user_id (int): The ID of the tech user
            shop_id (int): The ID of the shop
            pin (str): The pin to verify

        Returns:
            bool: True if the pin is valid, False otherwise

        Raises:
            ValueError: If the tech user is not found or the pin is invalid
        """
        try:

            if is_tech(user_id, shop_id) is False:
                raise ValueError("User is not a tech for this shop")

            data = (
                    supabase.table("techs")
                    .select("pin_hash")
                    .eq("shop_id", shop_id)
                    .eq("user_id", user_id)
                    .execute().data[0]
                )
            
            if data['pin_hash'] is None:
                raise ValueError("Tech does not have a pin set")

            verified = verify_pin(pin, data['pin_hash'])

            return verified

        except Exception as e:
            print(f"Error verifying pin for tech {user_id} in shop {shop_id} : {e}")
            raise e
        
    def generate_new_pin(self, user_id: int, shop_id: int, current_pin: str = None):
        """
        Generates a new pin for a specific tech user in a specific shop
        
        Args:
            user_id (int): The ID of the tech user
            shop_id (int): The ID of the shop
            pin (str): The new pin
            current_pin (str, optional): The current pin for verification

        Returns:
            dict: The response from the database update operation

        Raises:
            ValueError: If the tech user is not found or the pin is invalid
        """
        try:
            data = (
                supabase.table("techs")
                .select("pin_hash")
                .eq("shop_id", shop_id)
                .eq("user_id", user_id)
                .execute().data[0]
            )

            if is_tech(user_id, shop_id) is False:
                raise ValueError("User is not a tech for this shop")

            if data.get("pin_hash"):
                verified = verify_pin(current_pin, data["pin_hash"])
                if not verified:
                    raise ValueError("Current pin is incorrect")
                
            pin = generate_tech_pin()
            
            hashed_pin = hash_pin(pin)

            #TODO: Send pin to tech via email or sms
            print(f"Generated new pin for tech {user_id} in shop {shop_id}: {pin}")

            response = (
                supabase.table("techs")
                .update({"pin_hash": hashed_pin})
                .eq("user_id", user_id)
                .eq("shop_id", shop_id)
                .execute()
            )

            return response

        except Exception as e:
            print(f"There was an error updating tech pin : {e}")
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

    def clock_in_tech(self, user_id: int, shop_id: int, pin: str):
        """
        Signs in a tech user for a specific shop by verifying the provided pin
        
        Args:
            user_id (int): The ID of the tech user
            shop_id (int): The ID of the shop
            pin (str): The pin to verify

        Returns:
            bool: True if the sign-in is successful, False otherwise

        Raises:
            ValueError: If the tech user is not found or the pin is invalid
        """
        try:
            if not is_tech(user_id, shop_id):
                raise ValueError("User is not a tech for this shop")

            data = (
                supabase.table("techs")
                .select("pin_hash, tech_id")
                .eq("shop_id", shop_id)
                .eq("user_id", user_id)
                .execute().data[0]
            )

            if verify_pin(pin, data['pin_hash']):
                response = (
                    supabase.table("tech_attendance")
                    .insert({
                        "tech_id": data["tech_id"],
                        "shop_id": shop_id,
                        "check_in": datetime.datetime.now().isoformat()
                    })
                    .execute()
                )

            return response

        except Exception as e:
            print(f"Error signing in tech {user_id} for shop {shop_id} : {e}")
            raise e

    def clock_out_tech(self, user_id: int, shop_id: int):
        """
        Signs out a tech user for a specific shop by updating the check-out time in the database
        
        Args:
            user_id (int): The ID of the tech user
            shop_id (int): The ID of the shop   

        Returns:
            dict: The response from the database update operation
        Raises:
            ValueError: If the tech user is not found or there is no active check-in record
        """
        try:
            if not is_tech(user_id, shop_id):
                raise ValueError("User is not a tech for this shop")

            data = (
                supabase.table("techs")
                .select("tech_id")
                .eq("shop_id", shop_id)
                .eq("user_id", user_id)
                .execute().data[0]
            )

            tech_id = data["tech_id"]

            # Get the latest check-in record for the tech
            attendance_record = (
                supabase.table("tech_attendance")
                .select("*")
                .eq("tech_id", tech_id)
                .eq("shop_id", shop_id)
                .order("check_in", desc=True)
                .limit(1)
                .execute().data
            )

            if not attendance_record:
                raise ValueError("No active check-in record found for this tech")

            attendance_record = attendance_record[0]

            # Update the check-out time
            response = (
                supabase.table("tech_attendance")
                .update({"check_out": datetime.datetime.now().isoformat()})
                .eq("attendance_id", attendance_record["attendance_id"])
                .execute()
            )

            return response

        except Exception as e:
            print(f"Error signing out tech {user_id} for shop {shop_id} : {e}")
            raise e