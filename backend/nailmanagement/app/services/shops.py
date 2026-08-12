from nailmanagement.app.db.supabase_client import supabase
import re
import time
from nailmanagement.app.services.utils import hash_pin, verify_pin, valid_phone, valid_email, valid_weekdays
from datetime import datetime
class Shops:

    #EDITING SHOP INFO
    def register_shop(self, name: str, phone: str, pin: str, address: str, open_t: time, close_t: time, email: str, close_d: str, open_d: str, ownerID: int):
        """
        Registers shop by inserting shop information into the database table

        Args:
            name (str): Shop name
            phone (str): Shop contact phone number
            pin (str): Shop pin for authorization to insert information
            address (str): The physical address of the shop
            open_t (time): When the shop opens
            close_t (time): When the shop closes
            email (str): Shop contact email
            close_d (str): a string of abbreviated days separated by commas when the shop is closed
            open_d (str): a string of abbreviated days separated by commas when the shop is open
            owner_id (int): the owner's identification number
        
        Returns:
            dict: Newly registered shop record 
        
        Raises: 
            Exception: If database insert fails
        """
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

    def get_shops(self, uuid: str, ownerID: int) -> list:
        """
        Returns a list of shops

        Args:
            uuid (str): user identification
            ownerID (int): owner identification number

        Returns:
            list: of the shop_id and name

        Raises: 
            Exception: if invalid access or query fails 
        """
        try:
            userID = (
                supabase.table("users")
                .select("user_id")
                .eq("uuid", uuid)
                .execute().data
            )

            if not userID:
                raise ValueError("User not found")

            userID = userID[0]["user_id"]

            if userID != ownerID:
                raise ValueError("Invalid access")

            #TODO: EDIT TO ALLOW PHOTO RETRIEVAL
            response = (
                supabase.table("shops")
                .select("shop_id, name")
                .eq("owner_id", ownerID)
                .execute()
            )

            return response.data
        
        except Exception as e:
            print(f"Error retrieving shop info for owner_id {ownerID}")
            raise e
        
    def get_shop_info(self, uuid: str, shopID: int) -> dict:
        """
        Retrieves shop information

        Args: 
            uuid (str): user identification
            shopID (int): shop identification number

        Returns:
            dict: containing the shop_id, owner_id, name, address, email, phone, opne_t, close_t, open_d, close_d
        
        Raises: 
            Exception: if the shopID is invalid or query error
        """
        try:

            response = (
                supabase.table("shops")
                .select("*")
                .eq("shop_id", shopID)
                .execute().data[0]
            )

            if not response: 
                raise ValueError("Shop not found")

            return response

        except Exception as e:

            print(f"Error retrieving shop information for {shopID}")

            raise e

    #FETCHING SHOP INFO 
    #ONLY OWNER CAN VIEW
    def get_shop_commission_total(self, shopID: int, uuid: str) -> float:
        """
        Get the total commissions of techs associated with the shop

        Args:
            shopID (int): shop identification number
            uuid: user identification

        Returns:
            float: the total commission 
        
        Raises: 
            Exception: if invalid access or query error
        """
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
                total = 0
                for commission in response.data:
                    total += float(commission["service_amount"])
                return total
            
        except Exception as e:

            print(f"Error retrieving commissions for shop {shopID}")

            raise e

    #TODO: NEEDS TO BE TESTED
    def get_shop_techs(self, uuid: str, shopID: int) -> list:
        """
        Retrieves a list of all techs associated with a shop

        Args:
            uuid (str): user identification
            shopID (int): shop identification number
        
        Returns:
            list: of user identification numbers

        Raises:
            Exception: if query issues
        """
        #TODO: authorization check
        try:
            response = (
                supabase.table("techs")
                .select("user_id")
                .eq("shop_id", shopID)
                .execute()
            )

            return response.data

        except Exception as e:

            print(f"Error retrieving nail techs for shop {shopID}")

            raise e
    #TODO: NEEDS TO BE TESTED
    def get_shop_services(self, uuid: str, shopID: int) -> list:
        """
        Retrieves a list of all shop services

        Args:
            uuid(str): user identification
            shopID(int): shop identification number

        Returns:
            list: of shop service name, description, price, and duration
        
        Raises:
            Exception: if issue querying
        """
        #TODO: authorization check
        try:
            response = (
                supabase.table("shop_services")
                .select("name, description, price, duration")
                .eq("shop_id", shopID)
                .execute()
            )

            return response.data

        except Exception as e:

            print(f"Error retrieving shop services for shop {shopID}")

            raise e
    #TODO: NEEDS TO BE TESTED
    def get_shop_skills(self, uuid: str, shopID: int) -> list:
        """
        Retrieves a list of all shop skills
        
        Args:
            uuid(str): user identification
            shopID(int): shop identification number

        Returns:
            list: a list of skill names
        
        Raises:
            Exception: If querying fails
        """
        #TODO: authorization check
        try:
            response = (
                supabase.table("shop_skills")
                .select("skills(name)")
                .eq("shop_id", shopID)
                .execute()
            )

            return response.data

        except Exception as e:

            print(f"Error retrieving shop skills for shop {shopID}")

            raise e

    def get_shop_appointments(self, uuid: str, day: datetime, shopID: int) -> list:
        """
        Retrieves all appointments associated with a shop on a given day

        Args:
            uuid (str): user identification
            day (datetime): the desired day 
            shopID (int): shop identification number
        
        Returns:
            list: a list of appointments' appointment_id, client_name, time, status
        
        Raises:
            Exception: if querying fails
        """
        #TODO: authorization check
        supabase_datetime = day.isoformat()
        try:
            response = (
                supabase.table("appointments")
                .select("appointment_id, client_name, time, status")
                .eq("shop_id", shopID)
                .eq("day", supabase_datetime)
                .execute()
            )

            return response.data

        except Exception as e:

            print(f"Error retrieving appointment information for shop {shopID}")

            raise e

    
  

            

