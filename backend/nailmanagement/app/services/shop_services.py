from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.db_helpers import get_user_id, get_owner_id, is_tech

class Shop_Services:

    def add_service(self, uuid: str,shop_id: int, name: str, description: str, price: int, duration: int, skill_ids: list = []):
            """
            Adds a new service to the shop's offerings.
            
            Args:
                uuid (str): The user's uuid
                shop_id (int): The ID of the shop to add the service to
                name (str): The name of the service
                description (str): The description of the service
                price (float): The price of the service
                duration (int): The duration of the service in minutes
                skill_ids (list): A list of skill IDs associated with the service

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
                # If skill_ids are provided, associate them with the newly added service
                if skill_ids:
                    service_id = response.data[0]["service_id"]
                    self.add_service_skills(service_id, skill_ids)
                    
                return response.data[0]
            
            except Exception as e:
                print(f"Error adding service to shop {shop_id}: {e}")
                raise e
            
    def add_service_skills(self, service_id: int, skill_ids: list):
        """
        Associates a list of skill IDs with a specific service.
        
        Args:
            service_id (int): The ID of the service to associate skills with
            skill_ids (list): A list of skill IDs to associate with the service
        Returns:
            the response from the supabase insert operation
        Raises:
            Exception: if issue querying
        """
        try:
            skill_associations = [{"service_id": service_id, "skill_id": skill_id} for skill_id in skill_ids]
            response = (
                supabase.table("shop_service_skills")
                .insert(skill_associations)
                .execute()
            )
            print(f"Response: {response.data}")
            if response.data is None:
                raise ValueError("Failed to associate skills with the service.")
            return response.data
        except Exception as e:
            print(f"Error associating skills with service {service_id}: {e}")
            raise e

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

    def update_service(self, uuid: str, shop_id: int, service_id: int, name: str = None, description: str = None, price: float = None, duration: int = None, skill_ids: list = None):
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
            skill_ids (list, optional): A list of skill IDs associated with the service
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

            if skill_ids is not None:
                skills_update = self.update_service_skills(service_id, skill_ids)

            if response.data and skills_update:
                return {"Message": "Service updated successfully."}
            else:
                return {"Message": "Service not found or no changes made."}
        
        except Exception as e:
            print(f"Error updating service in shop {shop_id}: {e}")
            raise e
    def update_service_skills(self, service_id: int, skill_ids: list):
        """
        Updates the skills associated with a specific service.
        
        Args:
            service_id (int): The ID of the service to update skills for
            skill_ids (list): A list of new skill IDs to associate with the service
        
    
        """
        try:
            # Remove existing skill associations
            supabase.table("shop_service_skills").delete().eq("service_id", service_id).execute()
            
            # Add new skill associations
            skill_associations = [{"service_id": service_id, "skill_id": skill_id} for skill_id in skill_ids]
            response = (
                supabase.table("shop_service_skills")
                .insert(skill_associations)
                .execute()
            )

            return response.data
        
        except Exception as e:
            print(f"Error updating skills for service {service_id}: {e}")
            raise e 