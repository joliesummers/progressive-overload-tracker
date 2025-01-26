import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Box from '@mui/material/Box';
import { Navigate } from 'react-router-dom';

import { NotificationProvider } from './contexts/NotificationContext';
import ErrorBoundary from './components/Common/ErrorBoundary';
import Layout from './components/Layout';
import { WorkoutChat } from './components/WorkoutChat/WorkoutChat';
import AnalyticsDashboard from './components/Analytics/AnalyticsDashboard';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    background: {
      default: '#000000',
      paper: '#1e1e1e',
    },
    text: {
      primary: '#ffffff',
      secondary: 'rgba(255,255,255,0.7)',
    },
    primary: {
      main: '#1976d2',
      dark: '#1565c0',
      contrastText: '#ffffff',
    },
  },
  components: {
    MuiInputBase: {
      styleOverrides: {
        root: {
          color: '#ffffff',
        },
        input: {
          color: '#ffffff',
        },
      },
    },
    MuiFormHelperText: {
      styleOverrides: {
        root: {
          color: 'rgba(255,255,255,0.7)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        containedPrimary: {
          color: '#ffffff',
          backgroundColor: '#1976d2',
          '&:hover': {
            backgroundColor: '#1565c0',
          },
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 1,
      },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#1e1e1e',
          '&.MuiAppBar-root': {
            backgroundColor: '#000000',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#121212',
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#000000',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#121212',
        },
      },
    },
  },
});

const queryClient = new QueryClient();

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={darkTheme}>
          <CssBaseline />
          <NotificationProvider>
            <Router>
              <Box sx={{ 
                bgcolor: '#000000',
                minHeight: '100vh',
              }}>
                <Layout>
                  <Routes>
                    <Route path="/" element={<WorkoutChat />} />
                    <Route path="/analytics" element={<AnalyticsDashboard />} />
                    <Route path="/workoutchat" element={<WorkoutChat />} />
                  </Routes>
                </Layout>
              </Box>
            </Router>
          </NotificationProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
