import api from "./api";
const API = api.create({
    baseURL: "http://127.0.0.1:8000",
});

export interface AIResponse {
    response: string;
}

export async function sendMessage(
    message: string
): Promise<AIResponse> {

    const res = await API.post<AIResponse>(
        "/assistant/chat",
        {
            message,
        }
    );

    return res.data;
}