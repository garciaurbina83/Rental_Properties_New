import '@testing-library/jest-dom';

// Mock next/router
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '',
      query: {},
      asPath: '',
      push: jest.fn(),
      replace: jest.fn(),
      reload: jest.fn(),
      back: jest.fn(),
      prefetch: jest.fn(),
      beforePopState: jest.fn(),
      events: {
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
      },
      isFallback: false,
    };
  },
}));

// Mock next/image
jest.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => {
    // eslint-disable-next-line @next/next/no-img-element
    return <img {...props} alt={props.alt} />;
  },
}));

// Mock Clerk
jest.mock('@clerk/nextjs', () => ({
  auth: () => new Promise((resolve) => resolve({ userId: 'user_123' })),
  ClerkProvider: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useUser: () => ({
    isSignedIn: true,
    user: {
      id: 'user_123',
      fullName: 'Test User',
      primaryEmailAddress: 'test@example.com',
    },
  }),
  useClerk: () => ({
    signOut: jest.fn(),
  }),
}));

// Supress console errors during tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});
