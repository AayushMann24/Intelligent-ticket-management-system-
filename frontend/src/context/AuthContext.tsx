import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";

import { loginUser, registerUser, refreshAccessToken, type LoginData, type LoginResponse, type RegisterData } from "../services/authService";

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
  logout: () => void;
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

  // Load user from localStorage on init
  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("token");
      const refreshToken = localStorage.getItem("refreshToken");
      
      if (token) {
        try {
          // Try to get user profile
          const response = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/users/me`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else if (response.status === 401 && refreshToken) {
            // Try to refresh token
            try {
              await refreshAccessToken({ refresh_token: refreshToken });
              // Retry fetching user
              const retryResponse = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/users/me`, {
                headers: {
                  Authorization: `Bearer ${localStorage.getItem("token")}`,
                },
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
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const clearAuth = useCallback(() => {
    localStorage.removeItem("token");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("role");
    localStorage.removeItem("name");
    localStorage.removeItem("email");
    localStorage.removeItem("userId");
    setUser(null);
  }, []);

  const login = useCallback(async (data: LoginData) => {
    try {
      const response = await loginUser(data);
      
      localStorage.setItem("token", response.access_token);
      localStorage.setItem("refreshToken", response.refresh_token);
      localStorage.setItem("role", response.role);
      localStorage.setItem("name", response.name);
      localStorage.setItem("email", response.email);
      localStorage.setItem("userId", response.id.toString());
      
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
  }, []);

  const register = useCallback(async (data: RegisterData) => {
    await registerUser(data);
  }, []);

  const logout = useCallback(() => {
    clearAuth();
  }, [clearAuth]);

  const refreshAuth = useCallback(async () => {
    const refreshToken = localStorage.getItem("refreshToken");
    if (refreshToken) {
      try {
        await refreshAccessToken({ refresh_token: refreshToken });
        // Refetch user
        const response = await fetch(`${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"}/users/me`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        }
      } catch {
        clearAuth();
      }
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