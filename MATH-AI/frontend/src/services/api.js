import axios from "axios";

// Configure axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8001",
  timeout: 300000, // 5 minutes for video rendering
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add any auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail || error.message || "An error occurred";
    console.error("API Error:", message);
    return Promise.reject(new Error(message));
  },
);

// API methods
export const imageAPI = {
  /**
   * Upload and analyze image
   */
  async upload(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/image/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Extract text from image
   */
  async extractText(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/image/extract-text", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Comprehensive image analysis
   */
  async analyze(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/image/analyze", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },
};

export const animationAPI = {
  /**
   * Generate Manim code from math text
   */
  async generate(mathText, additionalContext = "") {
    const response = await api.post("/api/animation/generate", {
      math_text: mathText,
      additional_context: additionalContext,
    });

    return response.data;
  },

  /**
   * Render animation from code
   */
  async render(code, sceneName = "MathAnimation") {
    const response = await api.post("/api/animation/render", {
      code,
      scene_name: sceneName,
    });

    return response.data;
  },

  /**
   * Complete pipeline: image to animation
   */
  async fromImage(file, additionalContext = "") {
    const formData = new FormData();
    formData.append("file", file);
    if (additionalContext) {
      formData.append("additional_context", additionalContext);
    }

    const response = await api.post("/api/animation/from-image", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Improve existing code based on feedback
   */
  async improve(code, feedback) {
    const response = await api.post("/api/animation/improve", {
      code,
      feedback,
    });

    return response.data;
  },

  /**
   * Explain math problem from image
   */
  async explain(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/api/animation/explain", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },

  /**
   * Validate Manim code
   */
  async validate(code) {
    const formData = new FormData();
    formData.append("code", code);

    const response = await api.post("/api/animation/validate", formData, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    });

    return response.data;
  },

  /**
   * Clean up old temporary files
   */
  async cleanup(maxAgeHours = 24) {
    const response = await api.post("/api/animation/cleanup", null, {
      params: { max_age_hours: maxAgeHours },
    });

    return response.data;
  },

  /**
   * Smart chat endpoint - auto-detects intent or uses specified mode
   */
  async smartChat(file = null, text = null, mode = "auto") {
    const formData = new FormData();

    if (file) {
      formData.append("file", file);
    }
    if (text) {
      formData.append("text", text);
    }
    formData.append("mode", mode);

    const response = await api.post("/api/animation/chat", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get("/health");
  return response.data;
};

// WebSocket connection
export class WebSocketService {
  constructor() {
    this.ws = null;
    this.listeners = new Map();
  }

  connect(url = "ws://localhost:8001/ws") {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(url);

        this.ws.onopen = () => {
          console.log("WebSocket connected");
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.emit("message", data);
          } catch (e) {
            console.error("Failed to parse WebSocket message:", e);
          }
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.emit("error", error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log("WebSocket disconnected");
          this.emit("close");
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error("WebSocket is not connected");
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default api;
