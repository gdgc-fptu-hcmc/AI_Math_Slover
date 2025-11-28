import React, { useState, useRef, useEffect } from "react";
import { FiSend, FiImage, FiCamera, FiX, FiRefreshCw, FiEdit3, FiZap } from "react-icons/fi";
import { BiLoaderAlt } from "react-icons/bi";
import { motion, AnimatePresence } from "framer-motion";
import VideoPlayer from "./VideoPlayer";

const ChatInterface = ({ onSendMessage, messages, isLoading }) => {
  const [inputText, setInputText] = useState("");
  const [inputMode, setInputMode] = useState("text"); // 'text', 'image', 'camera'
  const [selectedMode, setSelectedMode] = useState("auto");
  const [dragActive, setDragActive] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [webcamActive, setWebcamActive] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);
  const webcamRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendText = () => {
    if (inputText.trim() && !isLoading) {
      onSendMessage({ type: "text", content: inputText, mode: selectedMode });
      setInputText("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputMode === "text" && inputText.trim()) {
        handleSendText();
      } else if (inputMode === "image" && selectedFile) {
        handleImageUpload();
      }
    }
  };

  const handleImageSelect = (file) => {
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      setInputMode("image");
    }
  };

  const handleImageUpload = () => {
    if (selectedFile) {
      onSendMessage({ type: "image", file: selectedFile, mode: selectedMode });
      clearImageInput();
    }
  };

  const clearImageInput = () => {
    setImagePreview(null);
    setSelectedFile(null);
    setInputMode("text");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleImageSelect(e.dataTransfer.files[0]);
    }
  };

  const startWebcam = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" } 
      });
      if (webcamRef.current) {
        webcamRef.current.srcObject = stream;
      }
      setWebcamActive(true);
      setInputMode("camera");
    } catch (err) {
      console.error("Error accessing webcam:", err);
      alert("Could not access camera. Please check permissions.");
    }
  };

  const captureFromWebcam = () => {
    if (webcamRef.current) {
      const canvas = document.createElement("canvas");
      canvas.width = webcamRef.current.videoWidth;
      canvas.height = webcamRef.current.videoHeight;
      canvas.getContext("2d").drawImage(webcamRef.current, 0, 0);
      
      canvas.toBlob((blob) => {
        const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
        handleImageSelect(file);
        stopWebcam();
      }, "image/jpeg");
    }
  };

  const stopWebcam = () => {
    if (webcamRef.current && webcamRef.current.srcObject) {
      webcamRef.current.srcObject.getTracks().forEach(track => track.stop());
      webcamRef.current.srcObject = null;
    }
    setWebcamActive(false);
    setInputMode("text");
  };

  const modes = [
    { id: "auto", label: "Auto", icon: "🤖", color: "cyan", desc: "Smart detection" },
    { id: "explain", label: "Explain", icon: "📚", color: "sky", desc: "Step-by-step" },
    { id: "answer", label: "Solve", icon: "⚡", color: "emerald", desc: "Quick answer" },
    { id: "animate", label: "Animate", icon: "🎬", color: "violet", desc: "Full video" },
  ];

  return (
    <div 
      className="relative flex h-screen max-w-7xl mx-auto flex-col gap-4 p-4 md:p-6"
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      <AnimatePresence>
        {dragActive && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/95 backdrop-blur-xl"
          >
            <div className="text-center">
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
                className="mb-6 text-8xl"
              >
                📊
              </motion.div>
              <h3 className="text-3xl font-bold text-sky-200 mb-2">Drop your math here</h3>
              <p className="text-slate-400">Release to analyze and animate</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Compact Header */}
      <motion.div 
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center justify-between rounded-3xl border border-slate-700/40 bg-slate-900/60 px-6 py-4 backdrop-blur-xl"
      >
        <div className="flex items-center gap-4">
          <img
            src="/start-with-startup-logo-with-text.svg"
            alt="Logo"
            className="h-10 w-auto"
          />
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-sky-300 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
              Math Animation AI
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">Transform equations into motion</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className={`px-3 py-1.5 rounded-full text-xs font-medium ${
            isLoading 
              ? "bg-amber-500/20 text-amber-300 border border-amber-500/30" 
              : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
          }`}>
            {isLoading ? "🔄 Processing" : "✓ Ready"}
          </div>
        </div>
      </motion.div>

      {/* Messages Area with smooth animations */}
      <div className="flex-1 overflow-y-auto rounded-2xl border border-slate-800/40 bg-slate-950/30 p-4 md:p-6 backdrop-blur-sm scrollbar-thin">
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="space-y-4">
              {messages.map((message, index) => (
                <MessageBubble 
                  key={`${message.timestamp}-${index}`} 
                  message={message}
                  onRetry={(msg) => {
                    // Implement retry logic
                    console.log("Retry:", msg);
                  }}
                />
              ))}
              {isLoading && <LoadingMessage />}
            </div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      {/* Mode Selector - More compact and intuitive */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-slate-900/40 border border-slate-700/30 backdrop-blur-sm"
      >
        <span className="text-xs text-slate-400 font-medium mr-2">Mode:</span>
        {modes.map((mode) => (
          <motion.button
            key={mode.id}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setSelectedMode(mode.id)}
            disabled={isLoading}
            className={`relative px-3 py-1.5 rounded-xl text-sm font-medium transition-all ${
              selectedMode === mode.id
                ? `bg-${mode.color}-500/20 text-${mode.color}-200 border border-${mode.color}-500/40 shadow-lg shadow-${mode.color}-500/20`
                : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
            } disabled:opacity-50 disabled:cursor-not-allowed`}
            title={mode.desc}
          >
            <span className="mr-1.5">{mode.icon}</span>
            {mode.label}
          </motion.button>
        ))}
      </motion.div>

      {/* Input Area - Fluid and adaptive */}
      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="rounded-2xl border border-slate-700/40 bg-slate-900/60 p-3 backdrop-blur-xl"
      >
        <AnimatePresence mode="wait">
          {inputMode === "camera" && webcamActive ? (
            <motion.div
              key="camera"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-3"
            >
              <video
                ref={webcamRef}
                autoPlay
                playsInline
                className="w-full rounded-xl bg-black"
                style={{ maxHeight: "300px" }}
              />
              <div className="flex gap-2">
                <button
                  onClick={captureFromWebcam}
                  className="flex-1 btn-primary py-3 rounded-xl"
                >
                  <FiCamera className="inline mr-2" />
                  Capture
                </button>
                <button
                  onClick={stopWebcam}
                  className="px-4 py-3 rounded-xl border border-slate-600 hover:bg-slate-800 transition"
                >
                  <FiX />
                </button>
              </div>
            </motion.div>
          ) : inputMode === "image" && imagePreview ? (
            <motion.div
              key="image-preview"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="space-y-3"
            >
              <div className="relative">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full rounded-xl max-h-64 object-contain bg-slate-950/50"
                />
                <button
                  onClick={clearImageInput}
                  className="absolute top-2 right-2 p-2 rounded-full bg-rose-500/90 hover:bg-rose-500 transition"
                >
                  <FiX />
                </button>
              </div>
              <button
                onClick={handleImageUpload}
                disabled={isLoading}
                className="w-full btn-primary py-3 rounded-xl disabled:opacity-50"
              >
                {isLoading ? (
                  <>
                    <BiLoaderAlt className="inline mr-2 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <FiZap className="inline mr-2" />
                    Generate Animation
                  </>
                )}
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="text-input"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-end gap-2"
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => e.target.files?.[0] && handleImageSelect(e.target.files[0])}
                accept="image/*"
                className="hidden"
              />
              
              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading}
                className="p-3 rounded-xl border border-slate-600/50 hover:border-sky-500/50 hover:bg-slate-800/50 transition disabled:opacity-50"
                title="Upload image"
              >
                <FiImage className="text-xl" />
              </button>
              
              <button
                onClick={startWebcam}
                disabled={isLoading}
                className="p-3 rounded-xl border border-slate-600/50 hover:border-emerald-500/50 hover:bg-slate-800/50 transition disabled:opacity-50"
                title="Use camera"
              >
                <FiCamera className="text-xl" />
              </button>
              
              <textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Describe your equation or drop an image..."
                disabled={isLoading}
                rows={1}
                className="flex-1 bg-slate-800/30 border border-slate-700/40 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-sky-500/50 focus:ring-2 focus:ring-sky-500/20 transition resize-none disabled:opacity-50"
              />
              
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSendText}
                disabled={!inputText.trim() || isLoading}
                className="p-3 rounded-xl bg-gradient-to-r from-sky-500 to-cyan-500 hover:from-sky-400 hover:to-cyan-400 disabled:opacity-40 disabled:cursor-not-allowed transition"
              >
                <FiSend className="text-xl" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

// Empty state with quick actions
const EmptyState = () => {
  const examples = [
    { icon: "∫", label: "Integrate x² dx", type: "calculus" },
    { icon: "Σ", label: "Sequence and series", type: "algebra" },
    { icon: "∂", label: "Partial derivatives", type: "calculus" },
    { icon: "∞", label: "Limits", type: "analysis" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center h-full min-h-[400px] text-center px-4"
    >
      <motion.div
        animate={{ rotate: [0, 5, -5, 0] }}
        transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
        className="text-7xl mb-6 font-bold bg-gradient-to-br from-sky-300 via-cyan-300 to-emerald-300 bg-clip-text text-transparent"
      >
        ∫ Σ ∞
      </motion.div>
      
      <h2 className="text-3xl font-bold text-slate-100 mb-3">
        Math in Motion
      </h2>
      <p className="text-slate-400 max-w-md mb-8">
        Upload equations, capture problems, or type questions—watch them come alive through beautiful animations
      </p>

      <div className="grid grid-cols-2 gap-3 w-full max-w-md">
        {examples.map((example, i) => (
          <motion.button
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            whileHover={{ scale: 1.05, y: -2 }}
            className="p-4 rounded-2xl border border-slate-700/50 bg-slate-800/30 hover:bg-slate-800/60 hover:border-sky-500/50 transition-all text-left group"
          >
            <div className="text-3xl mb-2 group-hover:scale-110 transition-transform">{example.icon}</div>
            <div className="text-sm font-medium text-slate-200">{example.label}</div>
            <div className="text-xs text-slate-500 mt-1">{example.type}</div>
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
};

// Improved message bubble with actions
const MessageBubble = ({ message, onRetry }) => {
  const isUser = message.role === "user";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[85%] rounded-2xl p-4 ${
          isUser
            ? "bg-gradient-to-br from-sky-500 to-cyan-500 text-slate-950"
            : "bg-slate-800/60 border border-slate-700/50 text-slate-100 backdrop-blur-sm"
        }`}
      >
        {!isUser && (
          <div className="flex items-center gap-2 mb-2 text-xs text-sky-300 font-medium">
            <span>🤖</span>
            <span>AI Tutor</span>
          </div>
        )}

        {message.image && (
          <img
            src={message.image}
            alt="Uploaded"
            className="mb-3 rounded-xl max-w-xs"
          />
        )}

        {message.text && (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.text}
          </p>
        )}

        {message.mathText && (
          <div className="mt-3 p-3 rounded-xl bg-slate-900/50 border border-slate-700/50">
            <div className="text-xs text-sky-300 font-medium mb-1">Extracted:</div>
            <div className="text-sm font-mono">{message.mathText}</div>
          </div>
        )}

        {message.videoUrl && <VideoPlayer videoUrl={message.videoUrl} />}

        {message.error && (
          <div className="mt-3 p-3 rounded-xl bg-rose-900/30 border border-rose-500/30">
            <div className="flex items-start gap-2">
              <span className="text-rose-400">⚠️</span>
              <div className="flex-1">
                <div className="text-xs text-rose-300 font-medium mb-1">Error:</div>
                <div className="text-xs text-rose-200/80">{message.error}</div>
              </div>
              <button
                onClick={() => onRetry(message)}
                className="p-1.5 rounded-lg hover:bg-rose-800/30 transition"
                title="Retry"
              >
                <FiRefreshCw className="text-sm" />
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

// Animated loading indicator
const LoadingMessage = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex justify-start"
    >
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-4 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
            className="text-sky-400"
          >
            ⚡
          </motion.div>
          <div className="flex gap-1">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ scale: [1, 1.5, 1], opacity: [0.3, 1, 0.3] }}
                transition={{
                  repeat: Infinity,
                  duration: 1,
                  delay: i * 0.15,
                }}
                className="w-2 h-2 rounded-full bg-sky-400"
              />
            ))}
          </div>
          <span className="text-xs text-slate-400">Thinking...</span>
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface;