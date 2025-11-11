import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { sendChatMessage, getConversationMessages } from '../services/api';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
}

interface ChatWindowProps {
  conversationId: number | null;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (conversationId) {
      loadChatHistory(conversationId);
    } else {
      setMessages([]);
    }
  }, [conversationId]);

  const loadChatHistory = async (convId: number) => {
    try {
      setLoading(true);
      const conversation = await getConversationMessages(convId);
      setMessages(conversation.messages || []);
      setError(null);
    } catch (err) {
      console.error('Failed to load chat history:', err);
      setError('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);
    setError(null);

    try {
      const response = await sendChatMessage(inputMessage, conversationId || undefined);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message?.content || 'No response from assistant',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error('Failed to send message:', err);
      const errorMsg = err?.response?.data?.detail || 'Failed to send message. Please try again.';
      setError(errorMsg);
      
      // Optionally add error message to chat
      const errorMessage: ChatMessage = {
        role: 'system',
        content: `Error: ${errorMsg}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        p: 2,
      }}
    >
      {/* Header */}
      <Typography variant="h6" gutterBottom>
        {conversationId ? `Conversation #${conversationId}` : 'AI Medical Assistant'}
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: 'auto',
          mb: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {messages.length === 0 && !loading && (
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Start a conversation with the AI Medical Assistant
            </Typography>
          </Box>
        )}

        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <Paper
              sx={{
                p: 2,
                maxWidth: '70%',
                backgroundColor:
                  msg.role === 'user'
                    ? 'primary.main'
                    : msg.role === 'system'
                    ? 'error.light'
                    : 'grey.100',
                color:
                  msg.role === 'user'
                    ? 'primary.contrastText'
                    : msg.role === 'system'
                    ? 'error.contrastText'
                    : 'text.primary',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {msg.content}
              </Typography>
              {msg.timestamp && (
                <Typography variant="caption" sx={{ display: 'block', mt: 0.5, opacity: 0.7 }}>
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Typography>
              )}
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start' }}>
            <Paper sx={{ p: 2, backgroundColor: 'grey.100' }}>
              <CircularProgress size={20} />
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          placeholder="Type your message..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={loading}
          variant="outlined"
        />
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          onClick={handleSendMessage}
          disabled={loading || !inputMessage.trim()}
          sx={{ minWidth: 100 }}
        >
          Send
        </Button>
      </Box>
    </Box>
  );
};

export default ChatWindow;
