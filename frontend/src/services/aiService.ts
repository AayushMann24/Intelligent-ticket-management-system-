import api from "./api";

export interface AIResponse {
    response: string;
}

export async function sendMessage(
    message: string
): Promise<AIResponse> {
    const res = await api.post<AIResponse>(
        "/assistant/chat",
        {
            message,
        }
    );
    return res.data;
}