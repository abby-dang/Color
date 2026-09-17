from urllib import response

from nailmanagement.app.db.supabase_client import supabase
from datetime import datetime, timezone
from typing import List
from nailmanagement.app.services.clients import Clients
from nailmanagement.app.services.db_helpers import is_authorized
from nailmanagement.app.services.utils import verify_date_format
class Appointments:
    def __init__(self):
        self.supabase = supabase

    def create_appointment(self, client_id: int, shop_id: int, notes: str, service_ids: list,status: str = "pending", date: str = None, time: str = None, tech_ids: list = None  ) -> dict:
        """
        Creates a new appointment in the database.

        Args:
            client_id (id): The ID of the client who is getting scheduled
            shop_id (int): The ID of the shop where the appointment is scheduled
            notes (str): Additional notes for the appointment
            date (str): The date of the appointment in YYYY-MM-DD format
            time (str): The time of the appointment in HH:MM format
            service_ids (list): A list of IDs for the services associated with the appointment
            tech_ids (list): A list of IDs for the technicians assigned to the appointment

        Returns:
            dict: The newly created appointment record
        """
        try:
            if status not in ["pending", "confirmed", "completed", "cancelled", "in_progress"]:
                raise ValueError("Invalid status value. Must be one of: pending, confirmed, completed, cancelled, in_progress")

            if not date:
                date = datetime.now().strftime("%Y-%m-%d")  # Default to today's date if not provided
            if not time:
                time = datetime.now().strftime("%H:%M")  # Default to current time if not provided
            #convert date and time to utc
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            appointment_datetime_utc = appointment_datetime.astimezone(timezone.utc)

            # Create a new appointment record in the database
            appointment_data = {
                "client_id": client_id,
                "shop_id": shop_id,
                "notes": notes,
                "datetime": appointment_datetime_utc.isoformat(),
                "status": status,
            }
            
            appointment_response = self.supabase.table("appointments").insert(appointment_data).execute()

            # Create appointment services records for each service_id in the list
            appointment_id = appointment_response.data[0]["appointment_id"]
            services_to_insert = [
                {
                    "appointment_id": appointment_response.data[0]["appointment_id"],
                    "service_id": service_ids[i],
                    "tech_id": tech_ids[i]
                }
                for i in range(len(service_ids))
            ]

            appointment_service_response = self.supabase.table("appointment_services").insert(services_to_insert).execute()

            return appointment_response.data[0]  # Return the newly created appointment record
        except Exception as e:
            raise Exception(f"Error creating appointment: {str(e)}")

    def get_appointments_by_client(self, uuid: str, shop_id: int, client_id: int = None, first_name: str = None, last_name: str = None, phone: str = None, email: str = None):
        client = Clients()
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User not authorized")
            
            query = self.supabase.table("appointments").select("*").eq("shop_id", shop_id)

            if client_id:
                query = query.eq("client_id", client_id)
            else:
                client_info = client.get_client(shop_id, first_name= first_name, last_name = last_name, email = email, phone = phone)
                if not client_info:
                    return []
                query = query.eq("client_id", client_info[0]["client_id"])

            response = query.execute()

            return response.data
        except Exception as e:
            print(f"Error searching for appointment by client: {e}")
            raise e

    def get_appointments_by_day(self, uuid: str, shop_id: int, day: str):
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
        if not is_authorized(uuid, shop_id):
            raise ValueError("User not authorized")
        
        if not verify_date_format(day):
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

        date_object = datetime.strptime(day, "%Y-%m-%d").date()

        try:
            
            response = (
                supabase.table("appointments")
                .select("appointment_id, client_name, time, status")
                .eq("shop_id", shop_id)
                .eq("day", date_object)
                .execute()
            )

            return response.data

        except Exception as e:

            print(f"Error retrieving appointment information for shop {shop_id}")

            raise e

    #def get_appointments_by_tech(self, uuid: str, shop_id: int, tech_id: int):

