import { renderHook } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { usePrefetch } from '@/hooks/usePrefetch';
import { useInView } from 'react-intersection-observer';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('react-intersection-observer', () => ({
  useInView: jest.fn(),
}));

describe('usePrefetch', () => {
  const mockRouter = {
    prefetch: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    (useInView as jest.Mock).mockReturnValue({
      ref: jest.fn(),
      inView: false,
    });
  });

  it('returns ref function', () => {
    const { result } = renderHook(() => usePrefetch('/test'));
    expect(result.current.ref).toBeDefined();
  });

  it('prefetches when element comes into view', () => {
    (useInView as jest.Mock).mockReturnValue({
      ref: jest.fn(),
      inView: true,
    });

    renderHook(() => usePrefetch('/test'));

    // Wait for the timeout
    jest.advanceTimersByTime(100);
    expect(mockRouter.prefetch).toHaveBeenCalledWith('/test');
  });

  it('does not prefetch when element is not in view', () => {
    renderHook(() => usePrefetch('/test'));
    
    jest.advanceTimersByTime(100);
    expect(mockRouter.prefetch).not.toHaveBeenCalled();
  });

  it('cleans up timeout on unmount', () => {
    const { unmount } = renderHook(() => usePrefetch('/test'));
    
    unmount();
    jest.advanceTimersByTime(100);
    expect(mockRouter.prefetch).not.toHaveBeenCalled();
  });

  it('respects custom prefetch timeout', () => {
    (useInView as jest.Mock).mockReturnValue({
      ref: jest.fn(),
      inView: true,
    });

    renderHook(() => usePrefetch('/test', 200));
    
    jest.advanceTimersByTime(100);
    expect(mockRouter.prefetch).not.toHaveBeenCalled();
    
    jest.advanceTimersByTime(100);
    expect(mockRouter.prefetch).toHaveBeenCalledWith('/test');
  });
});
