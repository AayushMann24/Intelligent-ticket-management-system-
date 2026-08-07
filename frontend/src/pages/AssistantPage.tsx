import { useState, useRef, useEffect } from "react";

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

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const handleSend = async (text?: string) => {
    const currentMessage = text ?? message;

    if (!currentMessage.trim()) return;

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
          text: "Unable to contact AI Assistant.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const prompts = [
    "Summarize today's tickets",
    "Show high priority tickets",
    "Find unresolved issues",
    "Generate weekly report",
    "Suggest technician assignment",
    "Explain ticket trends",
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
              Powered by AI to help manage tickets faster.
            </p>

          </div>

          <button
            onClick={() => setMessages([])}
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
            onChange={(e) =>
              setMessage(e.target.value)
            }
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask the AI Assistant anything..."
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
              dark:border-slate-700
              dark:bg-slate-800
              dark:text-white
            "
          />

          <div className="mt-5 flex justify-end">

            <button
              onClick={() => handleSend()}
              disabled={loading}
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
              "
            >
              Send
            </button>

          </div>

        </div>

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

                <span
                  className="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                  style={{ animationDelay: "0.2s" }}
                ></span>

                <span
                  className="h-2 w-2 animate-bounce rounded-full bg-blue-500"
                  style={{ animationDelay: "0.4s" }}
                ></span>

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

              <div className="mb-5 text-6xl">
                🤖
              </div>

              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">
                Welcome to ITMS AI
              </h3>

              <p className="mt-3 text-slate-500 dark:text-slate-400">
                I can help you with:
              </p>

              <div className="mt-6 grid gap-3 md:grid-cols-2">

                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  📄 Summarize Tickets
                </div>

                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  🚨 High Priority Issues
                </div>

                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  📊 Generate Reports
                </div>

                <div className="rounded-xl border border-slate-200 p-4 dark:border-slate-700">
                  🤖 AI Suggestions
                </div>

              </div>

            </div>

          ) : (

            <div className="space-y-6">

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

                      {msg.sender === "assistant"
                        ? "🤖"
                        : "👤"}

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

                          {msg.sender === "assistant"
                            ? "ITMS AI"
                            : "You"}

                        </p>

                        {msg.sender === "assistant" && (

                          <button
                            onClick={() =>
                              navigator.clipboard.writeText(
                                msg.text
                              )
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