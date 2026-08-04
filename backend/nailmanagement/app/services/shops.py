from nailmanagement.app.db.supabase_client import supabase
import re
import time
from nailmanagement.app.services.utils import hash_pin, verify_pin, valid_phone, valid_email
class Shops:

    def register_shop(self, name: str, phone: str, pin: str, address: str, open_t: time, close_t: time, email: str, close_d: int, open_d: int):
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

        hash_pin = hash_pin(pin)

        try:
            response = (
                supabase.table("shops")
                .insert({"name": name, "phone": phone, "pin": hash_pin, "address": address, "open_t": open_t, "close_t": close_t, "email": email, "close_d": close_d, "open_d": open_d})
                .execute()
                )
            
            return response
        except Exception as e:\
        
            print("Error registering shop")

            raise e
            