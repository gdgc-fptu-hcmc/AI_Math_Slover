import React, { useState, useEffect } from "react";
import { Toaster, toast } from "react-hot-toast";
import ChatInterface from "./components/ChatInterface";
import { animationAPI } from "./services/api";

function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load welcome message
    const welcomeMessage = {
      role: "assistant",
      text: "👋 Hi! I can help you create beautiful math animations. Upload an image with math problems, take a photo, or type your question!",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, []);

  const ambientSymbols = [
    {
      char: "∑",
      className:
        "ambient-symbol top-16 left-12 text-7xl text-cyan-200/15 animate-pulse-slow",
    },
    {
      char: "π",
      className:
        "ambient-symbol top-[32%] right-14 text-6xl text-sky-200/20 animate-pulse",
    },
    {
      char: "∞",
      className:
        "ambient-symbol bottom-24 right-24 text-8xl text-cyan-100/15 animate-pulse-slow",
    },
    {
      char: "∫",
      className:
        "ambient-symbol bottom-20 left-16 text-6xl text-emerald-200/20 animate-pulse",
    },
    {
      char: "Δ",
      className:
        "ambient-symbol top-[58%] left-[43%] text-5xl text-indigo-200/20 animate-pulse",
    },
  ];

  const addMessage = (message) => {
    setMessages((prev) => [...prev, { ...message, timestamp: new Date() }]);
  };

  const handleSendMessage = async (data) => {
    try {
      setIsLoading(true);

      if (data.type === "text") {
        // Handle text input
        addMessage({
          role: "user",
          text: data.content,
        });

        toast.loading("Generating animation...", { id: "processing" });

        // Generate code from text
        const generateResult = await animationAPI.generate(data.content);

        if (!generateResult.success) {
          throw new Error(generateResult.message || "Failed to generate code");
        }

        // Render animation
        const renderResult = await animationAPI.render(generateResult.code);

        toast.dismiss("processing");

        if (renderResult.success) {
          addMessage({
            role: "assistant",
            text: "✨ I've created your animation!",
            videoUrl: renderResult.video_url,
          });
          toast.success("Animation ready!");
        } else {
          throw new Error(renderResult.message || "Rendering failed");
        }
      } else if (data.type === "image") {
        // Handle image upload/capture
        const reader = new FileReader();
        reader.onloadend = () => {
          addMessage({
            role: "user",
            image: reader.result,
          });
        };
        reader.readAsDataURL(data.file);

        toast.loading("Processing image...", { id: "processing" });

        // Process image to animation
        const result = await animationAPI.fromImage(data.file);

        toast.dismiss("processing");

        if (result.success) {
          addMessage({
            role: "assistant",
            text: "✨ I extracted the math content and created an animation!",
            mathText: result.math_text,
            videoUrl: result.video_url,
          });
          toast.success("Animation created!");
        } else {
          // Partial success - show what we got
          if (result.math_text) {
            addMessage({
              role: "assistant",
              text: `I found this math content but rendering failed. You can try again!`,
              mathText: result.math_text,
              error: result.render_error || result.message,
            });
            toast.error("Rendering failed");
          } else {
            throw new Error(result.message || "Processing failed");
          }
        }
      }
    } catch (error) {
      console.error("Error processing message:", error);
      toast.dismiss("processing");
      toast.error(error.message || "Something went wrong");

      addMessage({
        role: "assistant",
        text: "❌ Sorry, I encountered an error. Please try again!",
        error: error.message,
      });
    } finally {
      toast.dismiss("processing");
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="pointer-events-none absolute inset-0 z-0">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(14,165,233,0.18),transparent_60%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_30%,rgba(56,189,248,0.12),transparent_65%)]" />
        <div
          className="absolute inset-0 opacity-20"
          style={{
            backgroundImage:
              "linear-gradient(to right, rgba(148, 163, 184, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(148, 163, 184, 0.08) 1px, transparent 1px)",
            backgroundSize: "80px 80px",
          }}
        />
        <div className="absolute inset-0">
          {ambientSymbols.map((symbol, index) => (
            <div
              key={`${symbol.char}-${index}`}
              className={`absolute font-semibold tracking-tight ${symbol.className}`}
            >
              {symbol.char}
            </div>
          ))}
        </div>
      </div>

      <div className="pointer-events-none absolute hidden lg:block top-24 right-20 z-10">
        <div className="rounded-3xl border border-white/20 bg-white/10 px-6 py-5 backdrop-blur-md shadow-2xl">
          <p className="text-[10px] uppercase tracking-[0.35em] text-sky-200">
            Euler's Identity
          </p>
          <p className="mt-3 text-3xl font-semibold text-sky-100">
            {"e^{iπ} + 1 = 0"}
          </p>
          <p className="mt-2 text-xs text-sky-100/70">
            {"∑_{n=0}^{∞} x^n = 1 / (1 - x)"}
          </p>
        </div>
      </div>

      <div className="relative z-20">
        <Toaster
          position="top-center"
          toastOptions={{
            duration: 4000,
            className: "math-toast",
            style: {
              background: "rgba(2, 6, 23, 0.88)",
              color: "#e0f2fe",
              border: "1px solid rgba(56, 189, 248, 0.35)",
              boxShadow: "0 30px 80px -45px rgba(14, 165, 233, 0.6)",
              backdropFilter: "blur(14px)",
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: "#38bdf8",
                secondary: "#020617",
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: "#f472b6",
                secondary: "#020617",
              },
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

export default App;
