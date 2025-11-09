import React, { useState } from 'react';
import { Grid, Paper } from '@mui/material';
import ChatHistory from '../components/ChatHistory';
import ChatWindow from '../components/ChatWindow'; // Assuming you have a ChatWindow component

const ChatPage: React.FC = () => {
  const [selectedConversationId, setSelectedConversationId] = useState<number | null>(null);

  const handleSelectConversation = (conversationId: number) => {
    setSelectedConversationId(conversationId);
  };

  return (
    <Grid container spacing={2} sx={{ height: 'calc(100vh - 64px)' }}>
      <Grid item xs={3}>
        <ChatHistory onSelectConversation={handleSelectConversation} />
      </Grid>
      <Grid item xs={9}>
        <Paper sx={{ height: '100%' }}>
          <ChatWindow conversationId={selectedConversationId} />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ChatPage;
