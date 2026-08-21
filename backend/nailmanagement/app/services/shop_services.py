from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.db_helpers import get_user_id, get_owner_id, is_tech

class Shop_Services:

    def add_service(self, uuid: str,shop_id: int, name: str, description: str, price: int, duration: int):
            """
            Adds a new service to the shop's offerings.
            
            Args:
                uuid (str): The user's uuid
                shop_id (int): The ID of the shop to add the service to
                name (str): The name of the service
                description (str): The description of the service
                price (float): The price of the service
                duration (int): The duration of the service in minutes
            
            Returns:
                dict: The newly added service record
            """
            try:
                user_id = get_user_id(uuid)
                if user_id == -1:
                    raise ValueError("User not found")

                owner_id = get_owner_id(shop_id)
                if owner_id != user_id:
                    raise ValueError("Unauthorized access: Only the shop owner can add services.")
                
                response = (
                    supabase.table("shop_services")
                    .insert({
                        "shop_id": shop_id,
                        "name": name,
                        "description": description,
                        "price": price,
                        "duration": duration
                    })
                    .execute()
                )

                return response.data[0]
            
            except Exception as e:
                print(f"Error adding service to shop {shop_id}: {e}")
                raise e
        #VIEWABLE TO PUBLIC
    def get_shop_services(self, shopID: int) -> list:
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
    def remove_service(self, uuid: str, shop_id: int, service_id: int):
        """
        Removes a service from the shop's offerings.
        
        Args:
            uuid (str): The user's uuid
            shop_id (int): The ID of the shop to remove the service from
            service_id (int): The ID of the service to be removed
        
        Returns:
            dict: A message indicating the result of the operation
        """
        try:
            user_id = get_user_id(uuid)
            if user_id == -1:
                raise ValueError("User not found")

            owner_id = get_owner_id(shop_id)
            if owner_id != user_id:
                raise ValueError("Unauthorized access: Only the shop owner can remove services.")
            
            response = (
                supabase.table("shop_services")
                .delete()
                .eq("shop_id", shop_id)
                .eq("service_id", service_id)
                .execute()
            )

            if response.data:
                return {"Message": "Service removed successfully."}
            else:
                return {"Message": "Service not found or already removed."}
        
        except Exception as e:
            print(f"Error removing service from shop {shop_id}: {e}")
            raise e

    def update_service(self, uuid: str, shop_id: int, service_id: int, name: str = None, description: str = None, price: float = None, duration: int = None):
        """
        Updates a service in the shop's offerings.
        
        Args:
            uuid (str): The user's uuid
            shop_id (int): The ID of the shop to update the service in
            service_id (int): The ID of the service to be updated
            name (str, optional): The new name of the service
            description (str, optional): The new description of the service
            price (float, optional): The new price of the service
            duration (int, optional): The new duration of the service in minutes
        """
        try:
            user_id = get_user_id(uuid)
            if user_id == -1:
                raise ValueError("User not found")

            owner_id = get_owner_id(shop_id)
            if owner_id != user_id:
                raise ValueError("Unauthorized access: Only the shop owner can update services.")
            
            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if price is not None:
                update_data["price"] = price
            if duration is not None:
                update_data["duration"] = duration
            
            if not update_data:
                raise ValueError("No fields to update provided.")

            response = (
                supabase.table("shop_services")
                .update(update_data)
                .eq("shop_id", shop_id)
                .eq("service_id", service_id)
                .execute()
            )

            if response.data:
                return {"Message": "Service updated successfully."}
            else:
                return {"Message": "Service not found or no changes made."}
        
        except Exception as e:
            print(f"Error updating service in shop {shop_id}: {e}")
            raise e