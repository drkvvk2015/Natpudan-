/* eslint-disable no-inline-styles, react/no-inline-styles */
import React, { useState } from 'react';
import { X, ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react';

interface ImageViewerProps {
  images: Array<{
    path: string;
    caption?: string;
    description?: string;
    page?: number;
    hash?: string;
  }>;
  initialIndex?: number;
  onClose: () => void;
}

export const ImageViewer: React.FC<ImageViewerProps> = ({
  images,
  initialIndex = 0,
  onClose,
}) => {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);
  const [zoom, setZoom] = useState(1);

  const currentImage = images[currentIndex];

  const handlePrevious = () => {
    setCurrentIndex((prev) => (prev > 0 ? prev - 1 : images.length - 1));
    setZoom(1);
  };

  const handleNext = () => {
    setCurrentIndex((prev) => (prev < images.length - 1 ? prev + 1 : 0));
    setZoom(1);
  };

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.25, 3));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.25, 0.5));

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowLeft') handlePrevious();
    if (e.key === 'ArrowRight') handleNext();
    if (e.key === 'Escape') onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center"
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
        aria-label="Close viewer"
      >
        <X className="w-6 h-6 text-white" />
      </button>

      {/* Zoom controls */}
      <div className="absolute top-4 left-4 flex gap-2">
        <button
          onClick={handleZoomOut}
          className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          aria-label="Zoom out"
        >
          <ZoomOut className="w-5 h-5 text-white" />
        </button>
        <span className="px-3 py-2 rounded-full bg-white/10 text-white text-sm">
          {Math.round(zoom * 100)}%
        </span>
        <button
          onClick={handleZoomIn}
          className="p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
          aria-label="Zoom in"
        >
          <ZoomIn className="w-5 h-5 text-white" />
        </button>
      </div>

      {/* Navigation */}
      {images.length > 1 && (
        <>
          <button
            onClick={handlePrevious}
            className="absolute left-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
            aria-label="Previous image"
          >
            <ChevronLeft className="w-6 h-6 text-white" />
          </button>
          <button
            onClick={handleNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 p-2 rounded-full bg-white/10 hover:bg-white/20 transition-colors"
            aria-label="Next image"
          >
            <ChevronRight className="w-6 h-6 text-white" />
          </button>
        </>
      )}

      {/* Image container */}
      <div className="flex flex-col items-center max-w-7xl max-h-screen p-4">
        {/* eslint-disable-next-line jsx-a11y/no-static-element-interactions */}
        <div
          className="overflow-auto max-h-[70vh] flex items-center justify-center transition-transform duration-200 transform"
          style={{ transform: `scale(${zoom})` }}
        >
          <img
            src={currentImage.path}
            alt={currentImage.caption || `Image ${currentIndex + 1}`}
            className="max-w-full max-h-full object-contain"
          />
        </div>

        {/* Image info */}
        <div className="mt-4 max-w-2xl w-full bg-white/10 backdrop-blur-sm rounded-lg p-4 text-white">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">
              Image {currentIndex + 1} of {images.length}
            </span>
            {currentImage.page && (
              <span className="text-sm text-white/70">Page {currentImage.page}</span>
            )}
          </div>

          {currentImage.caption && (
            <div className="mb-2">
              <p className="text-sm font-medium text-white/90">Caption:</p>
              <p className="text-sm text-white/80">{currentImage.caption}</p>
            </div>
          )}

          {currentImage.description && (
            <div>
              <p className="text-sm font-medium text-white/90">AI Description:</p>
              <p className="text-sm text-white/80">{currentImage.description}</p>
            </div>
          )}
        </div>
      </div>

      {/* Counter */}
      {images.length > 1 && (
        <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-1">
          {images.map((_, idx) => (
            <button
              key={idx}
              onClick={() => {
                setCurrentIndex(idx);
                setZoom(1);
              }}
              className={`w-2 h-2 rounded-full transition-colors ${
                idx === currentIndex ? 'bg-white' : 'bg-white/30'
              }`}
              aria-label={`Go to image ${idx + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  );
};
