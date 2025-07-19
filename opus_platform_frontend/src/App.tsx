import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { QueryClient, QueryClientProvider } from 'react-query';
import zhCN from 'antd/locale/zh_CN';
import { useThemeStore } from './stores/themeStore';
import { Layout } from './components/Layout';
import { AgentBuilder } from './pages/AgentBuilder';
import { AgentDashboard } from './pages/AgentDashboard';
import { AgentMarketplace } from './pages/AgentMarketplace';
import { WorkflowDesigner } from './pages/WorkflowDesigner';
import { MemoryExplorer } from './pages/MemoryExplorer';
import { DeploymentCenter } from './pages/DeploymentCenter';
import { Analytics } from './pages/Analytics';
import { Settings } from './pages/Settings';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  const { isDarkMode } = useThemeStore();

  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider
        locale={zhCN}
        theme={{
          algorithm: isDarkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
          token: {
            colorPrimary: '#1890ff',
            borderRadius: 8,
          },
        }}
      >
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<AgentDashboard />} />
              <Route path="/builder" element={<AgentBuilder />} />
              <Route path="/builder/:agentId" element={<AgentBuilder />} />
              <Route path="/marketplace" element={<AgentMarketplace />} />
              <Route path="/workflow/:agentId" element={<WorkflowDesigner />} />
              <Route path="/memory/:agentId" element={<MemoryExplorer />} />
              <Route path="/deployment" element={<DeploymentCenter />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
        </Router>
      </ConfigProvider>
    </QueryClientProvider>
  );
};