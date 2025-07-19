import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
  role: 'admin' | 'developer' | 'user';
  permissions: string[];
}

interface UserStore {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (profile: Partial<User>) => Promise<void>;
}

export const useUserStore = create<UserStore>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      
      login: async (email: string, password: string) => {
        // Simulate API call
        const mockUser: User = {
          id: 'user_001',
          name: '开发者',
          email,
          role: 'developer',
          permissions: ['agent:create', 'agent:edit', 'agent:deploy'],
        };
        
        set({ 
          user: mockUser, 
          isAuthenticated: true 
        });
      },
      
      logout: () => {
        set({ 
          user: null, 
          isAuthenticated: false 
        });
      },
      
      updateProfile: async (profile: Partial<User>) => {
        const { user } = get();
        if (user) {
          set({ 
            user: { ...user, ...profile } 
          });
        }
      },
    }),
    {
      name: 'user-store',
    }
  )
);