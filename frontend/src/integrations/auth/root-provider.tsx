import * as React from 'react'

export interface AuthContext {
    user: string | null
    setUser: React.Dispatch<React.SetStateAction<string | null>>
}

const AuthContext = React.createContext<AuthContext | null>(null)

const key = 'tanstack.auth.user'

function getStoredUser() {
    const token = document.cookie
        .split('; ')
        .find(row => row.startsWith('token='))
        ?.split('=')[1];
    if (token) {
        return localStorage.getItem(key)
    }
    return null
}

export function setStoredUser(user: string | null, auth: AuthContext) {
    if (user) {
        localStorage.setItem(key, user)
        auth.setUser(user)
    } else {
        localStorage.removeItem(key)
        auth.setUser(null)
    }
}

export function Provider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = React.useState<string | null>(getStoredUser())

    React.useEffect(() => {
        setUser(getStoredUser())
    }, [])

    return (
        <AuthContext.Provider value={{ user, setUser }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = React.useContext(AuthContext)
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
