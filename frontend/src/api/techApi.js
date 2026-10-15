const BASE_URL = "http://localhost:8000/api"
const authHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem("token")}` })
const getErrorMessage = (data, fallback) => data.error || data.Error || fallback

//The backend finds the tech from the token, so no user id is needed.
//Returns [{shop_id, commission_rate, shops: {name}}, ...], or [] if they work nowhere
export const getTechShops = async () => {
    const response = await fetch(`${BASE_URL}/techs/shops/`, {
        method: "GET",
        headers: authHeaders(),
    })

    if (!response.ok) {
        const data = await response.json()
        throw new Error(getErrorMessage(data, "Failed to fetch the shops you work at"))
    }
    return response.json()
}
