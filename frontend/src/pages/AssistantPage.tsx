import { useState, useRef, useEffect, useCallback } from "react";

import MainLayout from "../layouts/MainLayout";
import { sendMessage, type Citation } from "../services/aiService";

interface Message {
    id: number;
    sender: "user" | "assistant";
    text: string;
    citations?: Citation[];
    evidence_found?: boolean;
    grounded?: boolean;
    provider?: string;
    model?: string;
}

export default function AssistantPage() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [messageId, setMessageId] = useState(0);

    const chatEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = useCallback(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading, scrollToBottom]);

    const handleSend = async (text?: string) => {
        const currentMessage = text ?? message;

        if (!currentMessage.trim()) return;

        const userMsgId = messageId + 1;
        setMessageId(userMsgId);

        setMessages((prev) => [
            ...prev,
            {
                id: userMsgId,
                sender: "user",
                text: currentMessage,
            },
        ]);

        setMessage("");
        setLoading(true);
        setError(null);

        try {
            const result = await sendMessage(currentMessage);

            const assistantMsgId = messageId + 2;
            setMessageId(assistantMsgId);

            setMessages((prev) => [
                ...prev,
                {
                    id: assistantMsgId,
                    sender: "assistant",
                    text: result.answer,
                    citations: result.citations,
                    evidence_found: result.evidence_found,
                    grounded: result.grounded,
                    provider: result.provider,
                    model: result.model,
                },
            ]);
        } catch (err: unknown) {
            console.error(err);
            const errorMessage =
                err instanceof Error
                    ? err.message
                    : "Unable to contact AI Assistant. Please try again.";

            setError(errorMessage);

            const assistantMsgId = messageId + 2;
            setMessageId(assistantMsgId);

            setMessages((prev) => [
                ...prev,
                {
                    id: assistantMsgId,
                    sender: "assistant",
                    text: errorMessage,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const prompts = [
        "How do I reset my company password?",
        "My laptop cannot connect to Wi-Fi. What should I check?",
        "How do I troubleshoot a VPN connection?",
        "How can I resolve a printer issue?",
        "What should I do if my account is locked?",
        "How do I request software installation?",
        "How do I report a suspected phishing email?",
    ];

    return (
        <MainLayout>
            <div className="mx-auto max-w-6xl">
                {/* Header */}
                <div className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
                            🤖 AI Assistant
                        </h1>
                        <p className="mt-2 text-slate-500 dark:text-slate-400">
                            Grounded in ITMS Knowledge Base evidence.
                        </p>
                    </div>

                    <button
                        onClick={() => {
                            setMessages([]);
                            setMessageId(0);
                            setError(null);
                        }}
                        className="rounded-xl bg-red-600 px-5 py-3 font-semibold text-white transition hover:bg-red-700"
                    >
                        New Chat
                    </button>
                </div>

                {/* Quick Prompts */}
                <div className="mb-8">
                    <h2 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
                        Quick Prompts
                    </h2>

                    <div className="flex flex-wrap gap-3">
                        {prompts.map((prompt) => (
                            <button
                                key={prompt}
                                onClick={() => handleSend(prompt)}
                                disabled={loading}
                                className="
                                    rounded-full
                                    border
                                    border-slate-300
                                    bg-white
                                    px-4
                                    py-2
                                    text-sm
                                    font-medium
                                    text-slate-700
                                    transition
                                    hover:bg-blue-600
                                    hover:text-white
                                    disabled:opacity-50
                                    disabled:cursor-not-allowed
                                    dark:border-slate-700
                                    dark:bg-slate-900
                                    dark:text-white
                                "
                            >
                                {prompt}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Input */}
                <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <textarea
                        rows={5}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        placeholder="Ask the AI Assistant anything about IT support..."
                        disabled={loading}
                        className="
                            w-full
                            resize-none
                            rounded-xl
                            border
                            border-slate-300
                            bg-slate-50
                            p-4
                            text-slate-900
                            outline-none
                            transition
                            focus:border-blue-500
                            disabled:opacity-50
                            disabled:cursor-not-allowed
                            dark:border-slate-700
                            dark:bg-slate-800
                            dark:text-white
                        "
                    />

                    <div className="mt-5 flex justify-end">
                        <button
                            onClick={() => handleSend()}
                            disabled={loading || !message.trim()}
                            className="
                                rounded-xl
                                bg-blue-600
                                px-6
                                py-3
                                font-semibold
                                text-white
                                transition
                                hover:bg-blue-700
                                disabled:bg-slate-400
                                disabled:cursor-not-allowed
                            "
                        >
                            {loading ? "Thinking..." : "Send"}
                        </button>
                    </div>
                </div>

                {/* Error State */}
                {error && (
                    <div className="mt-4 rounded-xl border border-red-300 bg-red-50 p-4 text-red-700 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
                        <strong>Error:</strong> {error}
                        <button
                            onClick={() => handleSend(message)}
                            className="ml-4 underline hover:text-red-500"
                            disabled={loading}
                        >
                            Retry
                        </button>
                    </div>
                )}

                {/* Thinking Animation */}
                {loading && (
                    <div className="mt-6 flex items-center gap-4">
                        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-2xl text-white">
                            🤖
                        </div>

                        <div className="rounded-xl border border-slate-200 bg-white px-5 py-4 shadow-sm dark:border-slate-700 dark:bg-slate-900">
                            <p className="font-medium text-slate-900 dark:text-white">
                                AI Assistant
                            </p>

                            <div className="mt-2 flex gap-1">
                                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500"></span>
                                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500" style={{ animationDelay: "0.2s" }}></span>
                                <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500" style={{ animationDelay: "0.4s" }}></span>
                            </div>
                        </div>
                    </div>
                )}

                {/* Conversation */}
                <div className="mt-10">
                    <h2 className="mb-5 text-2xl font-bold text-slate-900 dark:text-white">
                        Conversation
                    </h2>

                    {messages.length === 0 ? (
                        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900">
                            <div className="mb-5 text-6xl">🤖</div>
                            <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
                                Welcome to ITMS AI Assistant
                            </h3>
                            <p className="mt-3 text-slate-500 dark:text-slate-400">
                                Ask me questions about IT procedures, troubleshooting, and policies.
                                I'll search the Knowledge Base and provide evidence-backed answers.
                            </p>
                            <div className="mt-6 grid gap-3 md:grid-cols-2">
                                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                                    🔐 Password Reset
                                </div>
                                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                                    📶 Wi-Fi Troubleshooting
                                </div>
                                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                                    🔒 VPN Issues
                                </div>
                                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                                    🖨️ Printer Problems
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`flex ${
                                        msg.sender === "user"
                                            ? "justify-end"
                                            : "justify-start"
                                    }`}
                                >
                                    <div
                                        className={`flex max-w-4xl gap-4 ${
                                            msg.sender === "user"
                                                ? "flex-row-reverse"
                                                : ""
                                        }`}
                                    >
                                        {/* Avatar */}
                                        <div
                                            className={`flex h-12 w-12 items-center justify-center rounded-full text-xl text-white ${
                                                msg.sender === "assistant"
                                                    ? "bg-blue-600"
                                                    : "bg-green-600"
                                            }`}
                                        >
                                            {msg.sender === "assistant" ? "🤖" : "👤"}
                                        </div>

                                        {/* Bubble */}
                                        <div
                                            className={`rounded-2xl p-5 shadow-md ${
                                                msg.sender === "assistant"
                                                    ? "border border-slate-200 bg-white text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                                                    : "bg-blue-600 text-white"
                                            }`}
                                        >
                                            <div className="mb-2 flex items-center justify-between">
                                                <p className="font-semibold">
                                                    {msg.sender === "assistant" ? "ITMS AI" : "You"}
                                                </p>

                                                {msg.sender === "assistant" && (
                                                    <button
                                                        onClick={() =>
                                                            navigator.clipboard.writeText(msg.text)
                                                        }
                                                        className="rounded-lg px-2 py-1 text-xs transition hover:bg-slate-200 dark:hover:bg-slate-700"
                                                    >
                                                        📋 Copy
                                                    </button>
                                                )}
                                            </div>

                                            <p className="whitespace-pre-wrap leading-7">
                                                {msg.text}
                                            </p>

                                            {/* Citations */}
                                            {msg.sender === "assistant" && msg.citations && msg.citations.length > 0 && (
                                                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                                                    <p className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">
                                                        📚 Sources ({msg.citations.length})
                                                    </p>
                                                    <div className="space-y-2">
                                                        {msg.citations.map((citation, idx) => (
                                                            <div
                                                                key={citation.chunk_id}
                                                                className="rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm dark:border-slate-700 dark:bg-slate-800"
                                                            >
                                                                <div className="flex items-center justify-between mb-1">
                                                                    <span className="font-medium text-slate-900 dark:text-white">
                                                                        [Evidence {idx + 1}] {citation.article_title}
                                                                    </span>
                                                                    <span className="text-xs text-slate-500 dark:text-slate-400">
                                                                        {citation.source} • score: {citation.score.toFixed(2)}
                                                                    </span>
                                                                </div>
                                                                <p className="text-slate-600 dark:text-slate-300 line-clamp-2">
                                                                    {citation.content.substring(0, 200)}
                                                                    {citation.content.length > 200 ? "..." : ""}
                                                                </p>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}

                                            {/* Evidence Status */}
                                            {msg.sender === "assistant" && (
                                                <div className="mt-3 flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                                                    <span className="flex items-center gap-1">
                                                        {msg.evidence_found ? (
                                                            <span className="text-green-600 dark:text-green-400">●</span>
                                                        ) : (
                                                            <span className="text-red-600 dark:text-red-400">●</span>
                                                        )}
                                                        Evidence: {msg.evidence_found ? "Found" : "Not Found"}
                                                    </span>
                                                    <span className="flex items-center gap-1">
                                                        {msg.grounded ? (
                                                            <span className="text-green-600 dark:text-green-400">●</span>
                                                        ) : (
                                                            <span className="text-yellow-600 dark:text-yellow-400">●</span>
                                                        )}
                                                        Grounded: {msg.grounded ? "Yes" : "No"}
                                                    </span>
                                                    {msg.provider && (
                                                        <span>
                                                            Provider: {msg.provider} ({msg.model})
                                                        </span>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))}

                            {/* Auto Scroll */}
                            <div ref={chatEndRef} />
                        </div>
                    )}
                </div>
            </div>
        </MainLayout>
    );
}