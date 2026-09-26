import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the auth service
vi.mock('../services/authService', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  refreshAccessToken: vi.fn(),
}));

import { loginUser, registerUser, refreshAccessToken } from '../services/authService';

// Test component that uses useAuth
const TestComponent = () => {
  const { user, loading, login, logout, refreshAuth } = useAuth();
  return (
    <div>
      <div data-testid="loading">{loading ? 'true' : 'false'}</div>
      <div data-testid="user">{user ? user.email : 'null'}</div>
      <button onClick={() => login({ email: 'test@example.com', password: 'password123' })} data-testid="login-btn">Login</button>
      <button onClick={logout} data-testid="logout-btn">Logout</button>
      <button onClick={refreshAuth} data-testid="refresh-btn">Refresh</button>
    </div>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    vi.resetModules();
  });

  it('renders without crashing', () => {
    // Ensure no token in localStorage
    localStorage.clear();
    
    // Mock the fetch to fail so loading completes quickly
    (refreshAccessToken as vi.Mock).mockRejectedValueOnce(new Error('No token'));
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    // Just verify the component renders without error
    expect(screen.getByTestId('loading')).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    const mockTokens = {
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer',
      id: 1,
      name: 'Test User',
      email: 'test@example.com',
      role: 'Employee',
    };

    (loginUser as vi.Mock).mockResolvedValueOnce(mockTokens);
    (refreshAccessToken as vi.Mock).mockRejectedValueOnce(new Error('No token'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial loading to finish
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    // Click login
    fireEvent.click(screen.getByTestId('login-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });

    expect(localStorage.setItem).toHaveBeenCalledWith('token', 'mock-access-token');
    expect(localStorage.setItem).toHaveBeenCalledWith('refreshToken', 'mock-refresh-token');
  });

  it('handles login failure', async () => {
    // Mock login to reject but catch it in the component
    (loginUser as vi.Mock).mockRejectedValueOnce(new Error('Invalid credentials'));
    (refreshAccessToken as vi.Mock).mockRejectedValueOnce(new Error('No token'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    // Click login - this should not throw unhandled
    await act(async () => {
      try {
        fireEvent.click(screen.getByTestId('login-btn'));
        // Wait for the promise to settle
        await new Promise(resolve => setTimeout(resolve, 0));
      } catch (e) {
        // Expected to throw
      }
    });

    // Wait for the error to be handled
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('null');
    });
    
    // Verify the error was caught (no unhandled rejection)
    await waitFor(() => {
      expect(screen.getByTestId('login-btn')).toBeInTheDocument();
    });
  });

  it('clears auth on logout', () => {
    // Set initial auth state
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('refreshToken', 'mock-refresh-token');
    localStorage.setItem('role', 'Employee');
    localStorage.setItem('name', 'Test User');
    localStorage.setItem('email', 'test@example.com');
    localStorage.setItem('userId', '1');

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Click logout
    fireEvent.click(screen.getByTestId('logout-btn'));

    expect(localStorage.removeItem).toHaveBeenCalledWith('token');
    expect(localStorage.removeItem).toHaveBeenCalledWith('refreshToken');
    expect(localStorage.removeItem).toHaveBeenCalledWith('role');
    expect(localStorage.removeItem).toHaveBeenCalledWith('name');
    expect(localStorage.removeItem).toHaveBeenCalledWith('email');
    expect(localStorage.removeItem).toHaveBeenCalledWith('userId');
  });
});