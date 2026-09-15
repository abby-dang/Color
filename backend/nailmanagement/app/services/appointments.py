from urllib import response

from nailmanagement.app.db.supabase_client import supabase
from datetime import datetime, timezone
from typing import List
class Appointments:
    def __init__(self):
        self.supabase = supabase

    def create_appointment(self, client_name: str, shop_id: int, notes: str, service_ids: list,status: str = "pending", date: str = None, time: str = None, tech_ids: list = None  ) -> dict:
        """
        Creates a new appointment in the database.

        Args:
            client_name (str): The name of the client
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
                "client_name": client_name,
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

    