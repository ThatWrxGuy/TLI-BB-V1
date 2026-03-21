import { createContext, useContext, useState, useEffect } from 'react'
import { authAPI } from '../services/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = localStorage.getItem('token')
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await authAPI.getMe()
      setUser(response.data)
    } catch (err) {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    setError(null)
    try {
      const response = await authAPI.login(email, password)
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      await checkAuth()
      return true
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
      return false
    }
  }

  const signup = async (email, password, fullName) => {
    setError(null)
    try {
      await authAPI.signup(email, password, fullName)
      return true
    } catch (err) {
      setError(err.response?.data?.detail || 'Signup failed')
      return false
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (err) {
      // Ignore errors
    } finally {
      localStorage.removeItem('token')
      setUser(null)
    }
  }

  const value = {
    user,
    loading,
    error,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
