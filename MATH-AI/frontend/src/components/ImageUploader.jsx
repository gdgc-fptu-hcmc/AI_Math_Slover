import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { FiUpload, FiImage, FiX, FiCheck } from "react-icons/fi";
import { BiLoaderAlt } from "react-icons/bi";

const ImageUploader = ({ onUpload }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".gif", ".webp"],
    },
    maxFiles: 1,
    multiple: false,
  });

  const handleUpload = () => {
    if (selectedFile) {
      setUploading(true);
      onUpload(selectedFile);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPreview(null);
  };

  return (
    <div className="space-y-8 text-slate-200">
      <div className="space-y-3">
        <h2 className="text-3xl font-semibold text-sky-100">
          Transcribe Mathematical Imagery
        </h2>
        <p className="text-sm text-slate-300 md:text-base">
          Upload chalkboard work, handwritten derivations, or textbook diagrams
          to translate them into dynamic Manim scenes.
        </p>
        <div className="flex flex-wrap items-center gap-3 text-[0.65rem] font-mono uppercase tracking-[0.35em] text-sky-300/80">
          <span>∫ Calculus</span>
          <span className="text-slate-500/70">•</span>
          <span>Σ Series</span>
          <span className="text-slate-500/70">•</span>
          <span>Δ Geometry</span>
        </div>
      </div>

      {!preview ? (
        <div
          {...getRootProps()}
          className={`relative overflow-hidden rounded-3xl border-2 border-dashed transition duration-300 ${isDragActive ? "border-sky-300/80 bg-slate-900/80 shadow-[0_0_0_2px_rgba(56,189,248,0.35)]" : "border-slate-700/80 bg-slate-950/60 shadow-[0_30px_90px_-45px_rgba(8,47,73,0.9)]"}`}
        >
          <span className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_60%),radial-gradient(circle_at_bottom_right,rgba(14,165,233,0.16),transparent_55%)]" />
          <div className="relative flex flex-col items-center justify-center gap-4 px-10 py-16 text-center">
            <div className="rounded-2xl border border-sky-400/40 bg-slate-900/60 p-5 shadow-lg shadow-sky-900/40">
              <FiUpload className="text-5xl text-sky-200" />
            </div>
            {isDragActive ? (
              <p className="text-lg font-semibold text-sky-100">
                Release to analyse the notation…
              </p>
            ) : (
              <>
                <p className="text-lg font-semibold text-slate-100">
                  Drag & drop your mathematical image
                </p>
                <p className="text-sm text-slate-400">
                  or click to browse from your device
                </p>
              </>
            )}
            <div className="rounded-full border border-slate-700/70 bg-slate-900/60 px-5 py-1 font-mono text-xs uppercase tracking-[0.35em] text-slate-400">
              Supported: JPG · PNG · GIF · WebP
            </div>
          </div>
          <input {...getInputProps()} />
        </div>
      ) : (
        <div className="space-y-6">
          {/* Preview */}
          <div className="relative overflow-hidden rounded-3xl border border-slate-700/70 bg-slate-950/70 shadow-lg shadow-slate-950/60">
            <img
              src={preview}
              alt="Preview"
              className="w-full max-h-96 object-contain bg-slate-950/60"
            />
            <button
              onClick={handleClear}
              className="absolute top-4 right-4 rounded-full border border-rose-500/40 bg-rose-500/80 p-2 text-rose-50 shadow-lg transition hover:bg-rose-400/90"
              title="Remove image"
            >
              <FiX className="text-lg" />
            </button>
          </div>

          {/* File info */}
          <div className="rounded-2xl border border-slate-800/60 bg-slate-950/60 p-4 shadow-inner shadow-slate-950/60">
            <div className="flex flex-wrap items-center gap-3 text-sm text-slate-200">
              <FiImage className="text-sky-300" />
              <span className="font-semibold text-slate-100">
                {selectedFile?.name}
              </span>
              <span className="text-slate-500">
                ({(selectedFile?.size / 1024).toFixed(2)} KB)
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="flex flex-1 items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-sky-500 via-cyan-500 to-emerald-400 px-4 py-3 font-semibold text-slate-950 shadow-lg shadow-sky-900/40 transition hover:from-sky-400 hover:to-cyan-400 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {uploading ? (
                <>
                  <BiLoaderAlt className="text-xl text-slate-950/80" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <FiCheck className="text-xl" />
                  <span>Generate Animation</span>
                </>
              )}
            </button>
            <button
              onClick={handleClear}
              disabled={uploading}
              className="flex items-center justify-center rounded-2xl border border-slate-700/70 bg-slate-900/70 px-4 py-3 font-medium text-slate-200 transition hover:border-sky-400/70 hover:text-sky-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="rounded-2xl border border-slate-800/70 bg-slate-950/60 p-6 shadow-inner shadow-slate-950/60">
        <h3 className="mb-3 flex items-center gap-3 text-sm font-semibold uppercase tracking-[0.3em] text-sky-300">
          <span>💡</span>
          Optimise Clarity
        </h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-slate-300">
          <li>Ensure sharp focus so integrals and indices remain legible.</li>
          <li>Use even lighting to reveal chalk and ink strokes.</li>
          <li>Align the frame so axes and vectors appear straight.</li>
          <li>Crop distractions to emphasise the mathematical region.</li>
          <li>Handwritten and printed notation are both supported.</li>
        </ul>
      </div>
    </div>
  );
};

export default ImageUploader;
