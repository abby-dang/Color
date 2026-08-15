from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.utils import hash_pin, verify_pin
class Techs:

    def register_tech(self, shop_id: int, user_id: int, commission_rate: int, pin: str = None):
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
    
            response = (
                supabase.table("techs")
                .insert({
                    "shop_id": shop_id,
                    "user_id": user_id,
                    "commission_rate": commission_rate,
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