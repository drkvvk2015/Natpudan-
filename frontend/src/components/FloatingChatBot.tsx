import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  IconButton,
  TextField,
  Typography,
  Fab,
  Badge,
  Divider,
  CircularProgress,
  Avatar,
  Collapse,
  Chip,
  Zoom,
  Fade,
  Slide,
  keyframes,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Close as CloseIcon,
  Send as SendIcon,
  SmartToy as BotIcon,
  Person as PersonIcon,
  Minimize as MinimizeIcon,
  AutoAwesome as SparklesIcon,
  Psychology as BrainIcon,
} from '@mui/icons-material';
import { sendChatMessage } from '../services/api';
import { useAuth } from '../context/AuthContext';

// Animated gradient keyframes
const gradientAnimation = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

const shimmer = keyframes`
  0% { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
`;

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const FloatingChatBot: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI medical assistant. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [authState, setAuthState] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated } = useAuth();

  // Listen for authentication state changes
  useEffect(() => {
    console.log('FloatingChatBot: isAuthenticated =', isAuthenticated);
    setAuthState(isAuthenticated);

    // Listen for custom auth state change events
    const handleAuthChange = (event: CustomEvent) => {
      console.log('FloatingChatBot: Auth state changed via event', event.detail);
      setAuthState(event.detail.isAuthenticated);
    };

    window.addEventListener('authStateChanged', handleAuthChange as EventListener);
    return () => window.removeEventListener('authStateChanged', handleAuthChange as EventListener);
  }, [isAuthenticated]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen) {
      setUnreadCount(0);
    }
  }, [isOpen]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(inputMessage);
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message.content,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMessage]);
      
      if (!isOpen) {
        setUnreadCount((prev) => prev + 1);
      }
    } catch (error: any) {
      console.error('Chat error:', error);
      let errorMsg = 'Sorry, I encountered an error. Please try again.';
      
      if (error?.response?.status === 401) {
        errorMsg = '🔒 Please log in to use the AI assistant.';
      } else if (error?.response?.status === 500) {
        errorMsg = '⚠️ Server error. Please check if OpenAI API key is configured.';
      } else if (error?.response?.data?.detail) {
        errorMsg = `❌ ${error.response.data.detail}`;
      } else if (error?.message) {
        errorMsg = `❌ ${error.message}`;
      }
      
      const errorMessage: Message = {
        role: 'assistant',
        content: errorMsg,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Use authState which updates via both context and custom events
  if (!authState) {
    return null; // Don't show chatbot if not logged in
  }

  return (
    <>
      {/* Floating Action Button with Gradient */}
      <Zoom in={!isOpen} timeout={300}>
        <Fab
          aria-label="chat"
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            zIndex: 1300,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            width: 64,
            height: 64,
            animation: `${pulse} 2s ease-in-out infinite`,
            boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
              transform: 'scale(1.1)',
              boxShadow: '0 12px 40px rgba(102, 126, 234, 0.6)',
            },
            transition: 'all 0.3s ease',
          }}
          onClick={() => setIsOpen(true)}
        >
          <Badge 
            badgeContent={unreadCount} 
            color="error"
            sx={{
              '& .MuiBadge-badge': {
                animation: unreadCount > 0 ? `${pulse} 1s ease-in-out infinite` : 'none',
              },
            }}
          >
            <SparklesIcon sx={{ fontSize: 32 }} />
          </Badge>
        </Fab>
      </Zoom>

      {/* Chat Window */}
      <Slide direction="up" in={isOpen} timeout={400}>
        <Paper
          elevation={24}
          sx={{
            position: 'fixed',
            bottom: 24,
            right: 24,
            width: 400,
            height: 600,
            zIndex: 1300,
            display: 'flex',
            flexDirection: 'column',
            borderRadius: 4,
            overflow: 'hidden',
            border: '2px solid',
            borderColor: 'transparent',
            background: 'linear-gradient(white, white) padding-box, linear-gradient(135deg, #667eea, #764ba2, #f093fb, #4facfe) border-box',
            boxShadow: '0 20px 60px rgba(102, 126, 234, 0.3)',
          }}
        >
          {/* Animated Header */}
          <Box
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
              backgroundSize: '200% 200%',
              animation: `${gradientAnimation} 8s ease infinite`,
              color: 'white',
              p: 2.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <Avatar
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  backdropFilter: 'blur(10px)',
                  animation: `${pulse} 2s ease-in-out infinite`,
                }}
              >
                <BrainIcon sx={{ color: 'white' }} />
              </Avatar>
              <Box>
                <Typography variant="h6" fontWeight="bold" sx={{ lineHeight: 1.2 }}>
                  AI Medical Assistant
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: '#4ade80',
                      animation: `${pulse} 1.5s ease-in-out infinite`,
                    }}
                  />
                  <Typography variant="caption" sx={{ opacity: 0.9 }}>
                    Online & Ready
                  </Typography>
                </Box>
              </Box>
            </Box>
            <Box>
              <IconButton
                size="small"
                sx={{ color: 'white', mr: 0.5 }}
                onClick={() => setIsOpen(false)}
              >
                <MinimizeIcon />
              </IconButton>
              <IconButton
                size="small"
                sx={{ color: 'white' }}
                onClick={() => {
                  setIsOpen(false);
                  setMessages([
                    {
                      role: 'assistant',
                      content: 'Hello! I\'m your AI medical assistant. How can I help you today?',
                      timestamp: new Date(),
                    },
                  ]);
                }}
              >
                <CloseIcon />
              </IconButton>
            </Box>
          </Box>

          <Divider />

          {/* Messages Area with Gradient Background */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              p: 2.5,
              background: 'linear-gradient(to bottom, #fafafa 0%, #f0f4ff 100%)',
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              '&::-webkit-scrollbar': {
                width: '8px',
              },
              '&::-webkit-scrollbar-track': {
                background: 'rgba(0,0,0,0.05)',
                borderRadius: '10px',
              },
              '&::-webkit-scrollbar-thumb': {
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '10px',
              },
            }}
          >
            {messages.map((msg, index) => (
              <Fade in={true} timeout={500} key={index}>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    gap: 1,
                    animation: 'slideUp 0.3s ease-out',
                    '@keyframes slideUp': {
                      from: { opacity: 0, transform: 'translateY(10px)' },
                      to: { opacity: 1, transform: 'translateY(0)' },
                    },
                  }}
                >
                  {msg.role === 'assistant' && (
                    <Avatar
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        width: 36,
                        height: 36,
                        boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                      }}
                    >
                      <BotIcon sx={{ fontSize: 20 }} />
                    </Avatar>
                  )}
                  <Paper
                    elevation={msg.role === 'user' ? 4 : 2}
                    sx={{
                      p: 2,
                      maxWidth: '75%',
                      background: msg.role === 'user' 
                        ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                        : 'white',
                      color: msg.role === 'user' ? 'white' : '#1f2937',
                      borderRadius: msg.role === 'user' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                      wordWrap: 'break-word',
                      boxShadow: msg.role === 'user'
                        ? '0 8px 24px rgba(102, 126, 234, 0.3)'
                        : '0 2px 12px rgba(0,0,0,0.08)',
                      position: 'relative',
                      '&::before': msg.role === 'assistant' ? {
                        content: '""',
                        position: 'absolute',
                        left: -2,
                        top: 12,
                        width: 4,
                        height: '60%',
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        borderRadius: '10px',
                      } : {},
                    }}
                  >
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        whiteSpace: 'pre-wrap',
                        fontSize: '0.95rem',
                        lineHeight: 1.6,
                        fontWeight: msg.role === 'assistant' ? 400 : 500,
                      }}
                    >
                      {msg.content}
                    </Typography>
                    <Typography
                      variant="caption"
                      sx={{
                        display: 'block',
                        mt: 1,
                        opacity: 0.7,
                        fontSize: '0.7rem',
                        textAlign: 'right',
                      }}
                    >
                      {msg.timestamp.toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </Typography>
                  </Paper>
                  {msg.role === 'user' && (
                    <Avatar
                      sx={{
                        background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                        width: 36,
                        height: 36,
                        boxShadow: '0 4px 12px rgba(240, 147, 251, 0.3)',
                      }}
                    >
                      <PersonIcon sx={{ fontSize: 20 }} />
                    </Avatar>
                  )}
                </Box>
              </Fade>
            ))}
            {isLoading && (
              <Fade in={true} timeout={300}>
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', gap: 1 }}>
                  <Avatar
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      width: 36,
                      height: 36,
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                    }}
                  >
                    <BotIcon sx={{ fontSize: 20 }} />
                  </Avatar>
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: 'white',
                      borderRadius: '20px 20px 20px 4px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 1.5,
                      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                    }}
                  >
                    <CircularProgress 
                      size={20}
                      sx={{
                        color: '#667eea',
                      }}
                    />
                    <Box sx={{ display: 'flex', gap: 0.5 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: '#667eea',
                          animation: `${pulse} 1s ease-in-out infinite`,
                          animationDelay: '0s',
                        }}
                      />
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: '#764ba2',
                          animation: `${pulse} 1s ease-in-out infinite`,
                          animationDelay: '0.2s',
                        }}
                      />
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: '#f093fb',
                          animation: `${pulse} 1s ease-in-out infinite`,
                          animationDelay: '0.4s',
                        }}
                      />
                    </Box>
                  </Paper>
                </Box>
              </Fade>
            )}
            <div ref={messagesEndRef} />
          </Box>

          <Divider />

          {/* Input Area with Modern Styling */}
          <Box 
            sx={{ 
              p: 2.5, 
              bgcolor: 'white',
              borderTop: '1px solid rgba(102, 126, 234, 0.1)',
              background: 'linear-gradient(to top, #ffffff 0%, #f8f9ff 100%)',
            }}
          >
            <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-end' }}>
              <TextField
                fullWidth
                placeholder="Ask me anything about medical care..."
                variant="outlined"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                disabled={isLoading}
                multiline
                maxRows={4}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '20px',
                    bgcolor: '#f8f9ff',
                    fontSize: '0.95rem',
                    transition: 'all 0.3s ease',
                    '& fieldset': {
                      borderColor: 'rgba(102, 126, 234, 0.2)',
                      borderWidth: 2,
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(102, 126, 234, 0.4)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#667eea',
                      borderWidth: 2,
                    },
                    '&.Mui-focused': {
                      bgcolor: 'white',
                      boxShadow: '0 4px 12px rgba(102, 126, 234, 0.15)',
                    },
                  },
                  '& .MuiInputBase-input': {
                    color: '#1f2937',
                  },
                  '& .MuiInputBase-input::placeholder': {
                    color: '#9ca3af',
                    opacity: 1,
                  },
                }}
              />
              <IconButton
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                sx={{
                  background: inputMessage.trim() 
                    ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                    : '#e5e7eb',
                  color: 'white',
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  transition: 'all 0.3s ease',
                  boxShadow: inputMessage.trim()
                    ? '0 4px 12px rgba(102, 126, 234, 0.3)'
                    : 'none',
                  '&:hover': {
                    background: inputMessage.trim()
                      ? 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)'
                      : '#e5e7eb',
                    transform: inputMessage.trim() ? 'scale(1.1) rotate(10deg)' : 'none',
                    boxShadow: inputMessage.trim()
                      ? '0 6px 16px rgba(102, 126, 234, 0.4)'
                      : 'none',
                  },
                  '&:active': {
                    transform: 'scale(0.95)',
                  },
                  '&.Mui-disabled': {
                    bgcolor: '#e5e7eb',
                    color: '#9ca3af',
                  },
                }}
              >
                <SendIcon />
              </IconButton>
            </Box>
            {/* Quick Actions */}
            <Box sx={{ display: 'flex', gap: 1, mt: 1.5, flexWrap: 'wrap' }}>
              <Chip
                label="💊 Medications"
                size="small"
                onClick={() => !isLoading && setInputMessage('Tell me about common medications')}
                sx={{
                  background: 'linear-gradient(135deg, #667eea20 0%, #764ba220 100%)',
                  border: '1px solid #667eea40',
                  color: '#667eea',
                  fontWeight: 500,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #667eea30 0%, #764ba230 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 8px rgba(102, 126, 234, 0.2)',
                  },
                  transition: 'all 0.2s ease',
                }}
              />
              <Chip
                label="🩺 Symptoms"
                size="small"
                onClick={() => !isLoading && setInputMessage('Help me understand symptoms')}
                sx={{
                  background: 'linear-gradient(135deg, #f093fb20 0%, #f5576c20 100%)',
                  border: '1px solid #f093fb40',
                  color: '#f5576c',
                  fontWeight: 500,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #f093fb30 0%, #f5576c30 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 8px rgba(240, 147, 251, 0.2)',
                  },
                  transition: 'all 0.2s ease',
                }}
              />
              <Chip
                label="📋 Procedures"
                size="small"
                onClick={() => !isLoading && setInputMessage('Explain medical procedures')}
                sx={{
                  background: 'linear-gradient(135deg, #4facfe20 0%, #00f2fe20 100%)',
                  border: '1px solid #4facfe40',
                  color: '#4facfe',
                  fontWeight: 500,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #4facfe30 0%, #00f2fe30 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 4px 8px rgba(79, 172, 254, 0.2)',
                  },
                  transition: 'all 0.2s ease',
                }}
              />
            </Box>
          </Box>
        </Paper>
      </Slide>
    </>
  );
};

export default FloatingChatBot;
