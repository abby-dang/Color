import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from nailmanagement.app.services.shop_services import Shop_Services
from nailmanagement.app.db.supabase_client import supabase

shop_services = Shop_Services()

@csrf_exempt
def add_service(request, shop_id: int):
    """
    Adds a new service to the shop's offerings.

    Args:
        shop_id (int): The ID of the shop to add the service to
        name (str): The name of the service
        description (str): The description of the service
        price (float): The price of the service
        duration (int): The duration of the service in minutes

    Returns:
        dict: The newly added service record
    """

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Only POST is allowed."}, status=405)

    uuid = request.supabase_user.user.id  # gets the user's uuid
    try:
        body = json.loads(request.body)
        name = body.get("name")
        description = body.get("description")
        price = body.get("price")
        duration = body.get("duration")

        response = shop_services.add_service(uuid, shop_id, name, description, price, duration)
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

def get_shop_services(request, shop_id: int):
    """
    Retrieves a list of all services offered by the specified shop.

    Args:
        shop_id (int): The ID of the shop to retrieve services for

    Returns:
        list: A list of service records for the specified shop
    """

    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method. Only GET is allowed."}, status=405)

    try:
        response = shop_services.get_shop_services(shop_id)
        return JsonResponse(response, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def remove_shop_service(request, shop_id: int, service_id: int):
    """
    Removes a service from the shop's offerings.

    Args:
        shop_id (int): The ID of the shop to remove the service from
        service_id (int): The ID of the service to be removed

    Returns:
        dict: A message indicating the success or failure of the operation
    """

    if request.method != "DELETE":
        return JsonResponse({"error": "Invalid request method. Only DELETE is allowed."}, status=405)

    uuid = request.supabase_user.user.id  # gets the user's uuid
    try:
        response = shop_services.remove_service(uuid, shop_id, service_id)
        return JsonResponse({"message": "Service removed successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def update_shop_service(request, shop_id: int, service_id: int):
    """
    Updates the details of a specific service offered by the shop.

    Args:
        shop_id (int): The ID of the shop to update the service for
        service_id (int): The ID of the service to be updated

    Returns:
        dict: The updated service record
    """

    if request.method != "PUT":
        return JsonResponse({"error": "Invalid request method. Only PUT is allowed."}, status=405)

    uuid = request.supabase_user.user.id  # gets the user's uuid
    try:
        body = json.loads(request.body)
        name = body.get("name")
        description = body.get("description")
        price = body.get("price")
        duration = body.get("duration")

        response = shop_services.update_service(uuid, shop_id, service_id, name, description, price, duration)
        return JsonResponse(response)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)