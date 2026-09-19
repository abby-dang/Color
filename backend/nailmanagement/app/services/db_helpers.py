from nailmanagement.app.db.supabase_client import supabase

def get_user_id(uuid: str) -> int:
    """
    Retrieves the user ID for a given UUID.

    Args:
        uuid (str): The user's uuid

    Returns:
        int: The user ID if the user exists, -1 otherwise
    """
    try:
        data = (
            supabase.table("users")
            .select("user_id")
            .eq("uuid", uuid)
            .execute().data[0]
        )

        if not data["user_id"]:
            return -1  # User not found

        return data["user_id"]
    
    except Exception as e:
        print(f"Error occurred while fetching user ID for UUID {uuid}: {e}")
        return -1

def get_owner_id(shop_id: int) -> int:
    """
    Retrieves the owner ID for a given shop ID.

    Args:
        shop_id (int): The shop's ID
    Returns:
        int: The user ID if the user exists, -1 otherwise    
    """
    try:
        data = (
            supabase.table("shops")
            .select("owner_id")
            .eq("shop_id", shop_id)
            .execute().data[0]
        )

        if not data["owner_id"]:
            return -1  # shop not found

        return data["owner_id"]
    
    except Exception as e:
        print(f"Error occurred while fetching owner ID for shop ID {shop_id}: {e}")
        return -1
#TODO: FIX SO IT UUID INSTEAD OF USER_ID
def is_tech(user_id: int, shop_id: int) -> bool:
    """
    Checks if a user is a tech for a given shop.

    Args:
        user_id (int): The user's ID
        shop_id (int): The shop's ID

    Returns:
        bool: True if the user is a tech for the shop, False otherwise
    """
    try:
        
        data = (
            supabase.table("techs")
            .select("user_id")
            .eq("user_id", user_id)
            .eq("shop_id", shop_id)
            .execute().data[0]
        )

        if not data["user_id"]:
            return False  # User is not a tech for the shop

        return True
    
    except Exception as e:
        print(f"Error occurred while checking if user {user_id} is a tech for shop {shop_id}: {e}")
        return False

def is_user(uuid: str) -> bool:
    user_id = get_user_id(uuid)
    if user_id == -1:
        return False
    return True

def is_owner(uuid: str, shop_id: int) -> bool:
    user_id = get_user_id(uuid)
    owner_id = get_owner_id(shop_id)
    if user_id != owner_id:
        return False
    return True

def is_receptionist(uuid: str, shop_id: int) -> bool:
    user_id = get_user_id(uuid)

    try:
        response = (
            supabase.table("receptionists")
            .select("receptionist_id")
            .eq("user_id", user_id)
            .eq("shop_id", shop_id)
            .execute()
        )

        if not response.data:
            return False
        return True
    except Exception as e:
        print(f"Error retrieving receptionist: {e}")
        raise e

def is_authorized(uuid: str, shop_id: int) -> bool:
    if is_user(uuid) and (is_owner(uuid, shop_id) or is_receptionist(uuid, shop_id)):
        return True
    return False

def is_client(client_id: int, shop_id: int) -> bool:
    try:
        response = (
            supabase.table("clients")
            .select("client_id")
            .eq("client_id", client_id)
            .eq("shop_id", shop_id)
            .execute().data
        )

        if not response:
            return False
        return True

    except Exception as e:
        print(f"Error retrieving client: {e}")
        raise e