const BASE_URL = "http://localhost:8000/api"
const authHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem("token")}` })
const getErrorMessage = (data, fallback) => data.error || data.Error || fallback

export const fetchTodayAppointments = async (shopId, date) => {

    const response = await fetch(`${BASE_URL}/shops/${shopId}/appointments/get/day/?day=${date}`, {
        method: "GET",
        headers: authHeaders(),
    })

    if (!response.ok) {
        const data = await response.json()
        throw new Error(getErrorMessage(data, "Failed to fetch today's appointments"))
    }
    return response.json()
}