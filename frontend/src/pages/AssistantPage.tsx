import { useState } from "react";

import MainLayout from "../layouts/MainLayout";
import { sendMessage } from "../services/aiService";

interface Message {
    sender: "user" | "assistant";
    text: string;
}

export default function AssistantPage() {
    const [message, setMessage] = useState("");
    const [messages, setMessages] = useState<Message[]>([]);
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!message.trim()) return;

        const currentMessage = message;

        // Show user message immediately
        setMessages((prev) => [
            ...prev,
            {
                sender: "user",
                text: currentMessage,
            },
        ]);

        setMessage("");
        setLoading(true);

        try {
            const result = await sendMessage(currentMessage);

            setMessages((prev) => [
                ...prev,
                {
                    sender: "assistant",
                    text: result.response,
                },
            ]);
        } catch (error) {
            console.error(error);

            setMessages((prev) => [
                ...prev,
                {
                    sender: "assistant",
                    text: "Failed to contact AI Assistant.",
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <MainLayout>
            <div className="max-w-5xl mx-auto">

                {/* Header */}

                <div className="flex justify-between items-center mb-6">

                    <h1 className="text-3xl font-bold text-white">
                        AI Assistant
                    </h1>

                    <button
                        onClick={() => setMessages([])}
                        className="bg-red-500 hover:bg-red-600 text-white px-5 py-2 rounded-lg"
                    >
                        New Chat
                    </button>

                </div>

                {/* Input */}

                <div className="bg-slate-900 rounded-xl shadow p-6">

                    <textarea
                        rows={5}
                        value={message}
                        onChange={(e) =>
                            setMessage(e.target.value)
                        }
                        placeholder="Ask the AI Assistant anything..."
                        className="w-full rounded-lg border border-gray-600 bg-slate-950 text-white p-4 resize-none"
                    />

                    <button
                        onClick={handleSend}
                        disabled={loading}
                        className="mt-4 px-6 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 disabled:bg-gray-500"
                    >
                        Send
                    </button>

                </div>

                {/* Thinking Animation */}

                {loading && (

                    <div className="flex items-center gap-3 mt-6">

                        <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white text-xl">

                            🤖

                        </div>

                        <div className="bg-gray-200 rounded-xl px-5 py-3 animate-pulse">

                            AI is thinking...

                        </div>

                    </div>

                )}

                {/* Chat */}

                <div className="mt-8 space-y-5">

                    {messages.map((msg, index) => (

                        <div
                            key={index}
                            className={`flex ${
                                msg.sender === "user"
                                    ? "justify-end"
                                    : "justify-start"
                            }`}
                        >

                            <div
                                className={`flex gap-3 max-w-3xl ${
                                    msg.sender === "user"
                                        ? "flex-row-reverse"
                                        : ""
                                }`}
                            >

                                {/* Avatar */}

                                <div
                                    className={`w-10 h-10 rounded-full flex items-center justify-center text-white text-lg ${
                                        msg.sender === "assistant"
                                            ? "bg-blue-600"
                                            : "bg-green-600"
                                    }`}
                                >

                                    {msg.sender === "assistant"
                                        ? "🤖"
                                        : "👤"}

                                </div>

                                {/* Bubble */}

                                <div
                                    className={`rounded-xl p-4 whitespace-pre-wrap ${
                                        msg.sender === "assistant"
                                            ? "bg-white text-gray-800"
                                            : "bg-blue-600 text-white"
                                    }`}
                                >

                                    {msg.text}

                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            </div>
        </MainLayout>
    );
}