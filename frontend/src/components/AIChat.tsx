import { useState } from "react";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  TextField,
  Typography,
} from "@mui/material";

import SmartToyIcon from "@mui/icons-material/SmartToy";
import PersonIcon from "@mui/icons-material/Person";

import { sendMessage } from "../services/aiService";

interface Message {
  sender: "user" | "ai";
  text: string;
}

export default function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      sender: "user",
      text: input,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await sendMessage(userMessage.text);

      const aiMessage: Message = {
        sender: "ai",
        text: response.response,
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (error: any) {
      console.error(error);

      setMessages((prev) => [
        ...prev,
        {
          sender: "ai",
          text:
            error?.response?.data?.detail ||
            error?.message ||
            "Unable to contact AI server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={5}
      sx={{
        width: "75%",
        margin: "40px auto",
        padding: 3,
        borderRadius: 4,
      }}
    >
      <Typography
        variant="h4"
        align="center"
        gutterBottom
      >
        🤖 ITMS AI Assistant
      </Typography>

      <Box
        sx={{
          height: 500,
          overflowY: "auto",
          bgcolor: "#f5f5f5",
          borderRadius: 2,
          p: 2,
          mb: 2,
        }}
      >
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              display: "flex",
              justifyContent:
                msg.sender === "user"
                  ? "flex-end"
                  : "flex-start",
              mb: 2,
            }}
          >
            <Paper
              elevation={2}
              sx={{
                p: 2,
                maxWidth: "70%",
                bgcolor:
                  msg.sender === "user"
                    ? "#1976d2"
                    : "#ffffff",
                color:
                  msg.sender === "user"
                    ? "#fff"
                    : "#000",
                borderRadius: 3,
              }}
            >
              <Typography
                variant="subtitle2"
                sx={{
                  fontWeight: "bold",
                  display: "flex",
                  alignItems: "center",
                  gap: 1,
                  mb: 1,
                }}
              >
                {msg.sender === "user" ? (
                  <>
                    <PersonIcon fontSize="small" />
                    You
                  </>
                ) : (
                  <>
                    <SmartToyIcon fontSize="small" />
                    AI Assistant
                  </>
                )}
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  whiteSpace: "pre-wrap",
                  wordBreak: "break-word",
                }}
              >
                {msg.text}
              </Typography>
            </Paper>
          </Box>
        ))}

        {loading && (
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              mt: 2,
            }}
          >
            <CircularProgress size={30} />

            <Typography
              variant="body2"
              sx={{ mt: 1 }}
            >
              AI is thinking...
            </Typography>
          </Box>
        )}
      </Box>

      <Box
        sx={{
          display: "flex",
          gap: 2,
        }}
      >
        <TextField
          fullWidth
          placeholder="Ask anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              handleSend();
            }
          }}
        />

        <Button
          variant="contained"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </Button>
      </Box>
    </Paper>
  );
}