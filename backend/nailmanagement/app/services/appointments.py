from nailmanagement.app.db.supabase_client import supabase
from datetime import datetime, timedelta, timezone
from nailmanagement.app.services.clients import Clients
from nailmanagement.app.services.db_helpers import is_authorized
from nailmanagement.app.services.utils import convert_date_time, convert_date
from nailmanagement.app.services.db_helpers import is_client


class Appointments:
    """
    Service layer for creating, retrieving and updating appointments.

    Dates and times are interpreted in the server's local timezone and
    stored in UTC.
    """

    def __init__(self):
        self.supabase = supabase
        self.appointment_fields = "appointment_id, datetime, status, clients(first_name, last_name, phone)"

    def create_appointment(self, client_id: int, shop_id: int, notes: str, services: list, status: str = "pending", date: str = None, time: str = None) -> dict:
        """
        Creates an appointment and links it to its services.

        If linking the services fails, the appointment is deleted.

        Args:
            client_id (int): The client being scheduled
            shop_id (int): The shop where the appointment is scheduled
            notes (str): Notes for the appointment
            services (list): Dicts with "service_id" and "tech_id" keys,
                e.g. [{"service_id": 1, "tech_id": 4}]
            status (str): "pending", "confirmed", "completed", "cancelled" or
                "in_progress". Defaults to "pending"
            date (str): e.g. "2026-09-20" or "09/20/2026". Defaults to today
            time (str): HH:MM or HH:MM:SS. Defaults to now

        Returns:
            list: The created appointment record

        Raises:
            Exception: if the client is not in the shop, the status, date or
                time is invalid, a service is missing a key, or an insert fails
        """
        try:
            if not is_client(client_id=client_id, shop_id=shop_id):
                raise ValueError("User is not a client at this shop")
            if status not in ["pending", "confirmed", "completed", "cancelled", "in_progress"]:
                raise ValueError("Invalid status value. Must be one of: pending, confirmed, completed, cancelled, in_progress")
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")  # Default to today's date if not provided
            if not time:
                time = datetime.now().strftime("%H:%M")  # Default to current time if not provided

            # Parsed as server-local time, then converted to UTC for storage
            appointment_datetime = convert_date_time(date, time)
            appointment_datetime_utc = appointment_datetime.astimezone(timezone.utc)

            appointment_data = {
                "client_id": client_id,
                "shop_id": shop_id,
                "notes": notes,
                "datetime": appointment_datetime_utc.isoformat(),
                "status": status,
            }

            appointment_response = self.supabase.table("appointments").insert(appointment_data).execute()
            appointment = appointment_response.data[0]

            # One appointment_services row per (service, tech) pair
            services_to_insert = [
                {
                    "appointment_id": appointment["appointment_id"],
                    "service_id": service["service_id"],
                    "tech_id": service["tech_id"],
                }
                for service in services
            ]

            try:
                self.supabase.table("appointment_services").insert(services_to_insert).execute()
            except Exception:
                # Undo the appointment so we don't leave one with no services
                self.supabase.table("appointments").delete().eq("appointment_id", appointment["appointment_id"]).execute()
                raise

            return appointment_response.data
        except Exception as e:
            raise Exception(f"Error creating appointment: {str(e)}")

    def get_appointments_by_client(self, uuid: str, shop_id: int, client_id: int = None, first_name: str = None, last_name: str = None, phone: str = None, email: str = None) -> list:
        """
        Retrieves a client's appointments in a shop.

        The client is found by client_id, or by searching on name, phone or
        email. Name searches are partial, so appointments for every matching
        client are returned.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            client_id (int): Takes priority over the other fields
            first_name (str): Partial match
            last_name (str): Partial match
            phone (str): Exact match
            email (str): Exact match

        Returns:
            list: Appointments ordered by datetime, each with the client's
                name and phone. Empty if no client matches

        Raises:
            ValueError: if the user is not authorized or no identifier is given
            Exception: if the query fails
        """
        client = Clients()
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User not authorized")

            query = self.supabase.table("appointments").select(self.appointment_fields).eq("shop_id", shop_id)

            if client_id:
                query = query.eq("client_id", client_id)
            else:
                # With no filters get_client would return every client in the shop
                if not any([first_name, last_name, phone, email]):
                    raise ValueError("Provide a client_id or at least one of first_name, last_name, phone, email")

                matches = client.get_client(uuid, shop_id, first_name=first_name, last_name=last_name, email=email, phone=phone)
                if not matches:
                    return []
                query = query.in_("client_id", [match["client_id"] for match in matches])

            response = query.order("datetime").execute()

            return response.data
        except Exception as e:
            print(f"Error searching for appointment by client: {e}")
            raise e

    def get_appointments_by_day(self, uuid: str, shop_id: int, day: str) -> list:
        """
        Retrieves a shop's appointments for a day (local midnight to midnight).

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            day (str): e.g. "2026-09-20" or "09/20/2026"

        Returns:
            list: Appointments ordered by datetime, each with the client's
                name and phone

        Raises:
            ValueError: if the user is not authorized or the day is invalid
            Exception: if the query fails
        """
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User not authorized")

            day_start = datetime.strptime(convert_date(day), "%Y-%m-%d")
            day_end = day_start + timedelta(days=1)

            response = (
                self.supabase.table("appointments")
                .select(self.appointment_fields)
                .eq("shop_id", shop_id)
                .gte("datetime", day_start.astimezone(timezone.utc).isoformat())
                .lt("datetime", day_end.astimezone(timezone.utc).isoformat())
                .order("datetime")
                .execute()
            )

            return response.data

        except Exception as e:
            print(f"Error retrieving appointment information for shop {shop_id}: {e}")
            raise e

    def get_appointments_by_tech(self, uuid: str, shop_id: int, tech_id: int):
        """
        Retrieves the appointments a tech is assigned to in a shop.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            tech_id (int): The tech's ID

        Returns:
            list: One entry per assigned service, each with tech_id and a
                nested "appointments" record

        Raises:
            ValueError: if the user is not authorized
            Exception: if the query fails
        """
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User is not authorized")


            response = (
                self.supabase.table("appointment_services")
                .select(f"tech_id, appointments({self.appointment_fields})")
                .eq("tech_id", tech_id)
                .eq("appointments.shop_id", shop_id)
                .execute()
            )

            return response.data

        except Exception as e:
            print(f"Error retrieving appointment infomration based on the tech_id given")
            raise e

    def get_appointment(self, uuid: str, shop_id: int, appointment_id: int):
        """
        Retrieves a single appointment with its services and assigned techs.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            appointment_id (int): The appointment's ID

        Returns:
            list: The appointment record with the client's name and phone, and
                each service's name and tech name

        Raises:
            ValueError: if the user is not authorized
            Exception: if the query fails
        """
        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("User not authorized")

            response = (
                self.supabase.table("appointments")
                .select(f"{self.appointment_fields}, appointment_services(shop_services(name), techs(users(first_name, last_name)))")
                .eq("appointment_id", appointment_id)
                .execute()
            )

            return response.data

        except Exception as e:
            print(f"Error retrieving appointment information")
            raise e
            

    def update_appointment(self, uuid: str, shop_id: int, appointment_id: int,  notes: str = None, services: list = None, status: str = None, date: str = None, time: str = None):
        """
        Updates an appointment. Only the fields provided are changed.

        Args:
            uuid (str): The user making the request
            shop_id (int): The shop's ID
            appointment_id (int): The appointment to update
            notes (str): New notes
            services (list): Dicts with "service_id" and "tech_id" keys.
                Replaces the existing services
            status (str): New status
            date (str): New date. Must be given together with time
            time (str): New time. Must be given together with date

        Returns:
            list: The updated appointment record

        Raises:
            ValueError: if the user is not authorized, or only one of date
                and time is given
            Exception: if an update fails
        """
        def update_appointment_services():
            """
            Replaces the appointment's services with the new list.

            Restores the old services if the insert fails.
            """
            try:
                services_to_insert = [
                    {
                        "appointment_id": appointment_id,
                        "service_id": service["service_id"],
                        "tech_id": service["tech_id"]
                    }
                    for service in services
                ]

                old_rows = (
                    self.supabase.table("appointment_services")
                    .select("appointment_id, service_id, tech_id")
                    .eq("appointment_id", appointment_id)
                    .execute()
                ).data

                self.supabase.table("appointment_services").delete().eq("appointment_id", appointment_id).execute()

                try:
                    return self.supabase.table("appointment_services").insert(services_to_insert).execute()
                except Exception:
                    # Put the old services back so the appointment isn't left with none
                    if old_rows:
                        self.supabase.table("appointment_services").insert(old_rows).execute()
                    raise
            except Exception as e:
                print(f"Error updating services: {e}")
                raise e

        try:
            if not is_authorized(uuid, shop_id):
                raise ValueError("Unauthorized Access")

            update_data = {}
            if notes:
                update_data["notes"] = notes
            if status:
                update_data["status"] = status
            if date and time:
                update_data["datetime"] = convert_date_time(date, time)
            elif date or time:
                raise ValueError("Must have both date and time")

            response = (
                self.supabase.table("appointments")
                .update(update_data)
                .eq("appointment_id", appointment_id)
                .execute()
            )

            if services:
                update_appointment_services()
                
            return response.data

        except Exception as e:
            print(f"Error updating appointment: {e}")
            raise e
