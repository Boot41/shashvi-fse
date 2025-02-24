import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useThemeStore } from './store/theme';
import { Navbar } from './components/navbar';
import { DashboardPage } from './pages/dashboard';
import { LandingPage } from './pages/landing';
import { LoginPage } from './pages/login';
import { RegisterPage } from './pages/register';

function App() {
  const { isDarkMode } = useThemeStore();

  return (
    <Router>
      <div className={isDarkMode ? 'dark' : ''}>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/dashboard"
              element={
                <>
                  <Navbar />
                  <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                    <DashboardPage />
                  </main>
                </>
              }
            />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;