import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './lib/AuthContext';
import { useThemeStore } from './store/theme';
import { Navbar } from './components/navbar';
import { DashboardPage } from './pages/dashboard';
import { LoginPage } from './pages/login';
import { RegisterPage } from './pages/register';
import { LandingPage } from './pages/landing';
import { ProtectedRoute } from './components/auth/ProtectedRoute';

function App() {
  const isDarkMode = useThemeStore((state) => state.isDarkMode);

  return (
    <Router>
      <AuthProvider>
        <div className={`min-h-screen ${isDarkMode ? 'dark' : ''}`}>
          <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <>
                      <Navbar />
                      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
                        <DashboardPage />
                      </main>
                    </>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;