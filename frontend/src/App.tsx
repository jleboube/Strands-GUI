import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { MainLayout } from '@/components/layout/MainLayout';
import { Landing } from '@/pages/Landing';
import { LoginForm } from '@/components/auth/LoginForm';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { Dashboard } from '@/pages/Dashboard';
import { Agents } from '@/pages/Agents';
import { AgentBuilder } from '@/pages/AgentBuilder';
import { AgentChat } from '@/pages/AgentChat';
import { Tools } from '@/pages/Tools';
import { APIKeys } from '@/pages/APIKeys';
import { Settings } from '@/pages/Settings';
import { SDKUpdate } from '@/pages/SDKUpdate';
import { Loader2 } from 'lucide-react';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      {/* Landing page - public */}
      <Route
        path="/landing"
        element={<Landing />}
      />
      <Route
        path="/login"
        element={
          <PublicRoute>
            <div className="min-h-screen flex items-center justify-center bg-background p-4">
              <LoginForm />
            </div>
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <div className="min-h-screen flex items-center justify-center bg-background p-4">
              <RegisterForm />
            </div>
          </PublicRoute>
        }
      />
      <Route
        path="/app"
        element={
          <ProtectedRoute>
            <MainLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="agents" element={<Agents />} />
        <Route path="agents/new" element={<AgentBuilder />} />
        <Route path="agents/:id" element={<AgentBuilder />} />
        <Route path="agents/:id/chat" element={<AgentChat />} />
        <Route path="tools" element={<Tools />} />
        <Route path="api-keys" element={<APIKeys />} />
        <Route path="sdk-update" element={<SDKUpdate />} />
        <Route path="settings" element={<Settings />} />
      </Route>
      {/* Redirect root to landing or app based on auth */}
      <Route path="/" element={<LandingOrApp />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function LandingOrApp() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/app" replace />;
  }

  return <Landing />;
}
