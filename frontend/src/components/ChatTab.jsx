import {
  useEffect,
  useRef,
  useState,
} from "react";
import ReactMarkdown from "react-markdown";
import {
  Send,
  Sparkles,
  Trash2,
} from "lucide-react";
import { chatWithDataset } from "../api";

const SUGGESTIONS = [
  "Summarize this dataset in a few sentences",
  "What trends or outliers stand out?",
  "Which columns are most correlated?",
];

export default function ChatTab({
  datasetId,
  datasetName,
  messages,
  onMessagesChange,
  onClearChat,
}) {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, sending]);

  async function send(question) {
    if (!question.trim() || sending) {
      return;
    }

    const cleanQuestion = question.trim();

    setError(null);

    const userMessage = {
      role: "user",
      content: cleanQuestion,
    };

    const previousMessages = messages || [];

    const nextMessages = [
      ...previousMessages,
      userMessage,
    ];

    /*
     * Immediately show and save the user's message.
     */
    onMessagesChange(nextMessages);

    setInput("");
    setSending(true);

    try {
      const answer = await chatWithDataset(
        datasetId,
        cleanQuestion,
        previousMessages
      );

      const finalMessages = [
        ...nextMessages,
        {
          role: "assistant",
          content: answer,
        },
      ];

      onMessagesChange(finalMessages);
    } catch (err) {
      setError(err.message);
    } finally {
      setSending(false);
    }
  }

  function handleClear() {
    if (!messages || messages.length === 0) {
      return;
    }

    const confirmed = window.confirm(
      "Clear this conversation?"
    );

    if (confirmed) {
      onClearChat();
      setError(null);
    }
  }

  return (
    <div className="chat-tab">
      {/* Chat Header */}
      <div className="chat-header">
        <div className="chat-header-title">
          <Sparkles
            size={18}
            strokeWidth={1.7}
          />

          <div className="chat-title-text">
            <strong>
              AI Data Analyst
            </strong>

            <span>
              Ask questions about{" "}
              {datasetName}
            </span>
          </div>
        </div>

        {messages &&
          messages.length > 0 && (
            <button
              type="button"
              className="chat-clear-btn"
              onClick={handleClear}
              title="Clear conversation"
            >
              <Trash2 size={15} />
              Clear chat
            </button>
          )}
      </div>

      {/* Chat Messages */}
      <div className="chat-scroll">
        {(!messages ||
          messages.length === 0) && (
          <div className="chat-empty">
            <Sparkles
              size={22}
              strokeWidth={1.5}
            />

            <p>
              Ask anything about "
              {datasetName}" — trends,
              summaries, comparisons.
            </p>

            <div className="suggestion-row">
              {SUGGESTIONS.map(
                (suggestion) => (
                  <button
                    key={suggestion}
                    className="suggestion-chip"
                    onClick={() =>
                      send(suggestion)
                    }
                    disabled={sending}
                  >
                    {suggestion}
                  </button>
                )
              )}
            </div>
          </div>
        )}

        {messages &&
          messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`chat-bubble chat-bubble-${message.role}`}
            >
              <span className="chat-role">
                {message.role === "user"
                  ? "You"
                  : "Analyst"}
              </span>

              <div className="chat-content">
                <ReactMarkdown>
                  {message.content}
                </ReactMarkdown>
              </div>
            </div>
          ))}

        {sending && (
          <div className="chat-bubble chat-bubble-assistant">
            <span className="chat-role">
              Analyst
            </span>

            <div className="chat-content chat-typing">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        {error && (
          <p className="upload-error">
            {error}
          </p>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Chat Input */}
      <form
        className="chat-input-row"
        onSubmit={(event) => {
          event.preventDefault();
          send(input);
        }}
      >
        <input
          type="text"
          placeholder="Ask a question about this dataset…"
          value={input}
          onChange={(event) =>
            setInput(event.target.value)
          }
          disabled={sending}
        />

        <button
          type="submit"
          disabled={
            sending || !input.trim()
          }
          className="send-btn"
        >
          <Send
            size={16}
            strokeWidth={1.75}
          />
        </button>
      </form>
    </div>
  );
}