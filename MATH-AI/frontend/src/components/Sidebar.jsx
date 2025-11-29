import React, { useState } from 'react';
import { FiPlus, FiMessageSquare, FiTrash2, FiEdit2, FiCheck, FiX } from 'react-icons/fi';
import axios from 'axios';

const Sidebar = ({ sessions, currentSessionId, onSwitchSession, onNewSession, setSessions }) => {
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");

  const handleDelete = async (e, sessionId) => {
    e.stopPropagation();
    if (!window.confirm("Delete this chat?")) return;
    
    try {
      await axios.delete(`http://localhost:8000/api/chat/session/${sessionId}`);
      const newSessions = sessions.filter(s => s.id !== sessionId);
      setSessions(newSessions);
      if (currentSessionId === sessionId && newSessions.length > 0) {
        onSwitchSession(newSessions[0].id);
      } else if (newSessions.length === 0) {
        onNewSession();
      }
    } catch (err) {
      console.error("Failed to delete", err);
    }
  };

  const startEdit = (e, session) => {
    e.stopPropagation();
    setEditingId(session.id);
    setEditTitle(session.preview);
  };

  const saveEdit = async (e) => {
    e.stopPropagation();
    try {
      // In a real app, call API here: await axios.patch(...)
      // For local state update:
      setSessions(prev => prev.map(s => s.id === editingId ? { ...s, preview: editTitle } : s));
      setEditingId(null);
    } catch (err) {
      console.error("Failed to rename", err);
    }
  };

  const cancelEdit = (e) => {
    e.stopPropagation();
    setEditingId(null);
  };

  return (
    <div className="w-64 h-screen bg-slate-950 border-r border-slate-800 flex flex-col p-4 shrink-0">
      <div className="mb-6 flex items-center gap-2 px-2">
        {/* Replace with your actual logo path */}
        <span className="text-2xl">⚡</span> 
        <span className="font-bold text-slate-200 text-lg">Math AI</span>
      </div>

      <button
        onClick={onNewSession}
        className="flex items-center gap-2 w-full bg-sky-600 hover:bg-sky-500 text-white p-3 rounded-xl transition mb-6 shadow-lg shadow-sky-900/20 font-medium"
      >
        <FiPlus /> New Chat
      </button>

      <div className="flex-1 overflow-y-auto space-y-1 pr-1 scrollbar-thin">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 px-2">
          History
        </div>
        {sessions.map((session) => (
          <div
            key={session.id}
            onClick={() => onSwitchSession(session.id)}
            className={`group relative w-full text-left p-3 rounded-lg text-sm flex items-center gap-3 transition cursor-pointer border ${
              currentSessionId === session.id
                ? 'bg-slate-800 text-sky-300 border-slate-700'
                : 'border-transparent text-slate-400 hover:bg-slate-900 hover:text-slate-200'
            }`}
          >
            <FiMessageSquare className="shrink-0" />
            
            {editingId === session.id ? (
              <div className="flex items-center gap-1 w-full">
                <input 
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  onClick={(e) => e.stopPropagation()}
                  className="bg-slate-950 text-white text-xs p-1 rounded w-full border border-slate-600 focus:outline-none"
                  autoFocus
                />
                <button onClick={saveEdit} className="text-emerald-400 hover:bg-emerald-400/20 p-1 rounded"><FiCheck size={14}/></button>
                <button onClick={cancelEdit} className="text-rose-400 hover:bg-rose-400/20 p-1 rounded"><FiX size={14}/></button>
              </div>
            ) : (
              <>
                <span className="truncate flex-1">{session.preview || "New Conversation"}</span>
                
                {/* Hover Actions */}
                <div className="absolute right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-slate-900/80 backdrop-blur-sm rounded">
                  <button 
                    onClick={(e) => startEdit(e, session)} 
                    className="p-1.5 text-slate-400 hover:text-sky-300 hover:bg-slate-700 rounded"
                    title="Rename"
                  >
                    <FiEdit2 size={14} />
                  </button>
                  <button 
                    onClick={(e) => handleDelete(e, session.id)} 
                    className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-700 rounded"
                    title="Delete"
                  >
                    <FiTrash2 size={14} />
                  </button>
                </div>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;