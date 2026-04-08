import { useState, useRef, useEffect } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  style?: React.CSSProperties;
  sizes?: string;
  priority?: boolean;
  aspectRatio?: string;
  onLoad?: () => void;
}

// Generate srcset for responsive images
function generateSrcSet(src: string): string {
  // If it's an Unsplash URL, use their transformation
  if (src.includes('unsplash.com')) {
    return [
      `${src.split('?')[0]}?w=400&q=75 400w`,
      `${src.split('?')[0]}?w=800&q=80 800w`,
      `${src.split('?')[0]}?w=1200&q=85 1200w`,
      `${src.split('?')[0]}?w=1600&q=85 1600w`,
    ].join(', ');
  }

  // For local/server images, check if we have optimized versions
  if (src.includes('/media/')) {
    const parts = src.split('.');
    parts.pop();
    const base = parts.join('.');

    // Try to use WebP optimized versions
    return [
      `${base.replace('/media/', '/media/optimized/')}_thumb.webp 400w`,
      `${base.replace('/media/', '/media/optimized/')}_medium.webp 800w`,
      `${base.replace('/media/', '/media/optimized/')}_large.webp 1200w`,
    ].join(', ');
  }

  return '';
}

// Create a tiny placeholder color
function getPlaceholderColor(src: string): string {
  // Generate a consistent color based on the URL
  let hash = 0;
  for (let i = 0; i < src.length; i++) {
    hash = src.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = hash % 360;
  return `hsl(${hue}, 40%, 85%)`;
}

export function OptimizedImage({
  src,
  alt,
  className = '',
  style = {},
  sizes = '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw',
  priority = false,
  aspectRatio,
  onLoad,
}: OptimizedImageProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || isInView) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '200px', // Start loading 200px before entering viewport
        threshold: 0.01,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => observer.disconnect();
  }, [priority, isInView]);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    // Fallback to original src on error
  };

  const srcSet = generateSrcSet(src);
  const placeholderColor = getPlaceholderColor(src);

  // Fallback image
  const fallbackSrc = 'https://images.unsplash.com/photo-1502680390469-be75c86b636f?w=800&h=600&fit=crop';

  return (
    <div
      ref={imgRef}
      className={className}
      style={{
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: placeholderColor,
        aspectRatio: aspectRatio,
        ...style,
      }}
    >
      {/* Blur placeholder */}
      {!isLoaded && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            backgroundColor: placeholderColor,
            filter: 'blur(20px)',
            transform: 'scale(1.1)',
            transition: 'opacity 0.3s ease-out',
            opacity: isLoaded ? 0 : 1,
          }}
        />
      )}

      {/* Actual image */}
      {isInView && (
        <img
          src={hasError ? fallbackSrc : src}
          srcSet={!hasError && srcSet ? srcSet : undefined}
          sizes={srcSet ? sizes : undefined}
          alt={alt}
          loading={priority ? 'eager' : 'lazy'}
          decoding={priority ? 'sync' : 'async'}
          fetchPriority={priority ? 'high' : 'auto'}
          onLoad={handleLoad}
          onError={handleError}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease-out',
          }}
        />
      )}

      {/* Loading skeleton */}
      {!isLoaded && isInView && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: `linear-gradient(90deg, ${placeholderColor} 25%, rgba(255,255,255,0.3) 50%, ${placeholderColor} 75%)`,
            backgroundSize: '200% 100%',
            animation: 'shimmer 1.5s infinite',
          }}
        />
      )}

      <style>{`
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  );
}

// Preload critical images
export function preloadImage(src: string): void {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.as = 'image';
  link.href = src;
  document.head.appendChild(link);
}

// Hook for preloading images
export function useImagePreload(images: string[], priority: number = 3): void {
  useEffect(() => {
    images.slice(0, priority).forEach(preloadImage);
  }, [images, priority]);
}
