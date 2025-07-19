import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface ThemeStore {
  isDarkMode: boolean;
  primaryColor: string;
  toggleTheme: () => void;
  setPrimaryColor: (color: string) => void;
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      isDarkMode: false,
      primaryColor: '#1890ff',
      
      toggleTheme: () => set((state) => ({ 
        isDarkMode: !state.isDarkMode 
      })),
      
      setPrimaryColor: (color: string) => set({ 
        primaryColor: color 
      }),
    }),
    {
      name: 'theme-store',
    }
  )
);