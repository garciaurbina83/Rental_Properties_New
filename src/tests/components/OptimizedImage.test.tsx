import React from 'react';
import { render, screen } from '../test-utils';
import { OptimizedImage } from '@/components/OptimizedImage';

describe('OptimizedImage', () => {
  const defaultProps = {
    src: 'test-image.jpg',
    alt: 'Test Image',
    width: 400,
    height: 300,
  };

  it('renders with correct props', () => {
    render(<OptimizedImage {...defaultProps} />);
    
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('src', expect.stringContaining(defaultProps.src));
    expect(image).toHaveAttribute('alt', defaultProps.alt);
    expect(image).toHaveAttribute('width', defaultProps.width.toString());
    expect(image).toHaveAttribute('height', defaultProps.height.toString());
  });

  it('applies lazy loading by default', () => {
    render(<OptimizedImage {...defaultProps} />);
    
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('loading', 'lazy');
  });

  it('uses eager loading when priority is true', () => {
    render(<OptimizedImage {...defaultProps} priority />);
    
    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('loading', 'eager');
  });

  it('applies custom className', () => {
    const className = 'custom-class';
    render(<OptimizedImage {...defaultProps} className={className} />);
    
    const container = screen.getByRole('img').parentElement;
    expect(container).toHaveClass(className);
  });

  it('maintains aspect ratio', () => {
    render(<OptimizedImage {...defaultProps} />);
    
    const container = screen.getByRole('img').parentElement;
    expect(container).toHaveStyle({ aspectRatio: defaultProps.width / defaultProps.height });
  });
});
