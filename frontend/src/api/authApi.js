const BASE_URL = "http://localhost:8000/api"

export const registerUser = async (email, password) => {
    const response = await fetch(`${BASE_URL}/auth/register/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({email, password})
    })
    
    const data = await response.json()
    
    if(!response.ok) {
        throw new Error(data.error || "Registration failed")
    }

    return data
}