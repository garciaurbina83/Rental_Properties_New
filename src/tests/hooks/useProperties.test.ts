import { renderHook, act } from '@testing-library/react';
import { useProperties } from '@/hooks/useProperties';

// Mock axios or your API client
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}));

describe('useProperties', () => {
  const mockProperties = [
    { id: '1', title: 'Property 1' },
    { id: '2', title: 'Property 2' },
  ];

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  it('fetches properties successfully', async () => {
    const { result } = renderHook(() => useProperties());

    // Initial state
    expect(result.current.isLoading).toBe(true);
    expect(result.current.properties).toEqual([]);

    // Wait for data to be loaded
    await act(async () => {
      // Mock successful API response
      (global as any).fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockProperties,
      });
    });

    // Verify final state
    expect(result.current.isLoading).toBe(false);
    expect(result.current.properties).toEqual(mockProperties);
    expect(result.current.error).toBeNull();
  });

  it('handles fetch errors gracefully', async () => {
    const { result } = renderHook(() => useProperties());

    await act(async () => {
      // Mock API error
      (global as any).fetch.mockRejectedValueOnce(new Error('Failed to fetch'));
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeTruthy();
    expect(result.current.properties).toEqual([]);
  });

  it('filters properties correctly', async () => {
    const { result } = renderHook(() => useProperties());

    await act(async () => {
      (global as any).fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockProperties,
      });
    });

    act(() => {
      result.current.filterProperties({ status: 'available' });
    });

    expect(result.current.filteredProperties).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ status: 'available' }),
      ])
    );
  });
});
