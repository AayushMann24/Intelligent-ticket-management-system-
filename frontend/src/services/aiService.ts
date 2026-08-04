import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export interface AIResponse {
  response: string;
}

export async function sendMessage(message: string): Promise<AIResponse> {
  const res = await API.post<AIResponse>("/ai/chat", {
    message,
  });

  return res.data;
}