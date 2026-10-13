const BASE_URL = "http://localhost:8000/api"

//The backend sends errors as either {"error": ...} or {"Error": ...}
const getErrorMessage = (data, fallback) => data.error || data.Error || fallback

//The backend's AuthMiddleware reads the token from "Authorization: Bearer <token>"
const authHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem("token")}` })

export const getShopsOwned = async (userId) => {
    const response = await fetch(`${BASE_URL}/shops/owner/${userId}/`, {
        method: "GET",
        headers: authHeaders(),
    })

    if (!response.ok) {
        const data = await response.json()
        throw new Error(getErrorMessage(data, "Failed to fetch shops"))
    }

    return response.json()
}

export const getShopInfo = async (shopId) => {
    const response = await fetch(`${BASE_URL}/shops/information/${shopId}/`, {
        method: "GET",
        headers: authHeaders(),
    })
    if (!response.ok) {
        const data = await response.json()
        throw new Error(getErrorMessage(data, "Failed to fetch shop info"))
    }
    return response.json()
}