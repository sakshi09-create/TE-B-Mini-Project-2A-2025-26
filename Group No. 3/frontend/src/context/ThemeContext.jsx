// src/contexts/ThemeContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDark, setIsDark] = useState(true); // Default to dark theme

  useEffect(() => {
    // Load theme from localStorage on component mount
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDark(savedTheme === 'dark');
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDark(prefersDark);
    }
  }, []);

  useEffect(() => {
    // Save theme to localStorage and apply to document
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    document.documentElement.classList.toggle('dark', isDark);
  }, [isDark]);

  const toggleTheme = () => {
    setIsDark(!isDark);
  };

  const theme = {
    isDark,
    toggleTheme,
    colors: {
      // Background colors
      bg: {
        primary: isDark ? '#131314' : '#ffffff',
        secondary: isDark ? '#1f2937' : '#f9fafb',
        tertiary: isDark ? '#374151' : '#f3f4f6',
        card: isDark ? '#1f2937' : '#ffffff',
        overlay: isDark ? 'rgba(0, 0, 0, 0.6)' : 'rgba(255, 255, 255, 0.8)',
      },
      // Text colors
      text: {
        primary: isDark ? '#ffffff' : '#111827',
        secondary: isDark ? '#d1d5db' : '#6b7280',
        tertiary: isDark ? '#9ca3af' : '#4b5563',
        accent: isDark ? '#60a5fa' : '#3b82f6',
      },
      // Border colors
      border: {
        primary: isDark ? '#374151' : '#e5e7eb',
        secondary: isDark ? '#4b5563' : '#d1d5db',
        accent: isDark ? '#60a5fa' : '#3b82f6',
      },
      // Status colors (remain consistent across themes)
      status: {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6',
      }
    }
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
