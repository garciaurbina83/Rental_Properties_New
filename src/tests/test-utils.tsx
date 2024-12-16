import React from 'react';
import { render as rtlRender } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ClerkProvider } from '@clerk/nextjs';

function render(ui: React.ReactElement, { ...renderOptions } = {}) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <ClerkProvider>{children}</ClerkProvider>;
  }
  return {
    user: userEvent.setup(),
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}

// re-export everything
export * from '@testing-library/react';

// override render method
export { render };
