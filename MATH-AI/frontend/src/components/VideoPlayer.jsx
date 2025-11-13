import React, { useState, useRef } from "react";
import {
  FiDownload,
  FiMaximize2,
  FiMinimize2,
  FiPlay,
  FiPause,
} from "react-icons/fi";

const VideoPlayer = ({ videoUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const videoRef = useRef(null);
  const containerRef = useRef(null);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleDownload = () => {
    const link = document.createElement("a");
    link.href = videoUrl;
    link.download = "math-animation.mp4";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleVideoEnd = () => {
    setIsPlaying(false);
  };

  return (
    <div className="space-y-4 animate-fade-in text-slate-200">
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs uppercase tracking-[0.4em] text-sky-300">
          ✨ Rendered Sequence
        </span>
        <button
          onClick={handleDownload}
          className="group flex items-center gap-2 rounded-2xl border border-slate-700/70 bg-slate-900/70 px-3 py-2 text-sm font-medium text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100"
          title="Download render"
        >
          <FiDownload className="transition group-hover:text-sky-300" />
          <span>Download</span>
        </button>
      </div>

      <div
        ref={containerRef}
        className="video-container group border border-slate-800/60 bg-slate-950/80 shadow-[0_30px_90px_-45px_rgba(8,47,73,0.9)]"
      >
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full"
          onEnded={handleVideoEnd}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          controls={false}
        />

        {/* Custom Controls Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-900/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100">
          <div className="absolute bottom-0 left-0 right-0 flex items-center justify-between p-4">
            <button
              onClick={togglePlay}
              className="rounded-full border border-slate-700/60 bg-slate-900/70 p-2 text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100"
              title={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <FiPause className="text-xl" />
              ) : (
                <FiPlay className="text-xl" />
              )}
            </button>

            <button
              onClick={toggleFullscreen}
              className="rounded-full border border-slate-700/60 bg-slate-900/70 p-2 text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100"
              title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
            >
              {isFullscreen ? (
                <FiMinimize2 className="text-xl" />
              ) : (
                <FiMaximize2 className="text-xl" />
              )}
            </button>
          </div>
        </div>

        {/* Play Button Center (when not playing) */}
        {!isPlaying && (
          <div className="absolute inset-0 flex items-center justify-center">
            <button
              onClick={togglePlay}
              className="rounded-full border border-slate-700/60 bg-slate-900/80 p-6 text-slate-200 shadow-lg shadow-slate-950/60 transition hover:border-sky-400/70 hover:text-sky-100 hover:scale-110"
            >
              <FiPlay className="ml-1 text-4xl text-sky-300" />
            </button>
          </div>
        )}
      </div>

      {/* Native controls as fallback */}
      <div className="mt-2">
        <video
          src={videoUrl}
          controls
          className="hidden w-full rounded-2xl border border-slate-800/60 bg-slate-950/70"
          style={{ display: "none" }}
        />
        <details className="text-sm text-slate-400">
          <summary className="cursor-pointer text-slate-400 hover:text-sky-300">
            Show native controls
          </summary>
          <video
            src={videoUrl}
            controls
            className="mt-2 w-full rounded-2xl border border-slate-800/60 bg-slate-950/70"
          />
        </details>
      </div>
    </div>
  );
};

export default VideoPlayer;
