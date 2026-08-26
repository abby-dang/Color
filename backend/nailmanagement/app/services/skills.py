from nailmanagement.app.db.supabase_client import supabase
from nailmanagement.app.services.db_helpers import get_user_id

class Skills:

    def add_skill(self, uuid: str, name: str):
        """
        Adds a new skill to the database.
        
        Args:
            uuid (str): The user's uuid
            name (str): The name of the skill to add
            
        Returns:
            dict: The newly added skill record

        Raises:
            Exception: if issue querying
        """
        try:
            user_id = get_user_id(uuid)
            if user_id == -1:
                raise ValueError("User not found")

            response = (
                supabase.table("skills")
                .insert({
                    "name": name
                })
                .execute()
            )

            return response.data[0]

        except Exception as e:
            print(f"Error adding skill: {e}")
            raise e

    def get_skills(self) -> list:
        """
        Retrieves a list of all skills from the database.

        Returns:
            list: A list of skill records
        
        Raises:
            Exception: if issue querying
        """

        try:
            response = (
                supabase.table("skills")
                .select("*")
                .execute()
            )

            return response.data

        except Exception as e:
            print(f"Error retrieving skills: {e}")
            raise e

    def get_skill_by_name(self, name: str) -> dict:
        """
        Retrieves a skill record by its name.

        Args:
            name (str): The name of the skill to retrieve

        Returns:
            dict: The skill record if found, otherwise None
        
        Raises:
            Exception: if issue querying
        """
        try:
            response = (
                supabase.table("skills")
                .select("*")
                .eq("name", name)
                .execute()
            )

            if response.data:
                return response.data[0]
            else:
                return None

        except Exception as e:
            print(f"Error retrieving skill by name '{name}': {e}")
            raise e

    