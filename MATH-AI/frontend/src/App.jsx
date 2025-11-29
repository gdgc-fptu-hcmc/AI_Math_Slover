import React, { useState, useEffect } from "react";
import { Toaster, toast } from "react-hot-toast";
import ChatInterface from "./components/ChatInterface";
import Sidebar from "./components/Sidebar";
import axios from "axios";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Initialize first session
    createNewSession();
  }, []);

  const createNewSession = async () => {
    try {
      const res = await axios.post("http://localhost:8000/api/chat/session/new");
      const newId = res.data.session_id;
      setSessionId(newId);
      setMessages([{
        role: "assistant",
        text: "Hello! I'm your Math AI. Upload a PDF, an image, or just ask a question. Toggle 'Animate' if you want a video!"
      }]);
      setSessions(prev => [{id: newId, preview: "New Chat"}, ...prev]);
    } catch (e) {
      console.error(e);
    }
  };

  const switchSession = async (id) => {
    setIsLoading(true);
    setSessionId(id);
    try {
      // Actually fetch the history from the backend
      const res = await axios.get(`http://localhost:8000/api/chat/session/${id}`);
      
      // Transform backend history format to frontend UI format
      const formattedHistory = res.data.history.map(msg => ({
        role: msg.role,
        text: msg.content,
        // If the message had metadata (video/code), restore it
        videoUrl: msg.metadata?.video_url || null,
        code: msg.metadata?.code || null
      }));
      
      setMessages(formattedHistory);
    } catch (e) {
      console.error("Failed to load history", e);
      toast.error("Could not load chat history");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (data) => {
    if (!sessionId) return;

    // Optimistic UI
    const newMsg = { 
      role: "user", 
      text: data.content, 
      image: data.imagePreview, // Base64 image
      previewData: data.previewData // { type: 'pdf', name: '...' }
    };
    setMessages(prev => [...prev, newMsg]);
    setIsLoading(true);

    const formData = new FormData();
    formData.append("session_id", sessionId);
    formData.append("message", data.content || "");
    formData.append("animate", data.animate);
    
    if (data.file) {
      formData.append("files", data.file);
    }

    try {
      const res = await axios.post("http://localhost:8000/api/chat/send", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      const result = res.data;
      
      const botMsg = {
        role: "assistant",
        text: result.text,
        videoUrl: result.type === "animation" ? result.video_url : null,
        code: result.type === "animation" ? result.code : null
      };

      setMessages(prev => [...prev, botMsg]);
      
      // Update session title
      setSessions(prev => prev.map(s => 
        s.id === sessionId && s.preview === "New Chat" 
          ? {...s, preview: data.content.substring(0, 30) || "Image Analysis"} 
          : s
      ));

    } catch (error) {
      toast.error("Failed to get response");
      setMessages(prev => [...prev, { role: "assistant", text: "Sorry, I encountered an error." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
      <Toaster position="top-right" />
      
      {/* Sidebar */}
      <div className="hidden md:block">
        <Sidebar 
          sessions={sessions} 
          currentSessionId={sessionId} 
          onSwitchSession={switchSession}
          onNewSession={createNewSession}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col h-full relative">
        {/* Background Gradients */}
        <div className="absolute inset-0 pointer-events-none opacity-20 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-sky-900 via-slate-950 to-slate-950"></div>
        
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