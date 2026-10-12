import { createContext } from 'react'

//Shared by AuthProvider (which fills it) and useAuth (which reads it).
//Kept in its own file so AuthContext.jsx only exports a component and Fast Refresh keeps working.
export const AuthContext = createContext(null)
