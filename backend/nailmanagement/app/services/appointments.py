from nailmanagement.app.db.supabase_client import supabase
from datetime import datetime, timedelta, timezone
from nailmanagement.app.services.clients import Clients
from nailmanagement.app.services.db_helpers import is_authorized
from nailmanagement.app.services.utils import convert_date_time, convert_date
from nailmanagement.app.services.db_helpers import is_client


class Appointments:
    """
    Service layer for creating and retrieving appointments.

    Appointments are stored in UTC. Incoming dates/times are interpreted in the
    server's local timezone and converted to UTC before being saved, and the
    day-based lookups use the same interpretation so both stay consistent.
    """

    def __init__(self):
        self.supabase = supabase
        self.appointment_fields = "appointment_id, datetime, status, clients(first_name, last_name, phone)"

    def create_appointment(self, client_id: int, shop_id: int, notes: str, service_ids: list, status: str = "pending", date: str = None, time: str = None, tech_ids: list = None) -> dict:
        """
        Creates a new appointment and links it to its services.

        The appointment row is inserted first, then one appointment_services row
        is inserted per service. If the services insert fails, the appointment
        row is deleted so no service-less appointment is left behind.

        Args:
            client_id (int): The ID of the client who is getting scheduled
            shop_id (int): The ID of the shop where the appointment is scheduled
            notes (str): Additional notes for the appointment
            service_ids (list): IDs of the services booked. Must contain at least one
            status (str): One of "pending", "confirmed", "completed", "cancelled",
                "in_progress". Defaults to "pending"
            date (str): The appointment date (e.g. "2026-09-20" or "09/20/2026").
                Defaults to today
            time (str): The appointment time in HH:MM or HH:MM:SS format.
                Defaults to the current time
            tech_ids (list): IDs of the technicians, matched to service_ids by position
                (tech_ids[i] performs service_ids[i]). If omitted, services are saved
                without a technician

        Returns:
            dict: The newly created appointment record

        Raises:
            Exception: if the status is invalid, service_ids is empty, tech_ids and
                service_ids differ in length, the date/time is invalid, or a
                database insert fails
        """
        try:
            if not is_client(client_id=client_id, shop_id=shop_id):
                raise ValueError("User is not a client at this shop")
            if status not in ["pending", "confirmed", "completed", "cancelled", "in_progress"]:
                raise ValueError("Invalid status value. Must be one of: pending, confirmed, completed, cancelled, in_progress")

            if not service_ids:
                raise ValueError("At least one service is required")

            if tech_ids is None:
                tech_ids = [None] * len(service_ids)
            elif len(tech_ids) != len(service_ids):
                raise ValueError("tech_ids must have the same length as service_ids")

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
                    "service_id": service_id,
                    "tech_id": tech_id,
                }
                for service_id, tech_id in zip(service_ids, tech_ids)
            ]

            try:
                self.supabase.table("appointment_services").insert(services_to_insert).execute()
            except Exception:
                # Undo the appointment so we don't leave one with no services
                self.supabase.table("appointments").delete().eq("appointment_id", appointment["appointment_id"]).execute()
                raise

            return appointment
        except Exception as e:
            raise Exception(f"Error creating appointment: {str(e)}")

    def get_appointments_by_client(self, uuid: str, shop_id: int, client_id: int = None, first_name: str = None, last_name: str = None, phone: str = None, email: str = None) -> list:
        """
        Retrieves all appointments in a shop for a client.

        The client is identified either directly by client_id, or by searching on
        any of first_name, last_name, phone and email. Name searches are partial,
        case-insensitive matches, so a search may match several clients; in that
        case the appointments of every matching client are returned (each row
        includes the client's name and phone so they can be told apart).

        Args:
            uuid (str): The identifier of the user making the request
            shop_id (int): The ID of the shop
            client_id (int): The client's ID. Takes priority over the other fields
            first_name (str): The client's first name (partial match)
            last_name (str): The client's last name (partial match)
            phone (str): The client's phone number (exact match)
            email (str): The client's email (exact match)

        Returns:
            list: Appointments ordered by datetime, each with appointment_id,
                datetime (UTC), status and the client's first_name, last_name and
                phone. Empty if no client matches or the client has no appointments

        Raises:
            ValueError: if the user is not authorized for the shop, or no client
                identifier was provided
            Exception: if querying fails
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

                matches = client.get_client(shop_id, first_name=first_name, last_name=last_name, email=email, phone=phone)
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
        Retrieves all appointments in a shop on a given day.

        The day runs from local midnight to the next local midnight (the same
        timezone used by create_appointment), converted to UTC for the query.

        Args:
            uuid (str): The identifier of the user making the request
            shop_id (int): The ID of the shop
            day (str): The desired day (e.g. "2026-09-20" or "09/20/2026")

        Returns:
            list: Appointments ordered by datetime, each with appointment_id,
                datetime (UTC), status and the client's first_name, last_name and
                phone

        Raises:
            ValueError: if the user is not authorized for the shop or the day
                format is invalid
            Exception: if querying fails
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

    #def get_appointments_by_tech(self, uuid: str, shop_id: int, tech_id: int):
