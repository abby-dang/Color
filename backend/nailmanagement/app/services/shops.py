from nailmanagement.app.db.supabase_client import supabase
import re
class Shops:

    def register_shop(self, name: str, phone: str, pin: str, address: str):
        #CHECK NAME
        if len(name) > 100:
            raise ValueError("Name of shop is too long")
        
        #CHECK PHONE NUMBER
        validPhoneNum = re.match(r"^\d{10}$", phone)

        if not validPhoneNum:
            raise ValueError("Phone number incorrect format")
        
        
        try:
            response = (
                supabase.table("shops")
                .insert({"name": name, "phone": phone, "pin": pin, "address": address})
                .execute()
                )
            
            return response
        except Exception as e:\
        
            print("Error registering shop")

            raise e
            