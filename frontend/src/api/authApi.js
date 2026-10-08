const BASE_URL = "http://localhost:8000/api"

//The backend sends errors as either {"error": ...} or {"Error": ...}
const getErrorMessage = (data, fallback) => data.error || data.Error || fallback

export const registerUser = async (email, password, firstName, lastName, phone) => {
    const response = await fetch(`${BASE_URL}/auth/register/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({email, password, firstName, lastName, phone})
    })

    const data = await response.json()

    if(!response.ok) {
        throw new Error(getErrorMessage(data, "Registration failed"))
    }

    return data
}

export const loginUser = async (email, password) => {
    const response = await fetch(`${BASE_URL}/auth/login/`, {
        method: "POST",
        headers:{
            "Content-Type": "application/json"
        },
        body: JSON.stringify({email, password})
    })

    const data = await response.json()

    if(!response.ok){
        throw new Error(getErrorMessage(data, "Login failed"))
    }

    return data
}