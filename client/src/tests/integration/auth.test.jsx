import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import App from '../../App';

// Mock API responses
const server = setupServer(
  // Mock registration
  rest.post('http://localhost:8000/api/register/', (req, res, ctx) => {
    const { username, email } = req.body;
    return res(
      ctx.status(201),
      ctx.json({
        id: 1,
        username,
        email,
      })
    );
  }),

  // Mock login
  rest.post('http://localhost:8000/api/token/', (req, res, ctx) => {
    const { username, password } = req.body;
    if (username === 'testuser' && password === 'password123') {
      return res(
        ctx.json({
          access: 'fake-access-token',
          refresh: 'fake-refresh-token',
        })
      );
    }
    return res(
      ctx.status(401),
      ctx.json({
        detail: 'Invalid credentials',
      })
    );
  }),

  // Mock token refresh
  rest.post('http://localhost:8000/api/token/refresh/', (req, res, ctx) => {
    const { refresh } = req.body;
    if (refresh === 'fake-refresh-token') {
      return res(
        ctx.json({
          access: 'new-fake-access-token',
        })
      );
    }
    return res(
      ctx.status(401),
      ctx.json({
        detail: 'Invalid refresh token',
      })
    );
  }),

  // Mock protected route
  rest.get('http://localhost:8000/api/leads/', (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader || !authHeader.includes('Bearer ')) {
      return res(
        ctx.status(401),
        ctx.json({
          detail: 'Authentication credentials were not provided.',
        })
      );
    }
    return res(
      ctx.json([
        {
          id: 1,
          name: 'Test Lead',
          email: 'test@example.com',
          company: 'Test Company',
          lead_score: 85,
        },
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => {
  server.resetHandlers();
  localStorage.clear();
  window.history.pushState({}, '', '/');
});
afterAll(() => server.close());

describe('Authentication Flow Integration', () => {
  const renderApp = () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );
  };

  test('complete authentication flow: signup -> login -> dashboard -> logout', async () => {
    renderApp();

    // Should redirect to login page initially
    expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();

    // Navigate to signup
    fireEvent.click(screen.getByText(/create a new account/i));

    // Fill signup form
    await waitFor(() => {
      expect(screen.getByText(/create your account/i)).toBeInTheDocument();
    });

    const signupData = {
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      confirmPassword: 'password123',
    };

    Object.entries(signupData).forEach(([name, value]) => {
      fireEvent.change(screen.getByPlaceholderText(new RegExp(name, 'i')), {
        target: { value },
      });
    });

    // Submit signup form
    fireEvent.click(screen.getByRole('button', { name: /sign up/i }));

    // Should be redirected to dashboard after successful signup and auto-login
    await waitFor(() => {
      expect(screen.getByText(/lead dashboard/i)).toBeInTheDocument();
    });

    // Check if token is stored
    expect(localStorage.getItem('accessToken')).toBe('fake-access-token');
    expect(localStorage.getItem('refreshToken')).toBe('fake-refresh-token');

    // Logout
    fireEvent.click(screen.getByRole('button', { name: /logout/i }));

    // Should be redirected to login page
    await waitFor(() => {
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    });

    // Tokens should be removed
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });

  test('token refresh flow', async () => {
    // Mock an expired token scenario
    server.use(
      rest.get('http://localhost:8000/api/leads/', (req, res, ctx) => {
        const authHeader = req.headers.get('Authorization');
        if (authHeader?.includes('fake-access-token')) {
          return res(
            ctx.status(401),
            ctx.json({
              detail: 'Token is invalid or expired',
            })
          );
        }
        if (authHeader?.includes('new-fake-access-token')) {
          return res(
            ctx.json([
              {
                id: 1,
                name: 'Test Lead',
                email: 'test@example.com',
              },
            ])
          );
        }
        return res(ctx.status(401));
      })
    );

    // Set initial tokens
    localStorage.setItem('accessToken', 'fake-access-token');
    localStorage.setItem('refreshToken', 'fake-refresh-token');

    renderApp();

    // Should automatically refresh token and show dashboard
    await waitFor(() => {
      expect(screen.getByText(/lead dashboard/i)).toBeInTheDocument();
    });

    // Should have new access token
    expect(localStorage.getItem('accessToken')).toBe('new-fake-access-token');
  });

  test('handles failed token refresh', async () => {
    // Mock failed refresh token scenario
    server.use(
      rest.post('http://localhost:8000/api/token/refresh/', (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json({
            detail: 'Invalid refresh token',
          })
        );
      })
    );

    // Set invalid tokens
    localStorage.setItem('accessToken', 'expired-token');
    localStorage.setItem('refreshToken', 'invalid-refresh-token');

    renderApp();

    // Should redirect to login page
    await waitFor(() => {
      expect(screen.getByText(/sign in to your account/i)).toBeInTheDocument();
    });

    // Tokens should be removed
    expect(localStorage.getItem('accessToken')).toBeNull();
    expect(localStorage.getItem('refreshToken')).toBeNull();
  });
});
