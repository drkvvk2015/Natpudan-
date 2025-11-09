import React, { useEffect, useState } from 'react';
import { List, ListItem, ListItemText, Typography, CircularProgress, Box, Paper } from '@mui/material';
import { getConversations, Conversation } from '../services/api';

interface ChatHistoryProps {
  onSelectConversation: (conversationId: number) => void;
}

const ChatHistory: React.FC<ChatHistoryProps> = ({ onSelectConversation }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const data = await getConversations();
        setConversations(data);
      } catch (err) {
        setError('Failed to load chat history.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, []);

  if (loading) {
    return <CircularProgress />;
  }

  if (error) {
    return <Typography color="error">{error}</Typography>;
  }

  return (
    <Paper elevation={2} sx={{ height: '100%', overflowY: 'auto' }}>
      <Box p={2}>
        <Typography variant="h6">Chat History</Typography>
      </Box>
      <List>
        {conversations.map((convo) => (
          <ListItem button key={convo.id} onClick={() => onSelectConversation(convo.id)}>
            <ListItemText primary={convo.title} secondary={new Date(convo.created_at).toLocaleString()} />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default ChatHistory;
