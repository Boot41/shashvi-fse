import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import Dashboard from '../../components/dashboard/Dashboard';

const mockLeads = [
  {
    id: 1,
    name: 'John Doe',
    email: 'john@example.com',
    company: 'Example Corp',
    lead_score: 85,
  },
  {
    id: 2,
    name: 'Jane Smith',
    email: 'jane@example.com',
    company: 'Tech Inc',
    lead_score: 92,
  },
];

const mockMessages = {
  linkedin_message: 'Hi John, I noticed your work at Example Corp...',
  email: 'Dear John,\n\nI hope this email finds you well...',
};

const server = setupServer(
  // Mock leads list
  rest.get('http://localhost:8000/api/leads/', (req, res, ctx) => {
    return res(ctx.json(mockLeads));
  }),

  // Mock lead processing
  rest.post('http://localhost:8000/api/leads/process/', (req, res, ctx) => {
    return res(ctx.json({ message: 'Leads processed successfully' }));
  }),

  // Mock message generation
  rest.post('http://localhost:8000/api/leads/:id/generate-messages/', (req, res, ctx) => {
    return res(ctx.json(mockMessages));
  }),

  // Mock lead import
  rest.post('http://localhost:8000/api/leads/import/', (req, res, ctx) => {
    return res(ctx.json({ message: 'Leads imported successfully' }));
  })
);

beforeAll(() => {
  server.listen();
  // Mock auth token
  localStorage.setItem('accessToken', 'fake-access-token');
});

afterEach(() => {
  server.resetHandlers();
});

afterAll(() => {
  server.close();
  localStorage.clear();
});

describe('Leads Management Integration', () => {
  const renderDashboard = () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    );
  };

  test('displays leads and handles message generation', async () => {
    renderDashboard();

    // Wait for leads to load
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });

    // Check lead scores are displayed
    expect(screen.getByText('Score: 85')).toBeInTheDocument();
    expect(screen.getByText('Score: 92')).toBeInTheDocument();

    // Generate messages for first lead
    const generateButtons = screen.getAllByText('Generate Messages');
    fireEvent.click(generateButtons[0]);

    // Check if messages are displayed
    await waitFor(() => {
      expect(screen.getByText('Generated Messages')).toBeInTheDocument();
      expect(screen.getByText(/Hi John, I noticed your work/)).toBeInTheDocument();
      expect(screen.getByText(/Dear John,/)).toBeInTheDocument();
    });
  });

  test('handles lead processing', async () => {
    renderDashboard();

    // Click process leads button
    const processButton = screen.getByText('Process All Leads');
    fireEvent.click(processButton);

    // Verify leads are reloaded after processing
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  test('handles lead import', async () => {
    renderDashboard();

    // Mock file upload
    const file = new File(['test data'], 'leads.csv', { type: 'text/csv' });
    const input = screen.getByLabelText(/file/i);
    
    Object.defineProperty(input, 'files', {
      value: [file],
    });
    fireEvent.change(input);

    // Click upload button
    const uploadButton = screen.getByText('Upload Leads');
    fireEvent.click(uploadButton);

    // Check for success message
    await waitFor(() => {
      expect(screen.getByText(/Upload successful!/i)).toBeInTheDocument();
    });

    // Verify leads are reloaded after upload
    await waitFor(() => {
      expect(screen.getByText('John Doe')).toBeInTheDocument();
      expect(screen.getByText('Jane Smith')).toBeInTheDocument();
    });
  });

  test('handles API errors gracefully', async () => {
    // Mock API error
    server.use(
      rest.get('http://localhost:8000/api/leads/', (req, res, ctx) => {
        return res(
          ctx.status(500),
          ctx.json({ error: 'Internal server error' })
        );
      })
    );

    renderDashboard();

    // Check if error message is displayed
    await waitFor(() => {
      expect(screen.getByText('An error occurred')).toBeInTheDocument();
    });
  });

  test('handles unauthorized access', async () => {
    // Mock unauthorized response
    server.use(
      rest.get('http://localhost:8000/api/leads/', (req, res, ctx) => {
        return res(
          ctx.status(401),
          ctx.json({ detail: 'Authentication credentials were not provided.' })
        );
      })
    );

    const mockNavigate = jest.fn();
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate,
    }));

    renderDashboard();

    // Should redirect to login
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });
});
