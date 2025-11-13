import React, { useState, useRef, useEffect } from "react";
import { FiSend, FiImage, FiCamera, FiX } from "react-icons/fi";
import { BiLoaderAlt } from "react-icons/bi";
import ImageUploader from "./ImageUploader";
import CameraCapture from "./CameraCapture";
import VideoPlayer from "./VideoPlayer";

const ChatInterface = ({ onSendMessage, messages, isLoading }) => {
  const [inputText, setInputText] = useState("");
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendText = () => {
    if (inputText.trim() && !isLoading) {
      onSendMessage({ type: "text", content: inputText });
      setInputText("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  const handleImageUpload = (file) => {
    setShowImageUpload(false);
    onSendMessage({ type: "image", file });
  };

  const handleCameraCapture = (imageBlob) => {
    setShowCamera(false);
    onSendMessage({ type: "image", file: imageBlob });
  };

  return (
    <div className="relative flex h-screen max-w-6xl mx-auto flex-col gap-6 px-4 py-6 md:px-8 lg:px-12">
      <div className="absolute inset-0 -z-10 rounded-3xl border border-slate-800/60 bg-slate-950/60 shadow-[0_40px_120px_-60px_rgba(14,165,233,0.55)] backdrop-blur-2xl" />
      <div className="absolute inset-0 -z-20 rounded-[2.5rem] bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.24),transparent_60%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.18),transparent_55%)]" />
      {/* Header */}
      <div className="rounded-2xl border border-slate-700/60 bg-slate-900/70 px-6 py-5 shadow-xl shadow-slate-950/60 backdrop-blur-lg">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-3">
            <div className="flex items-center gap-3 sm:gap-4">
              <img
                src="/start-with-startup-logo-with-text.svg"
                alt="Start With Startup"
                className="h-10 w-auto flex-shrink-0 sm:h-12"
              />
              <h1 className="text-3xl font-semibold tracking-tight text-sky-100 sm:text-[2.5rem] sm:leading-[1.1]">
                Math Animation AI
              </h1>
            </div>
            <p className="text-sm text-slate-300 md:text-base">
              Upload problems, explore algebraic structures, and watch ideas
              unfold through motion.
            </p>
            <div className="flex flex-wrap items-center gap-3 text-[0.65rem] font-mono uppercase tracking-[0.35em] text-sky-300/80">
              <span>∑ SERIES</span>
              <span className="text-slate-500/70">•</span>
              <span>∞ LIMITS</span>
              <span className="text-slate-500/70">•</span>
              <span>∫ CALCULUS</span>
            </div>
          </div>
          <div className="flex items-center gap-5 rounded-2xl border border-slate-700/70 bg-slate-900/80 px-6 py-4 text-slate-200 shadow-inner shadow-slate-950/60">
            <div className="text-right">
              <p className="text-[0.65rem] uppercase tracking-[0.35em] text-slate-400">
                Session State
              </p>
              <p className="text-lg font-semibold text-sky-200">
                {isLoading ? "Processing…" : "Ready"}
              </p>
            </div>
            <div className="h-12 w-12 rounded-full bg-gradient-to-br from-sky-500 via-cyan-500 to-emerald-400 p-[2px] shadow-lg shadow-sky-900/50">
              <div
                className={`flex h-full w-full items-center justify-center rounded-full ${isLoading ? "bg-sky-950/90" : "bg-slate-950/95"}`}
              >
                <span className="text-xl text-sky-100">
                  {isLoading ? "∂" : "π"}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto rounded-2xl border border-slate-800/60 bg-slate-950/40 px-6 py-8 shadow-inner shadow-slate-950/60 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-10">
            <div className="space-y-3 text-center">
              <div className="text-6xl font-semibold text-sky-200">∫Σ∞</div>
              <h2 className="text-3xl font-semibold text-sky-100">
                Welcome to Math Animation AI
              </h2>
              <p className="text-base text-slate-300 md:text-lg">
                Transform handwritten expressions into cinematic Manim
                animations and explore the reasoning visually.
              </p>
            </div>
            <div className="grid w-full max-w-3xl grid-cols-1 gap-4 md:grid-cols-3">
              <div className="rounded-2xl border border-sky-500/30 bg-sky-900/30 p-5 shadow-lg shadow-sky-900/30 transition hover:border-sky-400/70 hover:shadow-sky-800/50">
                <div className="mb-3 text-3xl">📷</div>
                <h3 className="text-lg font-semibold text-sky-100">
                  Capture Concepts
                </h3>
                <p className="mt-2 text-sm text-sky-100/80">
                  Upload a photo or scan and let vision models extract
                  mathematical notation with high fidelity.
                </p>
              </div>
              <div className="rounded-2xl border border-emerald-500/30 bg-emerald-900/25 p-5 shadow-lg shadow-emerald-900/30 transition hover:border-emerald-400/70 hover:shadow-emerald-800/50">
                <div className="mb-3 text-3xl">🧠</div>
                <h3 className="text-lg font-semibold text-emerald-100">
                  Compose Scenes
                </h3>
                <p className="mt-2 text-sm text-emerald-100/80">
                  AI assembles Manim code, synchronising geometry, narration,
                  and highlights that mirror your problem.
                </p>
              </div>
              <div className="rounded-2xl border border-indigo-500/30 bg-indigo-900/25 p-5 shadow-lg shadow-indigo-900/30 transition hover:border-indigo-400/70 hover:shadow-indigo-800/50">
                <div className="mb-3 text-3xl">🎬</div>
                <h3 className="text-lg font-semibold text-indigo-100">
                  Render Proofs
                </h3>
                <p className="mt-2 text-sm text-indigo-100/80">
                  Preview the animation instantly, download the video, or
                  fine-tune the generated scene for deeper insight.
                </p>
              </div>
            </div>
            <div className="rounded-full border border-slate-700/60 bg-slate-900/60 px-6 py-3 font-mono text-xs uppercase tracking-[0.35em] text-slate-300">
              {"e^{iπ} + 1 = 0 — the poetry of mathematics in motion"}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {messages.map((message, index) => (
              <MessageBubble key={index} message={message} />
            ))}
            {isLoading && <LoadingMessage />}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="rounded-2xl border border-slate-800/60 bg-slate-950/60 px-4 py-4 shadow-xl shadow-slate-950/60">
        <div className="mx-auto flex max-w-4xl flex-col gap-3">
          <div className="flex items-center justify-between text-[0.65rem] font-mono uppercase tracking-[0.3em] text-slate-400">
            <span>Prompt → Code → Animation</span>
            <span>∑ • ∂ • ∞</span>
          </div>

          <div className="flex items-end gap-3">
            <div className="flex flex-1 items-end gap-2 rounded-2xl border border-slate-700/70 bg-slate-900/70 px-3 py-2 shadow-inner focus-within:border-sky-400/70 focus-within:ring-2 focus-within:ring-sky-500/40">
              <button
                onClick={() => setShowImageUpload(true)}
                disabled={isLoading}
                className="group rounded-xl border border-transparent bg-slate-800/70 p-2 text-slate-300 transition hover:border-sky-400/60 hover:text-sky-100 disabled:cursor-not-allowed disabled:opacity-50"
                title="Upload Image"
              >
                <FiImage className="text-xl transition group-hover:text-sky-300" />
              </button>
              <button
                onClick={() => setShowCamera(true)}
                disabled={isLoading}
                className="group rounded-xl border border-transparent bg-slate-800/70 p-2 text-slate-300 transition hover:border-emerald-400/60 hover:text-emerald-100 disabled:cursor-not-allowed disabled:opacity-50"
                title="Capture from Camera"
              >
                <FiCamera className="text-xl transition group-hover:text-emerald-300" />
              </button>
              <textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe the theorem, equation, or geometric construction you want to animate..."
                disabled={isLoading}
                rows="1"
                className="flex-1 bg-transparent px-2 py-2 text-base text-slate-100 placeholder:text-slate-500 focus:outline-none focus:ring-0"
                style={{ resize: "none" }}
              />
            </div>
            <button
              onClick={handleSendText}
              disabled={!inputText.trim() || isLoading}
              className="flex h-[52px] min-w-[52px] items-center justify-center rounded-2xl bg-gradient-to-r from-sky-500 via-cyan-500 to-emerald-400 px-4 py-3 font-semibold text-slate-950 shadow-lg shadow-sky-900/40 transition hover:from-sky-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
              title="Send"
            >
              {isLoading ? (
                <BiLoaderAlt className="text-xl text-slate-950/80" />
              ) : (
                <FiSend className="text-xl" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Modals */}
      {showImageUpload && (
        <Modal onClose={() => setShowImageUpload(false)}>
          <ImageUploader onUpload={handleImageUpload} />
        </Modal>
      )}

      {showCamera && (
        <Modal onClose={() => setShowCamera(false)}>
          <CameraCapture onCapture={handleCameraCapture} />
        </Modal>
      )}
    </div>
  );
};

// Message Bubble Component
const MessageBubble = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in`}
    >
      <div
        className={`max-w-[85%] rounded-3xl transition-all duration-300 ${
          isUser
            ? "message-user border border-sky-300/40 shadow-[0_20px_60px_-25px_rgba(14,165,233,0.7)]"
            : "message-assistant border border-slate-700/60 bg-slate-900/70 text-slate-100 shadow-[0_28px_80px_-35px_rgba(8,47,73,0.9)] backdrop-blur-xl"
        }`}
      >
        {/* User message */}
        {isUser && (
          <div className="space-y-3">
            {message.image && (
              <img
                src={message.image}
                alt="Uploaded"
                className="mb-3 max-w-xs rounded-2xl border border-sky-400/40 bg-slate-900/60 p-2 shadow-lg shadow-sky-900/40"
              />
            )}
            {message.text && (
              <p className="whitespace-pre-wrap text-base leading-relaxed tracking-wide">
                {message.text}
              </p>
            )}
          </div>
        )}

        {/* Assistant message */}
        {!isUser && (
          <div className="space-y-4">
            <div className="flex items-center gap-3 text-[0.65rem] uppercase tracking-[0.35em] text-sky-300/80">
              <span className="h-px flex-1 bg-sky-400/40" />
              <span>AI Tutor</span>
              <span className="h-px flex-1 bg-sky-400/40" />
            </div>

            {message.text && (
              <p className="whitespace-pre-wrap text-base leading-relaxed text-slate-100/90">
                {message.text}
              </p>
            )}

            {message.mathText && (
              <div className="rounded-2xl border border-sky-500/35 bg-sky-900/40 p-4 shadow-inner shadow-sky-900/50">
                <div className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">
                  Extracted Math
                </div>
                <div className="mt-2 font-mono text-sm leading-relaxed text-sky-100">
                  {message.mathText}
                </div>
              </div>
            )}

            {message.videoUrl && <VideoPlayer videoUrl={message.videoUrl} />}

            {message.error && (
              <div className="rounded-2xl border border-rose-500/40 bg-rose-950/50 p-4 shadow-inner shadow-rose-900/40">
                <div className="text-xs font-semibold uppercase tracking-[0.3em] text-rose-200">
                  Error
                </div>
                <div className="mt-2 text-sm text-rose-100/90">
                  {message.error}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Loading Message Component
const LoadingMessage = () => {
  return (
    <div className="flex justify-start animate-fade-in">
      <div className="message-assistant border border-slate-700/60 bg-slate-900/70 text-slate-200 shadow-[0_28px_80px_-35px_rgba(8,47,73,0.9)] backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <span className="font-mono text-xs uppercase tracking-[0.35em] text-sky-300">
            Computing
          </span>
          <div className="flex gap-1">
            <span className="loading-dot h-2 w-2 rounded-full bg-sky-400"></span>
            <span className="loading-dot h-2 w-2 rounded-full bg-sky-400"></span>
            <span className="loading-dot h-2 w-2 rounded-full bg-sky-400"></span>
          </div>
        </div>
      </div>
    </div>
  );
};

// Modal Component
const Modal = ({ children, onClose }) => {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-md">
      <div className="relative w-full max-h-[90vh] max-w-2xl overflow-y-auto rounded-3xl border border-slate-700/60 bg-slate-950/70 shadow-2xl shadow-slate-950/60 backdrop-blur-xl">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 rounded-full border border-slate-700/70 bg-slate-900/70 p-2 text-slate-200 transition hover:border-sky-400/60 hover:text-sky-200"
          title="Close"
        >
          <FiX className="text-xl" />
        </button>
        <div className="p-8">{children}</div>
      </div>
    </div>
  );
};

export default ChatInterface;
