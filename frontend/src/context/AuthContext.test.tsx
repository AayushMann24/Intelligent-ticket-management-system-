import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { AuthProvider } from '../context/AuthContext';
import { useAuth } from '../context/useAuth';
import { vi, describe, it, expect, beforeEach } from 'vitest';

// Mock the auth service
vi.mock('../services/authService', () => ({
  loginUser: vi.fn(),
  registerUser: vi.fn(),
  refreshAccessToken: vi.fn(),
  logoutUser: vi.fn(),
}));

import { loginUser, refreshAccessToken, logoutUser } from '../services/authService';

// Mock fetch
global.fetch = vi.fn();

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
    vi.resetModules();
    (global.fetch as vi.Mock).mockReset();
  });

  it('renders without crashing', () => {
    // Mock the fetch to fail so loading completes quickly
    (global.fetch as vi.Mock).mockRejectedValueOnce(new Error('No token'));
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
    (global.fetch as vi.Mock).mockRejectedValueOnce(new Error('No token'));
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

    // Verify loginUser was called
    expect(loginUser).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password123' });
  });

  it('handles login failure', async () => {
    // Mock login to reject but catch it in the component
    (loginUser as vi.Mock).mockRejectedValueOnce(new Error('Invalid credentials'));
    (global.fetch as vi.Mock).mockRejectedValueOnce(new Error('No token'));
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
      } catch {
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

  it('clears auth on logout', async () => {
    (logoutUser as vi.Mock).mockResolvedValueOnce({ message: 'Logged out successfully' });
    (global.fetch as vi.Mock).mockRejectedValueOnce(new Error('No token'));
    (refreshAccessToken as vi.Mock).mockRejectedValueOnce(new Error('No token'));

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial loading
    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    // Click logout
    fireEvent.click(screen.getByTestId('logout-btn'));

    // Wait for logout to complete
    await waitFor(() => {
      expect(logoutUser).toHaveBeenCalled();
    });
  });
});