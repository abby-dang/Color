import { useState } from 'react'
import { AuthContext } from './authContextObject'

export function AuthProvider({ children }) {
    const [token, setToken] = useState(() => localStorage.getItem("token"))
    const [user, setUser] = useState(() => JSON.parse(localStorage.getItem("user")))

    const login = (data) => {
        //data is the response from loginUser: {id, email, token}
        localStorage.setItem("token", data.token)
        setToken(data.token)

        const newUser = { id: data.user_id, email: data.email, first_name: data.first_name, last_name: data.last_name, phone: data.phone }
        localStorage.setItem("user", JSON.stringify(newUser))
        setUser(newUser)

    }

    const logout = () => {
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ token, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}
