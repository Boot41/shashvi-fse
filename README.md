# **AI Job Application Email Summarizer & Ghosting Tracker**  

Welcome to the **AI Job Application Email Summarizer & Ghosting Tracker**! This project is designed to help job seekers streamline their job application process by automatically summarizing job application emails, tracking application statuses, detecting ghosting, and providing AI-powered follow-up recommendations.

---

## **✨ Key Features**  

### **1. Email Summarization**  
- Automatically fetches job application emails from **Gmail/Outlook**.  
- Uses **AI (spaCy/OpenAI API)** to extract key details:  
  - **Applicant Name**  
  - **Job Title**  
  - **Company Name**  
  - **Key Skills/Qualifications**  
  - **Call to Action (Next Steps)**  

### **2. Application Tracking**  
- Tracks the status of each job application:  
  - **Applied**  
  - **Interview Scheduled**  
  - **Ghosted**  
  - **Closed**  
- Provides a **dashboard** to view all applications in one place.  

### **3. Ghosting Detection**  
- Detects if a job application has been **ghosted** by:  
  - Checking if the job listing **still exists** (via web scraping).  
  - Tracking the **time elapsed** since the last response.  
- Sends **alerts** for ghosted applications.  

### **4. AI-Powered Follow-Up Recommendations**  
- Generates **personalized follow-up emails** using **OpenAI API**.  
- Provides **one-click sending** for follow-ups.  

### **5. Job Success Insights**  
- Tracks **which companies respond the most**.  
- Shows **which job applications have the highest success rate**.  

---

## **🛠️ Tech Stack**  

### **Frontend**  
- **React** (with **Tailwind CSS** for styling).  
- **Axios** for API calls.  

### **Backend**  
- **Django** (Python) for the backend API.  
- **PostgreSQL** for database storage.  

### **AI/ML**  
- **spaCy** for text processing.  
- **OpenAI API** for summarization and follow-up email generation.  

### **DevOps**  
- **Docker** for containerization.  
- **GitHub** for version control.  

---

## **🚀 Getting Started**  

### **Prerequisites**  
- **Node.js** and **npm** installed for React.  
- **Python 3.x** and **pip** installed for Django.  
- **Docker** installed for containerization.  
- **PostgreSQL** installed or accessible.  

### **Installation**  

1. **Clone the Repository**  
   ```bash  
   git clone https://github.com/your-username/ai-job-application-tracker.git  
   cd ai-job-application-tracker  
   ```  

2. **Set Up Backend**  
   - Navigate to the `backend` folder:  
     ```bash  
     cd backend  
     ```  
   - Create a virtual environment:  
     ```bash  
     python -m venv venv  
     source venv/bin/activate  # On Windows: venv\Scripts\activate  
     ```  
   - Install dependencies:  
     ```bash  
     pip install -r requirements.txt  
     ```  
   - Set up the database:  
     ```bash  
     python manage.py migrate  
     ```  
   - Run the Django server:  
     ```bash  
     python manage.py runserver  
     ```  

3. **Set Up Frontend**  
   - Navigate to the `frontend` folder:  
     ```bash  
     cd ../frontend  
     ```  
   - Install dependencies:  
     ```bash  
     npm install  
     ```  
   - Start the React app:  
     ```bash  
     npm start  
     ```  

4. **Run with Docker**  
   - Build and run the Docker containers:  
     ```bash  
     docker-compose up --build  
     ```  

---

## **📂 Project Structure**  

```  
ai-job-application-tracker/  
├── backend/                  # Django backend  
│   ├── manage.py  
│   ├── requirements.txt  
│   ├── Dockerfile  
│   └── ...  
├── frontend/                 # React frontend  
│   ├── src/  
│   ├── public/  
│   ├── package.json  
│   ├── Dockerfile  
│   └── ...  
├── docker-compose.yml        # Docker configuration  
└── README.md  
```  

---

## **🔧 Configuration**  

### **Environment Variables**  
Create a `.env` file in the `backend` folder with the following variables:  

```  
# Django  
SECRET_KEY=your-secret-key  
DEBUG=True  
DATABASE_URL=postgres://user:password@db:5432/jobtracker  

# Email API  
GMAIL_API_KEY=your-gmail-api-key  
OUTLOOK_API_KEY=your-outlook-api-key  

# OpenAI API  
OPENAI_API_KEY=your-openai-api-key  
```  

---

## **📈 Future Enhancements**  
- **Multi-platform integration** (LinkedIn, Indeed tracking).  
- **Success prediction** using advanced AI models.  
- **Refined job insights & analytics**.  
- **Mobile app** for on-the-go tracking.  

---

## **🙏 Contributing**  
Contributions are welcome! Please fork the repository and submit a pull request.  

Happy job hunting! 🚀