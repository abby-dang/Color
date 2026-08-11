from nailmanagement.app.db.supabase_client import supabase
import re
import time
from nailmanagement.app.services.utils import hash_pin, verify_pin, valid_phone, valid_email, valid_weekdays
class Shops:

    #EDITING SHOP INFO
    def register_shop(self, name: str, phone: str, pin: str, address: str, open_t: time, close_t: time, email: str, close_d: str, open_d: str, ownerID: int):
        #CHECK NAME
        if len(name) > 100:
            raise ValueError("Name of shop is too long")
        
        #CHECK PHONE NUMBER

        if not valid_phone(phone):
            raise ValueError("Phone number incorrect format")
        
        if len(pin) != 5:
            raise ValueError("PIN must be exactly 5 digits")

        if not valid_email(email):
            raise ValueError("Email is in the incorrect format")

        if len(close_d) > 16 or len(open_d) > 16:
            raise ValueError("Invalid input")

        if not valid_weekdays(open_d) or not valid_weekdays(close_d):
            raise ValueError("Invalid days for closing or opening days")
        
        hashed_pin = hash_pin(pin)
        print(f"Hashed pin: {hashed_pin}")
        try:
            response = (
                supabase.table("shops")
                .insert({"name": name, "phone": phone, "pin": hashed_pin, "address": address, "open_t": open_t, "close_t": close_t, "email": email, "close_d": close_d, "open_d": open_d, "owner_id": ownerID})
                .execute()
                )
            
            return response.data[0]
        except Exception as e:
        
            print("Error registering shop")

            raise e


    #FETCHING SHOP INFO 
    #ONLY OWNER CAN VIEW
    def get_shop_commission_total(self, shopID: int, uuid: str) -> float:

        try:
            userID = (
                supabase.table("users")
                .select("user_id")
                .eq("uuid", uuid)
                .execute().data[0]["user_id"]
            )

            ownerID = (
                supabase.table("shops")
                .select("owner_id")
                .eq("shop_id", shopID)
                .execute().data[0]["owner_id"]
            )

            if(ownerID != userID):
                raise ValueError("Invalid Access")
            
            response = (
                supabase.table("commissions")
                .select("service_amount")
                .eq("shop_id", shopID)
                .execute()
            )

            
            if len(response.data) < 1:
                return 0

            else:
                #TODO: FIX THIS SO THAT IT RESPONDS TO THE DATA RETURNED
                total = 0
                for commission in response.data:
                    total += float(commission["service_amount"])
                return total
            
        except Exception as e:

            print(f"Error retrieving commissions for shop {shopID}")

            raise e

    #TODO: NEEDS TO BE TESTED
    def get_shop_nail_techs(self, shopID: int) -> list:

        try:
            response = (
                supabase.table("nail_techs")
                .select("user_id")
                .eq("shop_id", shopID)
                .execute()
            )

            if response is None:
                raise ValueError("Unable to query nail_techs table")

            return response.data

        except Exception as e:

            print(f"Error retrieving nail techs for shop {shopID}")

            raise e
    #TODO: NEEDS TO BE TESTED
    def get_shop_services(self, shopID: int) -> list:

        try:
            response = (
                supabase.table("shop_services")
                .select("name, description, print, duration")
                .eq("shop_id", shopID)
                .execute()
            )

            if response is None:
                raise ValueError("Unable to query shop_services table")

            return response.data

        except Exception as e:

            print(f"Error retrieving shop services for shop {shopID}")

            raise e
    #TODO: NEEDS TO BE TESTED
    def get_shop_skills(self, shopID: int) -> list:

        try:
            response = (
                supabase.table("shop_skills")
                .select("skills(name)")
                .eq("shop_id", shopID)
                .execute()
            )

            if response is None:
                raise ValueError("Issue querying join from shop_skills and skills table")

            return response.data

        except Exception as e:

            print(f"Error retrieving shop skills for shop {shopID}")

            raise e

    
  

            

