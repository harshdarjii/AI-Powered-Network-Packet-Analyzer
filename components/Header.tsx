
import React from 'react';
import { LOGO } from '../constants';
import { Theme } from '../types';

interface HeaderProps {
  theme: Theme;
  onToggleTheme: () => void;
  onReset: () => void;
}

const Header: React.FC<HeaderProps> = ({ theme, onToggleTheme, onReset }) => {
  return (
    <header className="sticky top-0 z-[100] w-full border-b border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-[#020617]/70 backdrop-blur-xl transition-all duration-300">
      <div className="container mx-auto px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <div 
          className="flex items-center gap-3 cursor-pointer group"
          onClick={onReset}
        >
          <div className="scale-75 text-slate-900 dark:text-white">
            {LOGO}
          </div>
          <span className="text-xl font-avenir-heavy tracking-tighter text-slate-900 dark:text-white uppercase leading-none">
            DeepTrace
          </span>
        </div>

        {/* Utilities */}
        <div className="flex items-center gap-6">
          <button 
            onClick={onReset}
            className="text-[10px] font-black text-slate-400 hover:text-slate-900 dark:hover:text-white uppercase tracking-widest transition-all"
          >
            New Analysis
          </button>
          
          <div className="w-px h-4 bg-slate-200 dark:bg-slate-800" />

          <button
            onClick={onToggleTheme}
            className="p-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-900 transition-all text-slate-400 dark:text-slate-500"
            aria-label="Toggle theme"
          >
            {theme === 'light' ? (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 9H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
};

export default Header;
