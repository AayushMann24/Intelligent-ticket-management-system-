import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";

import { loginUser, registerUser, refreshAccessToken, logoutUser, type LoginData, type LoginResponse, type RegisterData } from "../services/authService";

interface User {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: LoginData) => Promise<LoginResponse | null>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user from server on init (cookies sent automatically)
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Try to get user profile - cookies sent automatically with withCredentials
        const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
        const response = await fetch(`${API_URL}/users/me`, {
          credentials: "include", // Send cookies
        });
        
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else if (response.status === 401) {
          // Try to refresh token
          try {
            await refreshAccessToken();
            // Retry fetching user
            const retryResponse = await fetch(`${API_URL}/users/me`, {
              credentials: "include",
            });
            if (retryResponse.ok) {
              const userData = await retryResponse.json();
              setUser(userData);
            } else {
              clearAuth();
            }
          } catch {
            clearAuth();
          }
        } else {
          clearAuth();
        }
      } catch {
        clearAuth();
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const clearAuth = useCallback(() => {
    setUser(null);
  }, []);

  const login = useCallback(async (data: LoginData) => {
    try {
      const response = await loginUser(data);
      
      // User data is in response, cookies are set by server
      setUser({
        id: response.id,
        name: response.name,
        email: response.email,
        role: response.role,
      });
      
      return response;
    } catch (error) {
      // Clear any partial auth state on error
      clearAuth();
      // Don't re-throw - handle gracefully
      return null;
    }
  }, [clearAuth]);

  const register = useCallback(async (data: RegisterData) => {
    await registerUser(data);
    // After registration, user needs to log in
  }, []);

  const logout = useCallback(async () => {
    try {
      await logoutUser();
    } finally {
      clearAuth();
    }
  }, [clearAuth]);

  const refreshAuth = useCallback(async () => {
    try {
      await refreshAccessToken();
      // Refetch user
      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_URL}/users/me`, {
        credentials: "include",
      });
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch {
      clearAuth();
    }
  }, [clearAuth]);

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        refreshAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}