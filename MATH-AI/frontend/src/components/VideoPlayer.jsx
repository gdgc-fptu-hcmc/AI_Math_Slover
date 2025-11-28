import React, { useState, useRef, useEffect } from "react";
import { FiDownload, FiMaximize2, FiPlay, FiPause, FiVolume2, FiVolumeX } from "react-icons/fi";
import { motion, AnimatePresence } from "framer-motion";

const VideoPlayer = ({ videoUrl }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [showControls, setShowControls] = useState(true);
  const [isBuffering, setIsBuffering] = useState(false);
  const videoRef = useRef(null);
  const containerRef = useRef(null);
  const controlsTimeoutRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(video.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleWaiting = () => setIsBuffering(true);
    const handleCanPlay = () => setIsBuffering(false);

    video.addEventListener("loadedmetadata", handleLoadedMetadata);
    video.addEventListener("timeupdate", handleTimeUpdate);
    video.addEventListener("ended", handleEnded);
    video.addEventListener("waiting", handleWaiting);
    video.addEventListener("canplay", handleCanPlay);

    return () => {
      video.removeEventListener("loadedmetadata", handleLoadedMetadata);
      video.removeEventListener("timeupdate", handleTimeUpdate);
      video.removeEventListener("ended", handleEnded);
      video.removeEventListener("waiting", handleWaiting);
      video.removeEventListener("canplay", handleCanPlay);
    };
  }, []);

  const togglePlay = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const toggleMute = () => {
    const video = videoRef.current;
    if (!video) return;

    video.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleVolumeChange = (e) => {
    const video = videoRef.current;
    if (!video) return;

    const newVolume = parseFloat(e.target.value);
    video.volume = newVolume;
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
    } else {
      document.exitFullscreen();
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

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleMouseMove = () => {
    setShowControls(true);
    if (controlsTimeoutRef.current) {
      clearTimeout(controlsTimeoutRef.current);
    }
    controlsTimeoutRef.current = setTimeout(() => {
      if (isPlaying) setShowControls(false);
    }, 3000);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="my-4 space-y-3"
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-emerald-400">✓</span>
          <span className="text-sm font-medium text-slate-300">Animation Ready</span>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={handleDownload}
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/60 border border-slate-700/50 hover:border-sky-500/50 text-sm text-slate-300 hover:text-sky-300 transition"
        >
          <FiDownload className="text-sm" />
          Download
        </motion.button>
      </div>

      {/* Video Container */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={() => isPlaying && setShowControls(false)}
        className="relative rounded-2xl overflow-hidden bg-black border border-slate-700/50 shadow-2xl group"
        style={{ aspectRatio: "16/9" }}
      >
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain"
          onClick={togglePlay}
        />

        {/* Buffering Indicator */}
        <AnimatePresence>
          {isBuffering && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex items-center justify-center bg-black/50"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                className="w-12 h-12 border-4 border-sky-500/30 border-t-sky-500 rounded-full"
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Center Play Button (when paused) */}
        <AnimatePresence>
          {!isPlaying && !isBuffering && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              className="absolute inset-0 flex items-center justify-center bg-black/30 backdrop-blur-sm cursor-pointer"
              onClick={togglePlay}
            >
              <motion.div
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="w-20 h-20 rounded-full bg-gradient-to-br from-sky-500 to-cyan-500 flex items-center justify-center shadow-2xl"
              >
                <FiPlay className="text-3xl text-white ml-1" />
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Controls Overlay */}
        <AnimatePresence>
          {(showControls || !isPlaying) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/60 to-transparent p-4 pt-12"
            >
              {/* Progress Bar */}
              <div
                className="w-full h-1.5 bg-slate-700/50 rounded-full mb-3 cursor-pointer group/progress"
                onClick={handleSeek}
              >
                <div
                  className="h-full bg-gradient-to-r from-sky-500 to-cyan-500 rounded-full relative transition-all group-hover/progress:h-2"
                  style={{ width: `${progress}%` }}
                >
                  <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-white rounded-full shadow-lg opacity-0 group-hover/progress:opacity-100 transition" />
                </div>
              </div>

              {/* Controls */}
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={togglePlay}
                    className="text-white hover:text-sky-400 transition"
                  >
                    {isPlaying ? <FiPause className="text-xl" /> : <FiPlay className="text-xl" />}
                  </motion.button>

                  <span className="text-sm text-slate-300 font-mono">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  {/* Volume Control */}
                  <div className="flex items-center gap-2 group/volume">
                    <button
                      onClick={toggleMute}
                      className="text-white hover:text-sky-400 transition"
                    >
                      {isMuted || volume === 0 ? (
                        <FiVolumeX className="text-lg" />
                      ) : (
                        <FiVolume2 className="text-lg" />
                      )}
                    </button>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={volume}
                      onChange={handleVolumeChange}
                      className="w-0 group-hover/volume:w-20 transition-all opacity-0 group-hover/volume:opacity-100"
                    />
                  </div>

                  <button
                    onClick={toggleFullscreen}
                    className="text-white hover:text-sky-400 transition"
                  >
                    <FiMaximize2 className="text-lg" />
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Video Info */}
      <div className="flex items-center gap-4 text-xs text-slate-400">
        <span>🎬 MP4 Video</span>
        <span>•</span>
        <span>16:9 Aspect</span>
        <span>•</span>
        <span className="text-sky-400">Manim Generated</span>
      </div>
    </motion.div>
  );
};

export default VideoPlayer;