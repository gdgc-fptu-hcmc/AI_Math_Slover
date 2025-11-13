import React, { useState, useRef, useCallback } from "react";
import Webcam from "react-webcam";
import { FiCamera, FiRotateCw, FiCheck, FiX } from "react-icons/fi";
import { BiLoaderAlt } from "react-icons/bi";

const CameraCapture = ({ onCapture }) => {
  const webcamRef = useRef(null);
  const [capturedImage, setCapturedImage] = useState(null);
  const [facingMode, setFacingMode] = useState("user");
  const [isCapturing, setIsCapturing] = useState(false);

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: facingMode,
  };

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setCapturedImage(imageSrc);
    }
  }, [webcamRef]);

  const switchCamera = () => {
    setFacingMode((prevMode) => (prevMode === "user" ? "environment" : "user"));
  };

  const retake = () => {
    setCapturedImage(null);
  };

  const handleConfirm = async () => {
    if (capturedImage) {
      setIsCapturing(true);
      // Convert base64 to blob
      const response = await fetch(capturedImage);
      const blob = await response.blob();
      const file = new File([blob], "camera-capture.jpg", {
        type: "image/jpeg",
      });
      onCapture(file);
    }
  };

  return (
    <div className="space-y-6 text-slate-200">
      <div className="space-y-3">
        <h2 className="text-3xl font-semibold text-sky-100">
          Capture Mathematical Insight
        </h2>
        <p className="text-sm text-slate-300 md:text-base">
          Use your camera to frame equations, diagrams, or proofs with clarity.
        </p>
      </div>

      <div className="relative rounded-3xl border border-slate-800/60 bg-slate-950/60 p-4 shadow-xl shadow-slate-950/50 backdrop-blur">
        {!capturedImage ? (
          <div className="webcam-preview overflow-hidden rounded-2xl border border-slate-800/60 bg-slate-900/80 shadow-lg shadow-slate-950/50">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="relative rounded-2xl overflow-hidden border border-slate-700/70 bg-slate-900/80 shadow-lg shadow-slate-950/50">
            <img
              src={capturedImage}
              alt="Captured"
              className="w-full object-contain bg-slate-950/60"
            />
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex flex-wrap justify-center gap-4 rounded-2xl border border-slate-800/60 bg-slate-950/60 p-5 shadow-inner shadow-slate-950/60">
        {!capturedImage ? (
          <>
            <button
              onClick={capture}
              className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-sky-500 via-cyan-500 to-emerald-400 px-8 py-3 text-lg font-semibold text-slate-950 shadow-lg shadow-sky-900/40 transition hover:from-sky-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <FiCamera className="text-2xl" />
              <span>Capture</span>
            </button>
            <button
              onClick={switchCamera}
              className="rounded-xl border border-slate-700/70 bg-slate-900/80 p-3 text-slate-200 transition hover:border-emerald-400/70 hover:text-emerald-200 disabled:cursor-not-allowed disabled:opacity-50"
              title="Switch Camera"
            >
              <FiRotateCw className="text-xl" />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={handleConfirm}
              disabled={isCapturing}
              className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-sky-500 via-cyan-500 to-emerald-400 px-6 py-3 font-semibold text-slate-950 shadow-lg shadow-sky-900/40 transition hover:from-sky-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isCapturing ? (
                <>
                  <BiLoaderAlt className="animate-spin text-xl" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FiCheck className="text-xl" />
                  <span>Use This Photo</span>
                </>
              )}
            </button>
            <button
              onClick={retake}
              disabled={isCapturing}
              className="flex items-center gap-2 rounded-2xl border border-slate-700/70 bg-slate-900/80 px-6 py-3 text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <FiX className="text-xl" />
              <span>Retake</span>
            </button>
          </>
        )}
      </div>

      {/* Camera Tips */}
      <div className="mt-8 rounded-2xl border border-slate-800/70 bg-slate-950/60 p-6 shadow-inner shadow-slate-950/60">
        <h3 className="mb-3 flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.3em] text-sky-300">
          <span>📷</span>
          Capture Tips
        </h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-slate-300">
          <li>
            Stabilize the frame so lines stay parallel to the image plane.
          </li>
          <li>Illuminate the page to showcase symbols and annotations.</li>
          <li>Center the key expressions within the viewport.</li>
          <li>Minimize shadows that could occlude integral signs or limits.</li>
          <li>Keep the paper level to reduce perspective distortion.</li>
        </ul>
      </div>
    </div>
  );
};

export default CameraCapture;
