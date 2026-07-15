"use client";

import { useEffect, useState, useRef } from "react";
import { ChatBubbleLeftRightIcon, ArrowRightIcon, TrashIcon, SparklesIcon } from "@heroicons/react/24/outline";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatPanel({ repoId }: { repoId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am the **Architect's Memory**. Ask me anything about the history, evolution, or architectural dependencies of this codebase.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [focusFile, setFocusFile] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested questions based on repo
  const suggestions = [
    { text: "What is the history of BillingService?", file: "src/services/billing_service.py" },
    { text: "Why did we split auth/oauth.py?", file: "src/auth/oauth.py" },
    { text: "Are there any bug patterns in user.py?", file: "src/models/user.py" },
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const clearChat = () => {
    setMessages([
      {
        role: "assistant",
        content: "Hello! I am the **Architect's Memory**. Ask me anything about the history, evolution, or architectural dependencies of this codebase.",
      },
    ]);
    setSessionId(null);
    setFocusFile(null);
  };

  const handleSend = async (textToSend: string) => {
    if (!textToSend.trim() || loading) return;

    const userMessage: Message = { role: "user", content: textToSend };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    // Add placeholder assistant message for streaming
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    try {
      const response = await fetch(`http://localhost:8001/repos/${repoId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: textToSend,
          file_path: focusFile || undefined,
          session_id: sessionId || undefined,
          stream: true,
        }),
      });

      if (!response.ok) throw new Error("Chat request failed");
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error("Stream reader not supported");

      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        
        // Normalize carriage returns to standard newlines
        const normalized = buffer.replace(/\r\n/g, "\n");
        // SSE streams return blocks separated by double newlines
        const lines = normalized.split("\n\n");
        // Keep the last partial block in buffer
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim()) continue;
          
          const eventMatch = line.match(/^event:\s*(\w+)/m);
          const dataMatch = line.match(/^data:\s*(.*)/m);

          if (eventMatch && dataMatch) {
            const event = eventMatch[1];
            const dataStr = dataMatch[1].trim();

            try {
              const data = JSON.parse(dataStr);
              if (event === "session") {
                setSessionId(data.session_id);
              } else if (event === "token") {
                setMessages((prev) => {
                  const updated = [...prev];
                  const lastIndex = updated.length - 1;
                  if (lastIndex >= 0 && updated[lastIndex].role === "assistant") {
                    updated[lastIndex] = {
                      ...updated[lastIndex],
                      content: updated[lastIndex].content + data.token,
                    };
                  }
                  return updated;
                });
              }
            } catch (err) {
              console.error("Failed to parse SSE line JSON:", err, "Line content:", line);
            }
          }
        }
      }
    } catch (err: any) {
      setMessages((prev) => {
        const updated = [...prev];
        const lastIndex = updated.length - 1;
        if (lastIndex >= 0 && updated[lastIndex].role === "assistant") {
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: `Error: ${err.message || "Failed to retrieve stream from AI server"}`,
          };
        }
        return updated;
      });
    } finally {
      setLoading(false);
      setMessages((prev) => {
        const updated = [...prev];
        const lastIndex = updated.length - 1;
        if (lastIndex >= 0 && updated[lastIndex].role === "assistant" && updated[lastIndex].content === "") {
          updated[lastIndex] = {
            ...updated[lastIndex],
            content: "Error: Stream disconnected without sending any tokens. Please refresh and try again.",
          };
        }
        return updated;
      });
    }
  };

  return (
    <div className="chat-panel-wrapper">
      <div className="panel-header-controls">
        <div className="title">
          <ChatBubbleLeftRightIcon className="w-5 h-5 text-indigo-400" />
          <span>Architect's Memory Chatbot</span>
        </div>
        <button onClick={clearChat} className="btn-refresh" title="Clear Chat">
          <TrashIcon className="w-4 h-4" />
        </button>
      </div>

      <div className="chat-workspace-grid">
        {/* Messages Trail */}
        <div className="chat-trail-area">
          <div className="messages-scroller">
            {messages.map((msg, index) => (
              <div key={index} className={`message-bubble-row ${msg.role}`}>
                <div className="avatar-icon">
                  {msg.role === "assistant" ? "⌁" : "U"}
                </div>
                <div className="message-content">
                  {msg.role === "assistant" ? (
                    msg.content === "" ? (
                      <div className="typing-indicator">
                        <span /><span /><span />
                      </div>
                    ) : (
                    <div className="ai-rich-text markdown-render">
                      {msg.content.split("\n").map((line, idx) => {
                        // Check #### before ### to avoid prefix collision
                        if (line.startsWith("####")) {
                          return <h5 key={idx} className="md-h5">{line.replace(/^####\s*/, "")}</h5>;
                        }
                        if (line.startsWith("###")) {
                          return <h4 key={idx} className="md-h4">{line.replace(/^###\s*/, "")}</h4>;
                        }
                        if (line.startsWith("##")) {
                          return <h3 key={idx} className="md-h3">{line.replace(/^##\s*/, "")}</h3>;
                        }
                        if (line.startsWith("**") && line.endsWith("**")) {
                          return <strong key={idx} className="md-bold">{line.replace(/\*\*/g, "")}</strong>;
                        }
                        if (line.startsWith("- ") || line.startsWith("* ")) {
                          return <li key={idx} className="md-li">{line.substring(2)}</li>;
                        }
                        if (line.trim() === "") {
                          return <div key={idx} className="h-2" />;
                        }
                        return <p key={idx} className="md-p">{line}</p>;
                      })}
                    </div>
                    )
                  ) : (
                    <p className="user-text">{msg.content}</p>
                  )}
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Control Box */}
          <div className="chat-input-bar">
            {focusFile && (
              <div className="focus-file-badge">
                <span>Focusing File: <strong>{focusFile}</strong></span>
                <button onClick={() => setFocusFile(null)} className="btn-close">×</button>
              </div>
            )}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSend(input);
              }}
              className="input-row"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about architectural choices, complexity modules..."
                className="input-text-field"
                disabled={loading}
              />
              <button type="submit" disabled={loading || !input.trim()} className="btn-submit">
                <ArrowRightIcon className="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>

        {/* Focus Sidebar Suggestions */}
        <div className="chat-suggestions-sidebar">
          <h3>Architectural Suggestions</h3>
          <p className="sidebar-desc">Select a query to investigate code history:</p>
          <div className="suggestions-list">
            {suggestions.map((sug, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setFocusFile(sug.file);
                  handleSend(sug.text);
                }}
                disabled={loading}
                className="btn-suggestion-card"
              >
                <SparklesIcon className="w-4 h-4 text-purple-400" />
                <div className="text-left">
                  <span>{sug.text}</span>
                  <span className="file-badge">{sug.file.split("/").pop()}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
