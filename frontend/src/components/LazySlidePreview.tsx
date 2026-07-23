import { useEffect, useRef, useState } from 'react';
import { ReadOnlySlide } from './ReadOnlySlide';
import { FolderOpen } from 'lucide-react';

interface LazySlidePreviewProps {
  slideId: string;
  htmlContent: string;
  backgroundColor?: string;
  backgroundImage?: string;
  className?: string;
}

/**
 * Lazy-loading wrapper for ReadOnlySlide that only renders when visible in viewport.
 * Dramatically improves performance on Projects page with many thumbnails.
 */
export const LazySlidePreview = ({
  slideId,
  htmlContent,
  backgroundColor,
  backgroundImage,
  className,
}: LazySlidePreviewProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = useState(false);
  const hasRenderedRef = useRef(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !hasRenderedRef.current) {
            setIsVisible(true);
            hasRenderedRef.current = true;
            // Disconnect after first render to free resources
            if (observerRef.current) {
              observerRef.current.disconnect();
              observerRef.current = null;
            }
          }
        });
      },
      {
        rootMargin: '200px', // Start loading 200px before visible
        threshold: 0.01,
      }
    );

    observerRef.current.observe(element);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, []);

  return (
    <div ref={containerRef} className={className}>
      {isVisible ? (
        <ReadOnlySlide
          slideId={slideId}
          htmlContent={htmlContent}
          backgroundColor={backgroundColor}
          backgroundImage={backgroundImage}
          className="absolute inset-0"
        />
      ) : (
        <div className="flex h-full items-center justify-center bg-muted">
          <FolderOpen className="h-8 w-8 text-muted-foreground/30" />
        </div>
      )}
    </div>
  );
};
