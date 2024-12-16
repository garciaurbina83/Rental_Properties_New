import { createContext, useContext, ReactNode } from 'react';
import { useClerk, useUser } from '@clerk/clerk-react';

interface AuthContextType {
  isAuthenticated: boolean;
  user: any;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const { signOut } = useClerk();
  const { user, isSignedIn } = useUser();

  const value = {
    isAuthenticated: !!isSignedIn,
    user,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
