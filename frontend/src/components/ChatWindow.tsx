import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField as DialogTextField,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import SendIcon from "@mui/icons-material/Send";
import MedicationIcon from "@mui/icons-material/Medication";
import SearchIcon from "@mui/icons-material/Search";
import {
  sendChatMessage,
  getConversationMessages,
  checkDrugInteractions,
  searchDrug,
} from "../services/api";

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

interface ChatWindowProps {
  conversationId: number | null;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [showDrugInteractionDialog, setShowDrugInteractionDialog] =
    useState(false);
  const [showICDDialog, setShowICDDialog] = useState(false);
  const [drugList, setDrugList] = useState<string[]>(["", ""]);
  const [icdQuery, setIcdQuery] = useState("");
  const [drugCheckResults, setDrugCheckResults] = useState<any>(null);
  const [icdResults, setIcdResults] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
      console.error("Failed to load chat history:", err);
      setError("Failed to load chat history");
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setLoading(true);
    setError(null);

    try {
      console.log("[Chat] Sending message:", inputMessage);
      console.log("[Chat] Conversation ID:", conversationId);

      const response = await sendChatMessage(
        inputMessage,
        conversationId || undefined
      );

      console.log("[Chat] Response received:", response);

      // Check if response has message content
      if (!response || !response.message) {
        throw new Error("Empty response from server");
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.message?.content || "No response from assistant",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err: any) {
      console.error("[Chat] Error details:", {
        message: err?.message,
        response: err?.response?.data,
        status: err?.response?.status,
        fullError: err,
      });

      let errorMsg = "Failed to send message. Please check:";

      if (err?.response?.status === 401) {
        errorMsg = "Authentication failed. Please log in again.";
      } else if (err?.response?.status === 500) {
        errorMsg =
          "Server error. Please check if the backend is running and OpenAI API key is configured.";
      } else if (err?.message?.includes("Network Error")) {
        errorMsg =
          "Network error. Please check if the backend is running on http://localhost:8000";
      } else if (err?.response?.data?.detail) {
        errorMsg = err.response.data.detail;
      }

      setError(errorMsg);

      // Add detailed error message to chat
      const errorMessage: ChatMessage = {
        role: "system",
        content: `[ERROR] ${errorMsg}\n\nDebug Info:\n- Status: ${
          err?.response?.status || "N/A"
        }\n- Endpoint: /api/chat/message\n- Time: ${new Date().toLocaleString()}`,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleCheckDrugInteraction = async () => {
    const validDrugs = drugList.filter((d) => d.trim());
    if (validDrugs.length < 2) {
      setError("Please enter at least 2 drugs to check interactions");
      return;
    }

    try {
      setLoading(true);
      const response = await checkDrugInteractions({ drugs: validDrugs });
      setDrugCheckResults(response);

      // Format and add to chat
      const interactionSummary =
        response.interactions?.length > 0
          ? `Found ${
              response.interactions.length
            } interaction(s):\n${response.interactions
              .map(
                (i: any) => `- ${i.drug1} + ${i.drug2}: ${i.severity} severity`
              )
              .join("\n")}`
          : "No significant interactions found";

      const systemMessage: ChatMessage = {
        role: "system",
        content: `💊 Drug Interaction Check:\n${interactionSummary}`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, systemMessage]);
      setShowDrugInteractionDialog(false);
      setDrugList(["", ""]);
      setError(null);
    } catch (err: any) {
      setError(`Failed to check drug interactions: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchICD = async () => {
    if (!icdQuery.trim()) {
      setError("Please enter a diagnosis or symptom");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(
        `/api/medical/icd/search?query=${encodeURIComponent(
          icdQuery
        )}&max_results=5`
      );
      const data = await response.json();
      setIcdResults(Array.isArray(data) ? data : []);

      const icdSummary =
        data.length > 0
          ? data
              .slice(0, 5)
              .map((item: any) => `- ${item.code}: ${item.description}`)
              .join("\n")
          : "No ICD-10 codes found";

      const systemMessage: ChatMessage = {
        role: "system",
        content: `📋 ICD-10 Code Search for "${icdQuery}":\n${icdSummary}`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, systemMessage]);
      setShowICDDialog(false);
      setIcdQuery("");
      setError(null);
    } catch (err: any) {
      setError(`Failed to search ICD codes: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        p: 2,
      }}
    >
      {/* Header */}
      <Typography variant="h6" gutterBottom>
        {conversationId
          ? `Conversation #${conversationId}`
          : "Medical AI Chat Assistant"}
      </Typography>
      {!conversationId && messages.length === 0 && (
        <Paper variant="outlined" sx={{ p: 2, mb: 2, bgcolor: "grey.50" }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            This assistant provides evidence-based medical information. It can
            synthesize content from the built-in knowledge base and cite
            sources. It does not replace professional judgment.
          </Typography>
          <Typography variant="caption" color="text.secondary">
            For emergencies, call local emergency services immediately.
          </Typography>
          <Stack direction="row" spacing={1} sx={{ mt: 1, flexWrap: "wrap" }}>
            <Chip
              label="Define fever"
              onClick={() => setInputMessage("Define fever")}
              size="small"
            />
            <Chip
              label="Treatment for community-acquired pneumonia"
              onClick={() =>
                setInputMessage(
                  "What is the treatment for community-acquired pneumonia in adults?"
                )
              }
              size="small"
            />
            <Chip
              label="Drug interaction: warfarin + amoxicillin"
              onClick={() =>
                setInputMessage(
                  "Check interaction between warfarin and amoxicillin"
                )
              }
              size="small"
            />
            <Chip
              label="Causes of chest pain"
              onClick={() =>
                setInputMessage(
                  "List common causes of chest pain and red flags"
                )
              }
              size="small"
            />
          </Stack>
        </Paper>
      )}

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflowY: "auto",
          mb: 2,
          display: "flex",
          flexDirection: "column",
          gap: 2,
        }}
      >
        {messages.length === 0 && !loading && conversationId && (
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Start a conversation with the Medical AI Assistant
            </Typography>
          </Box>
        )}

        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
            }}
          >
            <Paper
              sx={{
                p: 2,
                maxWidth: "70%",
                backgroundColor:
                  msg.role === "user"
                    ? "primary.main"
                    : msg.role === "system"
                    ? "error.light"
                    : "grey.100",
                color:
                  msg.role === "user"
                    ? "primary.contrastText"
                    : msg.role === "system"
                    ? "error.contrastText"
                    : "text.primary",
              }}
            >
              {msg.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {msg.content}
                </ReactMarkdown>
              ) : (
                <Typography variant="body1" sx={{ whiteSpace: "pre-wrap" }}>
                  {msg.content}
                </Typography>
              )}
              {msg.timestamp && (
                <Typography
                  variant="caption"
                  sx={{ display: "block", mt: 0.5, opacity: 0.7 }}
                >
                  {new Date(msg.timestamp).toLocaleTimeString()}
                </Typography>
              )}
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box sx={{ display: "flex", justifyContent: "flex-start" }}>
            <Paper sx={{ p: 2, backgroundColor: "grey.100" }}>
              <CircularProgress size={20} />
            </Paper>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Box sx={{ display: "flex", gap: 1, flexDirection: "column" }}>
        {/* Quick action buttons */}
        <Stack direction="row" spacing={1} sx={{ flexWrap: "wrap" }}>
          <Button
            size="small"
            startIcon={<MedicationIcon />}
            variant="outlined"
            onClick={() => setShowDrugInteractionDialog(true)}
            disabled={loading}
          >
            Check Drug Interaction
          </Button>
          <Button
            size="small"
            startIcon={<SearchIcon />}
            variant="outlined"
            onClick={() => setShowICDDialog(true)}
            disabled={loading}
          >
            Search ICD-10 Codes
          </Button>
        </Stack>

        {/* Message input */}
        <Box sx={{ display: "flex", gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your medical question..."
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

      {/* Drug Interaction Dialog */}
      <Dialog
        open={showDrugInteractionDialog}
        onClose={() => setShowDrugInteractionDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Check Drug Interactions</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
            {drugList.map((drug, idx) => (
              <TextField
                key={idx}
                label={`Drug ${idx + 1}`}
                value={drug}
                onChange={(e) => {
                  const newList = [...drugList];
                  newList[idx] = e.target.value;
                  setDrugList(newList);
                }}
                placeholder="e.g., Warfarin, Amoxicillin"
                fullWidth
              />
            ))}
            <Button
              variant="outlined"
              onClick={() => setDrugList([...drugList, ""])}
            >
              Add Drug
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDrugInteractionDialog(false)}>
            Cancel
          </Button>
          <Button
            onClick={handleCheckDrugInteraction}
            variant="contained"
            disabled={loading}
          >
            Check
          </Button>
        </DialogActions>
      </Dialog>

      {/* ICD-10 Search Dialog */}
      <Dialog
        open={showICDDialog}
        onClose={() => setShowICDDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Search ICD-10 Codes</DialogTitle>
        <DialogContent>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 2 }}>
            <TextField
              label="Diagnosis or Symptom"
              value={icdQuery}
              onChange={(e) => setIcdQuery(e.target.value)}
              placeholder="e.g., Diabetes, Hypertension, Fever"
              fullWidth
              multiline
              maxRows={3}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowICDDialog(false)}>Cancel</Button>
          <Button
            onClick={handleSearchICD}
            variant="contained"
            disabled={loading}
          >
            Search
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ChatWindow;
