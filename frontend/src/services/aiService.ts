import api from "./api";

export interface Citation {
    article_id: number;
    article_title: string;
    article_slug: string;
    chunk_id: number;
    chunk_index: number;
    content: string;
    score: number;
    source: "semantic" | "keyword" | "hybrid";
}

export interface AssistantResponse {
    answer: string;
    citations: Citation[];
    evidence_found: boolean;
    grounded: boolean;
    provider: string;
    model: string;
    usage?: {
        prompt_tokens?: number;
        completion_tokens?: number;
        total_tokens?: number;
    };
    metadata?: Record<string, unknown>;
}

export async function sendMessage(
    question: string,
    provider?: "gemini" | "ollama"
): Promise<AssistantResponse> {
    const res = await api.post<AssistantResponse>(
        "/assistant/ask",
        {
            question,
            provider,
        }
    );
    return res.data;
}

export async function checkAssistantHealth(): Promise<{
    status: string;
    service: string;
    ai_provider: string;
    ai_model: string;
}> {
    const res = await api.get("/assistant/health");
    return res.data;
}