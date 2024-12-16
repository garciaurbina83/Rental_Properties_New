import { useState, useEffect } from 'react';
import Image from 'next/image';
import { cn } from '@/lib/utils';
import { Skeleton } from '@/components/ui/skeleton';

interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
  fallbackSrc?: string;
  aspectRatio?: string;
  objectFit?: 'contain' | 'cover' | 'fill';
  onLoad?: () => void;
  onError?: () => void;
}

export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  priority = false,
  className,
  fallbackSrc = '/images/placeholder.jpg',
  aspectRatio = '16/9',
  objectFit = 'cover',
  onLoad,
  onError,
}: OptimizedImageProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [currentSrc, setCurrentSrc] = useState(src);

  useEffect(() => {
    setCurrentSrc(src);
    setError(false);
    setLoading(true);
  }, [src]);

  const handleLoad = () => {
    setLoading(false);
    onLoad?.();
  };

  const handleError = () => {
    setError(true);
    setCurrentSrc(fallbackSrc);
    onError?.();
  };

  return (
    <div
      className={cn(
        'relative overflow-hidden bg-muted',
        className
      )}
      style={{ aspectRatio }}
    >
      {loading && (
        <Skeleton
          className="absolute inset-0 animate-pulse"
        />
      )}
      
      <Image
        src={currentSrc}
        alt={alt}
        width={width}
        height={height}
        priority={priority}
        quality={80}
        className={cn(
          'transition-opacity duration-300',
          loading ? 'opacity-0' : 'opacity-100',
          objectFit === 'contain' && 'object-contain',
          objectFit === 'cover' && 'object-cover',
          objectFit === 'fill' && 'object-fill'
        )}
        onLoadingComplete={handleLoad}
        onError={handleError}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        {...(width && height ? { width, height } : { fill: true })}
      />

      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted/50">
          <p className="text-sm text-muted-foreground">
            Error al cargar la imagen
          </p>
        </div>
      )}
    </div>
  );
}
