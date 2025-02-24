import { useNavigate } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-center space-y-12 text-center">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-3">
            <BrainCircuit className="h-12 w-12 text-blue-600" />
            <span className="text-4xl font-bold text-gray-900 dark:text-white">
              LeadAI
            </span>
          </div>

          {/* Project Description */}
          <div className="max-w-2xl space-y-4">
            <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-5xl md:text-6xl">
              AI-Powered Lead Generation
            </h1>
            <p className="mx-auto mt-3 max-w-md text-xl text-gray-500 dark:text-gray-400 sm:text-xl md:mt-5 md:max-w-3xl">
              Transform your outreach strategy with AI-driven lead generation.
              Automatically identify, score, and engage high-value prospects while
              maintaining personalized communication at scale.
            </p>
          </div>

          {/* Login Button */}
          <div className="mt-10">
            <Button
              size="lg"
              className="text-lg"
              onClick={() => navigate('/login')}
            >
              Login to Dashboard
            </Button>
          </div>

          {/* Features Grid */}
          <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:bg-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Smart Lead Scoring
              </h3>
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                AI-powered algorithms analyze and score leads based on multiple
                data points.
              </p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:bg-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Automated Outreach
              </h3>
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                Personalized email campaigns that adapt based on recipient
                engagement.
              </p>
            </div>
            <div className="rounded-lg bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:bg-gray-800">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Response Analysis
              </h3>
              <p className="mt-2 text-gray-500 dark:text-gray-400">
                Intelligent analysis of responses to optimize follow-up strategies.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}