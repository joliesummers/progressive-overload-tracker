import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { NotificationProvider } from './contexts/NotificationContext';
import ErrorBoundary from './components/Common/ErrorBoundary';
import Layout from './components/Layout';
import { WorkoutChat } from './components/WorkoutChat/WorkoutChat';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#90caf9',
    },
    secondary: {
      main: '#f48fb1',
    },
  },
});

const queryClient = new QueryClient();

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <NotificationProvider>
            <Router>
              <Layout>
                <Routes>
                  <Route path="/" element={<WorkoutChat />} />
                  <Route path="/analytics" element={<AnalyticsDashboard />} />
                </Routes>
              </Layout>
            </Router>
          </NotificationProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
