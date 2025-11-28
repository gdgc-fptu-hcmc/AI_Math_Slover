import React, { useState, useEffect, useCallback } from "react";
import { Toaster, toast } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
import ChatInterface from "./components/ChatInterface";
import { animationAPI } from "./services/api";

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("checking");

  useEffect(() => {
    // Check backend connection
    checkConnection();
    
    // Load welcome message
    const welcomeMessage = {
      role: "assistant",
      text: "👋 Ready to animate math! Upload images, capture equations, or type your problems—I'll transform them into visual explanations.",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('/api/animation/health');
      if (response.ok) {
        setConnectionStatus("connected");
      } else {
        setConnectionStatus("error");
        toast.error("Backend connection issue. Please refresh.", {
          id: "connection-error",
          duration: 5000,
        });
      }
    } catch (error) {
      setConnectionStatus("error");
      toast.error("Cannot connect to backend. Is the server running?", {
        id: "connection-error",
        duration: 5000,
      });
    }
  };

  const addMessage = useCallback((message) => {
    setMessages((prev) => [...prev, { ...message, timestamp: new Date() }]);
  }, []);

  const handleSendMessage = async (data) => {
    // Dismiss any existing toasts
    toast.dismiss();

    try {
      setIsLoading(true);
      const mode = data.mode || "auto";

      // Add user message with optimistic UI
      if (data.type === "text") {
        addMessage({
          role: "user",
          text: data.content,
        });
      } else if (data.type === "image") {
        const reader = new FileReader();
        reader.onloadend = () => {
          addMessage({
            role: "user",
            image: reader.result,
          });
        };
        reader.readAsDataURL(data.file);
      }

      // Show loading state with progress
      const loadingToastId = toast.loading(
        getLoadingMessage(mode),
        {
          id: "processing",
          style: {
            background: "rgba(15, 23, 42, 0.95)",
            color: "#e0f2fe",
            border: "1px solid rgba(56, 189, 248, 0.3)",
            backdropFilter: "blur(12px)",
          },
        }
      );

      // Call API
      const result = await animationAPI.smartChat(
        data.type === "image" ? data.file : null,
        data.type === "text" ? data.content : null,
        mode
      );

      // Clear loading toast
      toast.dismiss(loadingToastId);

      if (result.success) {
        handleSuccessResponse(result);
      } else {
        handleErrorResponse(result);
      }
    } catch (error) {
      console.error("Error processing message:", error);
      toast.dismiss("processing");
      
      // Show user-friendly error
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage, {
        duration: 5000,
        style: {
          background: "rgba(127, 29, 29, 0.95)",
          color: "#fecaca",
          border: "1px solid rgba(239, 68, 68, 0.4)",
        },
      });

      addMessage({
        role: "assistant",
        text: "❌ Oops! Something went wrong. Let's try that again.",
        error: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getLoadingMessage = (mode) => {
    const messages = {
      explain: "🔍 Analyzing problem step-by-step...",
      answer: "⚡ Finding the solution...",
      animate: "🎬 Creating your animation...",
      auto: "🤖 Processing your request...",
    };
    return messages[mode] || messages.auto;
  };

  const handleSuccessResponse = (result) => {
    const responses = {
      chat: {
        icon: "💬",
        toast: "Response ready!",
        toastStyle: { borderColor: "rgba(56, 189, 248, 0.4)" },
      },
      explanation: {
        icon: "📚",
        toast: "Explanation complete!",
        toastStyle: { borderColor: "rgba(56, 189, 248, 0.4)" },
      },
      answer: {
        icon: "⚡",
        toast: "Solution found!",
        toastStyle: { borderColor: "rgba(52, 211, 153, 0.4)" },
      },
      animation: {
        icon: "🎬",
        toast: "Animation created!",
        toastStyle: { borderColor: "rgba(139, 92, 246, 0.4)" },
      },
    };

    const response = responses[result.type] || responses.chat;

    toast.success(response.toast, {
      duration: 3000,
      style: {
        background: "rgba(15, 23, 42, 0.95)",
        color: "#e0f2fe",
        border: `1px solid ${response.toastStyle.borderColor}`,
        backdropFilter: "blur(12px)",
      },
    });

    addMessage({
      role: "assistant",
      text: `${response.icon} ${result.type === "animation" ? "Here's your animation!" : result.content || ""}`,
      mathText: result.math_text,
      videoUrl: result.video_url,
    });
  };

  const handleErrorResponse = (result) => {
    toast.error("Processing failed. Try again?", {
      duration: 4000,
      style: {
        background: "rgba(127, 29, 29, 0.95)",
        color: "#fecaca",
        border: "1px solid rgba(239, 68, 68, 0.4)",
      },
    });

    addMessage({
      role: "assistant",
      text: result.math_text
        ? `I extracted the math but couldn't complete processing. Want to try again?`
        : "❌ Processing failed. Please try again or rephrase your question.",
      mathText: result.math_text,
      error: result.render_error || result.message,
    });
  };

  const getErrorMessage = (error) => {
    const message = error.message?.toLowerCase() || "";
    
    if (message.includes("network") || message.includes("fetch")) {
      return "Connection lost. Check your internet.";
    } else if (message.includes("timeout")) {
      return "Request timed out. The problem might be too complex.";
    } else if (message.includes("500")) {
      return "Server error. Our team has been notified.";
    } else if (message.includes("no math")) {
      return "No math detected. Try a clearer image or type the equation.";
    }
    
    return "Something went wrong. Please try again.";
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950">
      {/* Animated background */}
      <div className="fixed inset-0 z-0">
        <motion.div
          animate={{
            backgroundPosition: ["0% 0%", "100% 100%"],
          }}
          transition={{
            duration: 20,
            repeat: Infinity,
            repeatType: "reverse",
          }}
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `
              radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.15), transparent 50%),
              radial-gradient(circle at 80% 80%, rgba(14, 165, 233, 0.1), transparent 50%),
              radial-gradient(circle at 50% 50%, rgba(52, 211, 153, 0.08), transparent 50%)
            `,
            backgroundSize: "200% 200%",
          }}
        />
        
        {/* Grid overlay */}
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "linear-gradient(rgba(148, 163, 184, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(148, 163, 184, 0.05) 1px, transparent 1px)",
            backgroundSize: "80px 80px",
          }}
        />

        {/* Floating math symbols */}
        <AnimatedSymbols />
      </div>

      {/* Connection status indicator */}
      <AnimatePresence>
        {connectionStatus === "error" && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed top-4 right-4 z-50 px-4 py-2 rounded-xl bg-rose-500/20 border border-rose-500/30 text-rose-200 text-sm flex items-center gap-2"
          >
            <span className="w-2 h-2 bg-rose-500 rounded-full animate-pulse" />
            Connection issue
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="relative z-10">
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 4000,
            style: {
              background: "rgba(15, 23, 42, 0.95)",
              color: "#e0f2fe",
              border: "1px solid rgba(56, 189, 248, 0.3)",
              backdropFilter: "blur(16px)",
              boxShadow: "0 20px 60px -30px rgba(14, 165, 233, 0.4)",
            },
          }}
        />
        
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
      </div>
    </div>
  );
}

// Animated floating math symbols
const AnimatedSymbols = () => {
  const symbols = [
    { char: "∑", x: "15%", y: "20%", duration: 20 },
    { char: "π", x: "85%", y: "15%", duration: 25 },
    { char: "∞", x: "10%", y: "70%", duration: 22 },
    { char: "∫", x: "90%", y: "75%", duration: 18 },
    { char: "Δ", x: "50%", y: "50%", duration: 30 },
    { char: "∂", x: "25%", y: "85%", duration: 24 },
  ];

  return (
    <>
      {symbols.map((symbol, i) => (
        <motion.div
          key={i}
          className="absolute text-6xl font-bold text-sky-200/10 pointer-events-none select-none"
          style={{ left: symbol.x, top: symbol.y }}
          animate={{
            y: [0, -30, 0],
            rotate: [0, 10, -10, 0],
            opacity: [0.1, 0.15, 0.1],
          }}
          transition={{
            duration: symbol.duration,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          {symbol.char}
        </motion.div>
      ))}
    </>
  );
};

export default App;