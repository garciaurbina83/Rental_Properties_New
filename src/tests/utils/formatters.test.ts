import { formatPrice, formatDate, formatArea } from '@/utils/formatters';

describe('formatters', () => {
  describe('formatPrice', () => {
    it('formats price correctly', () => {
      expect(formatPrice(1000000)).toBe('$1,000,000');
      expect(formatPrice(999)).toBe('$999');
      expect(formatPrice(1234567.89)).toBe('$1,234,568');
    });

    it('handles zero and negative numbers', () => {
      expect(formatPrice(0)).toBe('$0');
      expect(formatPrice(-1000)).toBe('-$1,000');
    });
  });

  describe('formatDate', () => {
    it('formats date correctly', () => {
      expect(formatDate('2024-01-01T00:00:00Z')).toBe('January 1, 2024');
      expect(formatDate('2023-12-31T23:59:59Z')).toBe('December 31, 2023');
    });

    it('handles invalid dates gracefully', () => {
      expect(() => formatDate('invalid-date')).toThrow();
    });
  });

  describe('formatArea', () => {
    it('formats area correctly', () => {
      expect(formatArea(1000)).toBe('1,000 sqft');
      expect(formatArea(1500.5)).toBe('1,501 sqft');
    });

    it('handles zero and negative numbers', () => {
      expect(formatArea(0)).toBe('0 sqft');
      expect(formatArea(-100)).toBe('-100 sqft');
    });
  });
});
