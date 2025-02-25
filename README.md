# AI-Powered Lead Generation System

## Project Overview
This project is an AI-powered lead generation system designed to streamline the process of identifying and scoring potential leads for businesses. It leverages advanced algorithms to automate the generation of personalized messages and assess leads based on various attributes, including company size, funding, and industry relevance.

## Key Features
- **Lead Management**: Create, update, and manage leads through a RESTful API.
- **Automated Scoring**: Calculate lead scores based on predefined criteria to prioritize high-value leads.
- **Personalized Messaging**: Generate tailored email and LinkedIn messages for outreach.
- **Data Import**: Import leads from CSV files for easy integration of existing data.
- **Error Handling**: Robust error management to ensure system stability and reliability.
- **Comprehensive Testing**: Unit tests to maintain code quality and improve test coverage.

## Technologies Used
- **Backend**: Django, Django REST Framework
- **Frontend**: React (JavaScript)
- **Database**: PostgreSQL (or your choice of database)
- **Testing**: Django's testing framework, pytest

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   - Update your database settings in `settings.py`.
   - Run migrations:
     ```bash
     python manage.py migrate
     ```

5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints
- **Leads**
  - `GET /api/leads/`: List all leads
  - `POST /api/leads/`: Create a new lead
  - `GET /api/leads/<id>/`: Retrieve a specific lead
  - `PATCH /api/leads/<id>/`: Update a specific lead
  - `DELETE /api/leads/<id>/`: Delete a specific lead

- **Lead Processing**
  - `POST /api/leads/process/`: Process leads based on filters
  - `POST /api/leads/import/`: Import leads from a CSV file

- **Message Generation**
  - `POST /api/leads/generate-messages/`: Generate messages for leads
  - `POST /api/leads/test-message/`: Test message generation

## Testing
To run the tests, use the following command:
```bash
python manage.py test
```

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License.
