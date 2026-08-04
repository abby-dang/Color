from nailmanagement.app.db.supabase_client import supabase
import re
from nailmanagement.app.services.utils import valid_phone, valid_email, valid_password
class UserAuthentication:

    def sign_up(self, email: str, password: str, firstName: str, lastName: str, phone: str) -> dict:
        """
        Registers new user with Supabase Auth and inserts their information into users table

        Args:
            email (str): User's email
            password (str): User's password
            firstName (str): User's first name
            lastName (str): User's last name
            phone (str): User's phone
        
        Returns:
            dict: Newly created user record or None if validation fails
        
        Raises:
            Exception: If database insert fails
        """
        #PASSWORD CHECK
        if not valid_password(password):
            raise ValueError("Password does not meet requirements")
        
        #PHONE CHECK
        if not valid_phone(phone):
            raise  ValueError("Phone number is not in the correct format")

        if not valid_email(email):
            raise ValueError("Email is not in the correct format")
        
        #REGISTERS AUTHENTICATION TO SUPABASE
        auth = supabase.auth.sign_up(
            {
                "email": email, #format: email@example.com
                "password": password
            }
        )

        #ADD ACCOUNT TO TABLE
        if auth.user is not None: 

            try: 
                response = (
                    supabase.table("users")
                    .insert({"uuid": auth.user.id, "email": email, "first_name": firstName, "last_name": lastName, "phone": phone, "is_active": True})
                    .execute()
                )
                return response
            
            except Exception as e:
                print("Error completing account registration")
                raise e
        else:
            print("Error registering account")

        return auth


    def login(self, email: str, password: str):
        """
        Signs in new user with Supabase Auth.

        Args:
            email (str): The user's email address
            password (str): The user's password

        """
        try:

            response = supabase.auth.sign_in_with_password(
                {
                    "email": email,
                    "password": password
                }
            )

            return response
        
        except Exception as e:

            raise e


    def logout(self):
        """
        Sign out authenticated user

        Returns:
            dict: Success message
        """
    
        supabase.auth.sign_out()
        return {"message":"Successfully logged out"}

    def reset_password(self, email: str):
        """
            Prompts Supabase to send an reset email to user with URL to reset password page
        """
        supabase.auth.reset_password_for_email(
            email,
            {
                "redirect_to":"" #TODO: ADD REDIRECT URL
            }
        )


    def update_user(self, new_password: str):
        """
        Updates user's password 

        Returns:
            UserResponse: Supabase user data object
        """
        if not valid_password(new_password):
            raise ValueError("Password does not meet requirements")
        
        try:

            response = supabase.auth.update_user(
                {"password": new_password}
            )

            return response
        
        except Exception as e:

            print("Updating user unsuccessful")

            raise e
        
    