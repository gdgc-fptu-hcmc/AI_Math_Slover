import React, { useState, useRef, useEffect } from "react";
import { 
  FiSend, FiPaperclip, FiVideo, FiX, FiFileText, FiImage, FiCpu, FiUser 
} from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";
import VideoPlayer from "./VideoPlayer";
import CodeViewer from "./CodeViewer";

// --- NEW IMPORTS FOR MARKDOWN & MATH ---
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

const ChatInterface = ({ messages, isLoading, onSendMessage }) => {
  const [inputText, setInputText] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);
  const [animateMode, setAnimateMode] = useState(false);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [inputText]);

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      if (file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onloadend = () => setFilePreview({ type: 'image', url: reader.result, name: file.name });
        reader.readAsDataURL(file);
      } else if (file.type === "application/pdf") {
        // Explicit PDF Handling
        setFilePreview({ type: 'pdf', name: file.name });
      } else {
        // Generic fallback
        setFilePreview({ type: 'file', name: file.name });
      }
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setFilePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handleSubmit = () => {
    if ((!inputText.trim() && !selectedFile) || isLoading) return;

    onSendMessage({
      content: inputText,
      file: selectedFile,
      // Pass the preview type to show in the bubble
      previewData: filePreview, 
      animate: animateMode
    });

    setInputText("");
    clearFile();
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="flex flex-col h-full relative">
      
      {/* 1. Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 scrollbar-thin">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full text-slate-500 opacity-60 select-none">
            <div className="text-6xl mb-4 bg-slate-800 rounded-3xl p-4">👋</div>
            <p className="font-medium">Ask a math question or upload a problem.</p>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-slate-800/50 border border-slate-700/50 rounded-2xl rounded-tl-none p-4 flex items-center gap-3">
              <div className="flex space-x-1">
                <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0 }} className="w-2 h-2 bg-sky-400 rounded-full"/>
                <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.2 }} className="w-2 h-2 bg-sky-400 rounded-full"/>
                <motion.div animate={{ y: [0, -6, 0] }} transition={{ repeat: Infinity, duration: 0.6, delay: 0.4 }} className="w-2 h-2 bg-sky-400 rounded-full"/>
              </div>
              <span className="text-xs text-slate-400 font-medium tracking-wide">AI IS THINKING...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* 2. Input Area */}
      <div className="p-4 bg-slate-950/80 backdrop-blur-xl border-t border-slate-800/50">
        <div className="max-w-4xl mx-auto bg-slate-900 border border-slate-700/60 rounded-2xl shadow-2xl transition-all focus-within:ring-1 focus-within:ring-sky-500/50 focus-within:border-sky-500/50">
          
          {/* File Preview Banner - VISIBLE PDF INDICATOR */}
          <AnimatePresence>
            {filePreview && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: "auto", opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="bg-slate-800/80 border-b border-slate-700/50 px-4 py-3 flex items-center justify-between"
              >
                <div className="flex items-center gap-3 overflow-hidden">
                  {filePreview.type === 'image' ? (
                    <img src={filePreview.url} alt="preview" className="h-10 w-10 object-cover rounded-lg border border-slate-600" />
                  ) : (
                    // THIS IS THE PDF/FILE ICON PREVIEW
                    <div className="h-10 w-10 shrink-0 bg-rose-500/20 text-rose-400 rounded-lg flex items-center justify-center border border-rose-500/30">
                      <FiFileText size={20} />
                    </div>
                  )}
                  <div className="flex flex-col truncate">
                    <span className="text-sm text-slate-200 font-medium truncate">
                      {filePreview.type === 'image' ? 'Image Attached' : 'PDF Attached'}
                    </span>
                    <span className="text-xs text-slate-500 truncate max-w-[200px]">
                      {filePreview.name}
                    </span>
                  </div>
                </div>
                <button onClick={clearFile} className="p-2 hover:bg-slate-700 rounded-full text-slate-400 transition hover:text-white">
                  <FiX />
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Text Area */}
          <textarea
            ref={textareaRef}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={animateMode ? "Describe what you want to animate..." : "Ask a math question, upload an image or PDF..."}
            className="w-full bg-transparent border-none text-slate-100 placeholder-slate-500 px-4 py-3 max-h-[200px] focus:ring-0 resize-none scrollbar-thin"
            rows={1}
          />

          {/* Toolbar */}
          <div className="flex items-center justify-between px-3 pb-3 pt-1">
            <div className="flex items-center gap-2">
              
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="p-2 text-slate-400 hover:text-sky-400 hover:bg-slate-800 rounded-xl transition-colors relative group"
                title="Upload Image or PDF"
              >
                <FiPaperclip size={20} />
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                onChange={handleFileSelect} 
                className="hidden" 
                accept="image/*,application/pdf" 
              />

              <div className="h-6 w-px bg-slate-700 mx-1"></div>
              
              <button
                onClick={() => setAnimateMode(!animateMode)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${
                  animateMode
                    ? "bg-indigo-500/10 text-indigo-300 border-indigo-500/40 shadow-[0_0_15px_rgba(99,102,241,0.15)]"
                    : "bg-slate-800/50 text-slate-500 border-slate-700 hover:bg-slate-800 hover:text-slate-300"
                }`}
              >
                <FiVideo size={14} className={animateMode ? "animate-pulse" : ""} />
                {animateMode ? "ANIMATION MODE" : "Text Mode"}
              </button>
            </div>

            <button
              onClick={handleSubmit}
              disabled={(!inputText.trim() && !selectedFile) || isLoading}
              className={`p-2.5 rounded-xl transition-all shadow-lg ${
                (!inputText.trim() && !selectedFile) || isLoading
                  ? "bg-slate-800 text-slate-600 cursor-not-allowed"
                  : "bg-gradient-to-br from-sky-500 to-blue-600 text-white hover:shadow-sky-500/25 hover:scale-105 active:scale-95"
              }`}
            >
              <FiSend size={18} />
            </button>
          </div>
        </div>
        <div className="text-center mt-3">
          <p className="text-[10px] text-slate-600 uppercase tracking-widest font-semibold">
            Powered by Google Gemini 2.5 Flash Lite
          </p>
        </div>
      </div>
    </div>
  );
};

// --- Sub-component: Message Bubble with Markdown ---

const MessageBubble = ({ message }) => {
  const isUser = message.role === "user";
  
  // Handle attachments in the bubble
  const hasImage = message.image; // Assuming base64 or url
  // If we passed previewData in the message object for user messages:
  const isPdf = message.previewData?.type === 'pdf' || (message.file && message.file.type === 'application/pdf'); 
  const fileName = message.previewData?.name || "Document.pdf";

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div className={`flex max-w-[90%] md:max-w-[80%] gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center shadow-lg ${
          isUser 
            ? "bg-gradient-to-br from-indigo-500 to-purple-600" 
            : "bg-gradient-to-br from-emerald-500 to-teal-600"
        }`}>
          {isUser ? <FiUser className="text-white text-sm" /> : <FiCpu className="text-white text-sm" />}
        </div>

        {/* Content Box */}
        <div className={`flex flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
          <div className={`rounded-2xl px-5 py-3.5 shadow-md overflow-hidden ${
            isUser 
              ? "bg-indigo-600/90 text-white rounded-tr-none" 
              : "bg-slate-800 border border-slate-700/50 text-slate-100 rounded-tl-none"
          }`}>
            
            {/* 1. Attachment Display in Bubble */}
            {hasImage && (
              <div className="mb-3 -mx-2 -mt-2">
                <img src={message.image} alt="User upload" className="rounded-lg max-h-64 border border-white/10" />
              </div>
            )}
            
            {/* PDF Indicator in Bubble */}
            {isPdf && (
               <div className={`mb-3 flex items-center gap-3 p-3 rounded-lg ${isUser ? "bg-indigo-700/50" : "bg-slate-900/50"} border border-white/10`}>
                 <div className="bg-rose-500/20 p-2 rounded text-rose-300">
                   <FiFileText size={24} />
                 </div>
                 <div className="flex flex-col">
                   <span className="text-sm font-semibold opacity-90">PDF Document</span>
                   <span className="text-xs opacity-70 truncate max-w-[150px]">{fileName}</span>
                 </div>
               </div>
            )}

            {/* 2. Text Content with MARKDOWN & MATH */}
            <div className={`prose prose-invert max-w-none text-sm leading-relaxed ${isUser ? "prose-p:text-white" : "prose-p:text-slate-200"}`}>
              {message.text ? (
                <ReactMarkdown 
                  remarkPlugins={[remarkMath]} 
                  rehypePlugins={[rehypeKatex]}
                  components={{
                    // Custom rendering for code blocks if needed
                    code({node, inline, className, children, ...props}) {
                      return !inline ? (
                        <code className="block bg-slate-950/50 p-3 rounded-lg text-xs font-mono my-2 border border-white/10" {...props}>
                          {children}
                        </code>
                      ) : (
                        <code className="bg-white/10 px-1 py-0.5 rounded text-xs font-mono" {...props}>
                          {children}
                        </code>
                      )
                    }
                  }}
                >
                  {message.text}
                </ReactMarkdown>
              ) : (
                /* Fallback if just an image was sent */
                !hasImage && !isPdf && <span className="italic opacity-50">Sent an attachment</span>
              )}
            </div>
          </div>

          {/* 3. Assistant Assets (Video/Code) */}
          {!isUser && (
            <div className="w-full space-y-3 mt-1">
              {message.videoUrl && (
                <div className="w-full max-w-2xl overflow-hidden rounded-2xl border border-slate-700 shadow-2xl bg-black">
                  <VideoPlayer videoUrl={message.videoUrl} />
                </div>
              )}
              {message.code && (
                <div className="w-full max-w-2xl">
                  <CodeViewer code={message.code} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default ChatInterface;