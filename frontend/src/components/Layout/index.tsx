import React from 'react';
import { Box, AppBar, Toolbar, Typography, IconButton, Drawer, List, ListItem, ListItemIcon, ListItemText, useTheme } from '@mui/material';
import { Menu as MenuIcon, FitnessCenter, Chat } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [drawerOpen, setDrawerOpen] = React.useState(false);
  const theme = useTheme();
  const navigate = useNavigate();

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigation = (path: string) => {
    navigate(path);
    setDrawerOpen(false);
  };

  const menuItems = [
    { text: 'Workout Chat', icon: <Chat />, path: '/' },
    { text: 'Analytics', icon: <FitnessCenter />, path: '/analytics' },
  ];

  return (
    <Box sx={{ 
      display: 'flex',
      bgcolor: '#000000',
      minHeight: '100vh',
      '& .MuiInputBase-root': {
        color: '#fff',
      },
      '& .MuiFormHelperText-root': {
        color: 'rgba(255,255,255,0.7)',
      },
      '& .MuiButton-root': {
        color: '#fff',
      },
    }}>
      <AppBar 
        position="fixed"
        sx={{ 
          bgcolor: '#000000',
          borderBottom: 1,
          borderColor: 'divider',
          '& .MuiTypography-root': {
            color: '#fff',
          },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Progressive Overload
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="temporary"
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        sx={{
          '& .MuiDrawer-paper': { 
            width: 240,
            bgcolor: '#1e1e1e',
            borderRight: 1,
            borderColor: 'divider',
            '& .MuiTypography-root': {
              color: '#fff',
            },
            '& .MuiListItemIcon-root': {
              color: '#fff',
            },
          },
        }}
      >
        <Toolbar />
        <List>
          {menuItems.map((item) => (
            <ListItem 
              button 
              key={item.text} 
              onClick={() => handleNavigation(item.path)}
              sx={{
                '&:hover': {
                  bgcolor: 'rgba(255,255,255,0.1)',
                },
              }}
            >
              <ListItemIcon sx={{ color: '#fff' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Drawer>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: '100%',
          minHeight: '100vh',
          bgcolor: '#000000',
          mt: '64px',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
