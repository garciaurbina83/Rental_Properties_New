import { useRouter } from 'next/navigation';
import { useCallback, useEffect } from 'react';
import { useInView } from 'react-intersection-observer';

export function usePrefetch(href: string, prefetchTimeout = 100) {
  const router = useRouter();
  const { ref, inView } = useInView({
    threshold: 0,
    triggerOnce: true,
  });

  const doPrefetch = useCallback(() => {
    router.prefetch(href);
  }, [router, href]);

  useEffect(() => {
    if (inView) {
      const timeoutId = setTimeout(doPrefetch, prefetchTimeout);
      return () => clearTimeout(timeoutId);
    }
  }, [inView, doPrefetch, prefetchTimeout]);

  return { ref };
}
