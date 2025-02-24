import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { act } from 'react-dom/test-utils';
import SignUp from '../SignUp';
import { auth } from '../../../services/api';

// Mock the auth service
jest.mock('../../../services/api', () => ({
  auth: {
    register: jest.fn(),
    login: jest.fn(),
  },
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

describe('SignUp Component', () => {
  beforeEach(() => {
    // Clear mocks before each test
    jest.clearAllMocks();
    // Clear localStorage
    localStorage.clear();
  });

  const renderSignUp = () => {
    render(
      <BrowserRouter>
        <SignUp />
      </BrowserRouter>
    );
  };

  const fillForm = ({
    username = 'testuser',
    email = 'test@example.com',
    password = 'password123',
    confirmPassword = 'password123',
  } = {}) => {
    fireEvent.change(screen.getByPlaceholderText(/username/i), {
      target: { value: username },
    });
    fireEvent.change(screen.getByPlaceholderText(/email address/i), {
      target: { value: email },
    });
    fireEvent.change(screen.getByPlaceholderText(/^password$/i), {
      target: { value: password },
    });
    fireEvent.change(screen.getByPlaceholderText(/confirm password/i), {
      target: { value: confirmPassword },
    });
  };

  test('renders signup form', () => {
    renderSignUp();
    expect(screen.getByPlaceholderText(/username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/email address/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/^password$/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/confirm password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument();
  });

  test('shows error when passwords do not match', async () => {
    renderSignUp();
    fillForm({ confirmPassword: 'differentpassword' });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    });

    expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
    expect(auth.register).not.toHaveBeenCalled();
  });

  test('shows error when password is too short', async () => {
    renderSignUp();
    fillForm({ password: 'short', confirmPassword: 'short' });

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    });

    expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument();
    expect(auth.register).not.toHaveBeenCalled();
  });

  test('handles successful registration and login', async () => {
    const mockRegisterResponse = {
      data: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
      },
    };

    const mockLoginResponse = {
      data: {
        access: 'fake-access-token',
        refresh: 'fake-refresh-token',
      },
    };

    auth.register.mockResolvedValueOnce(mockRegisterResponse);
    auth.login.mockResolvedValueOnce(mockLoginResponse);

    renderSignUp();
    fillForm();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    });

    await waitFor(() => {
      expect(auth.register).toHaveBeenCalledWith({
        username: 'testuser',
        email: 'test@example.com',
        password: 'password123',
      });
      expect(auth.login).toHaveBeenCalledWith({
        username: 'testuser',
        password: 'password123',
      });
      expect(localStorage.getItem('accessToken')).toBe('fake-access-token');
      expect(localStorage.getItem('refreshToken')).toBe('fake-refresh-token');
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  test('handles registration failure', async () => {
    const errorMessage = 'Username already exists';
    auth.register.mockRejectedValueOnce({
      response: { data: { message: errorMessage } },
    });

    renderSignUp();
    fillForm();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    });

    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument();
      expect(auth.login).not.toHaveBeenCalled();
      expect(localStorage.getItem('accessToken')).toBeNull();
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });

  test('disables submit button while loading', async () => {
    auth.register.mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

    renderSignUp();
    fillForm();

    await act(async () => {
      fireEvent.click(screen.getByRole('button', { name: /sign up/i }));
    });

    const submitButton = screen.getByRole('button', { name: /creating account/i });
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent(/creating account/i);
  });
});
