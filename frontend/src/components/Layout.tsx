//
import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  useTheme,
} from '@mui/material'
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Chat as ChatIcon,
  LocalHospital as DiagnosisIcon,
  Medication as DrugIcon,
  MenuBook as KnowledgeIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  LocalHospital,
  PersonAdd,
  Assessment as AssessmentIcon,
  Api as ApiIcon,
} from '@mui/icons-material'

const DRAWER_WIDTH = 260

interface LayoutProps {
  children: React.ReactNode
}

interface MenuItem {
  text: string
  icon: React.ReactNode
  path: string
}

export default function Layout({ children }: LayoutProps) {
  const [mobileOpen, setMobileOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const theme = useTheme()

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  const { user } = useAuth();

  // Define role visibility matrix
  const baseItems: MenuItem[] = [
    { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
    { text: 'AI Chat', icon: <ChatIcon />, path: '/chat' },
  ];
  const staffExtra: MenuItem[] = [
    { text: 'Patient Intake', icon: <PersonAdd />, path: '/patient-intake' },
  ];
  const doctorItems: MenuItem[] = [
    { text: 'Patient List', icon: <PersonAdd />, path: '/patients' },
    { text: 'Discharge Summary', icon: <AssessmentIcon />, path: '/discharge-summary' },
    { text: 'Diagnosis', icon: <DiagnosisIcon />, path: '/diagnosis' },
    { text: 'Analytics', icon: <AssessmentIcon />, path: '/analytics' },
    { text: 'FHIR API', icon: <ApiIcon />, path: '/fhir' },
    { text: 'Drug Checker', icon: <DrugIcon />, path: '/drugs' },
    { text: 'Knowledge Base', icon: <KnowledgeIcon />, path: '/knowledge' },
    { text: 'Report Parser', icon: <LocalHospital />, path: '/report-parser' },
  ];

  let menuItems: MenuItem[] = baseItems;
  if (user?.role === 'staff') {
    menuItems = [...menuItems, ...staffExtra];
  } else if (user?.role === 'doctor') {
    menuItems = [...menuItems, ...staffExtra, ...doctorItems];
  } else if (user?.role === 'admin') {
    // Admin has everything
    menuItems = [...menuItems, ...staffExtra, ...doctorItems];
  }

  const drawer = (
    <Box sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(to bottom, #fafafa 0%, #ffffff 100%)',
    }}>
      <Toolbar
        sx={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
          minHeight: 80,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.2) 0%, transparent 50%)',
            animation: 'pulse 4s ease-in-out infinite',
          },
          '@keyframes pulse': {
            '0%, 100%': { opacity: 0.6 },
            '50%': { opacity: 1 },
          },
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, width: '100%', position: 'relative', zIndex: 1 }}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '12px',
              background: 'rgba(255,255,255,0.25)',
              backdropFilter: 'blur(10px)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '28px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }}
          >
            🤖
          </Box>
          <Box>
            <Typography
              variant="h5"
              component="div"
              sx={{
                color: 'white',
                fontWeight: 800,
                letterSpacing: '-0.03em',
                textShadow: '0 2px 8px rgba(0,0,0,0.3)',
                lineHeight: 1.2,
              }}
            >
              MedAssist AI
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255,255,255,0.9)',
                fontWeight: 500,
                letterSpacing: '0.5px',
                textTransform: 'uppercase',
                fontSize: '0.65rem',
              }}
            >
              Intelligent Healthcare
            </Typography>
          </Box>
        </Box>
      </Toolbar>

      <Divider />

      <List sx={{ flexGrow: 1, px: 1, py: 2 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path)
                setMobileOpen(false)
              }}
              sx={{
                borderRadius: 3,
                px: 2,
                py: 1.5,
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                position: 'relative',
                overflow: 'hidden',
                '&.Mui-selected': {
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                  transform: 'translateX(4px) scale(1.02)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'white',
                    transform: 'scale(1.1)',
                  },
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    bottom: 0,
                    width: '4px',
                    background: 'white',
                    borderRadius: '0 4px 4px 0',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(102, 126, 234, 0.08)',
                  transform: 'translateX(6px)',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                },
              }}
            >
              <ListItemIcon
                sx={{
                  color: location.pathname === item.path ? 'white' : theme.palette.primary.main,
                  minWidth: 40,
                  transition: 'color 0.2s',
                }}
              >
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: location.pathname === item.path ? 600 : 500,
                  fontSize: '0.95rem',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />

      <List sx={{ px: 1, py: 2 }}>
        <ListItem disablePadding>
          <ListItemButton
            sx={{
              borderRadius: 2,
              transition: 'all 0.2s',
              '&:hover': {
                backgroundColor: 'rgba(99, 102, 241, 0.08)',
                transform: 'translateX(4px)',
              },
            }}
          >
            <ListItemIcon sx={{ minWidth: 40 }}>
              <SettingsIcon />
            </ListItemIcon>
            <ListItemText
              primary="Settings"
              primaryTypographyProps={{
                fontWeight: 500,
                fontSize: '0.95rem',
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>
    </Box>
  )

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <AppBar
        position="fixed"
        elevation={0}
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
          backdropFilter: 'blur(20px)',
          borderBottom: 'none',
          boxShadow: '0 4px 20px rgba(102, 126, 234, 0.25)',
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{
              mr: 2,
              display: { sm: 'none' },
              '&:hover': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              flexGrow: 1,
              fontWeight: 600,
              letterSpacing: '-0.01em',
              color: 'white',
              textShadow: '0 2px 4px rgba(0,0,0,0.2)',
            }}
          >
            Physician AI Assistant
          </Typography>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar
              sx={{
                bgcolor: 'rgba(255, 255, 255, 0.25)',
                width: 40,
                height: 40,
                backdropFilter: 'blur(10px)',
                border: '2px solid rgba(255,255,255,0.3)',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'scale(1.1)',
                  boxShadow: '0 6px 16px rgba(0,0,0,0.2)',
                },
              }}
            >
              <PersonIcon sx={{ fontSize: 22 }} />
            </Avatar>
            <Box sx={{ display: { xs: 'none', sm: 'block' } }}>
              <Typography
                variant="body2"
                sx={{
                  color: 'white',
                  fontWeight: 600,
                  lineHeight: 1.2,
                }}
              >
                {user?.full_name || 'User'}
              </Typography>
              <Typography
                variant="caption"
                sx={{
                  color: 'rgba(255,255,255,0.8)',
                  fontSize: '0.7rem',
                }}
              >
                {(user?.role || 'user').toUpperCase()}
              </Typography>
            </Box>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              borderRight: 'none',
              boxShadow: 3,
            },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
              borderRight: '1px solid rgba(0, 0, 0, 0.08)',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
          height: 'calc(100vh - 64px)',
          overflow: 'auto',
          background: 'linear-gradient(to bottom, #f8f9ff 0%, #ffffff 100%)',
          '&::-webkit-scrollbar': {
            width: '8px',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: 'transparent',
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: 'rgba(0, 0, 0, 0.2)',
            borderRadius: '4px',
            '&:hover': {
              backgroundColor: 'rgba(0, 0, 0, 0.3)',
            },
          },
        }}
      >
        {children}
      </Box>
    </Box>
  )
}
