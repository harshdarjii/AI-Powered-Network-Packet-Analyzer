
import React from 'react';

interface StatsCardProps {
  label: string;
  value: string | number;
  icon: 'activity' | 'database' | 'trending-up' | 'clock';
}

const StatsCard: React.FC<StatsCardProps> = ({ label, value, icon }) => {
  const getIcon = () => {
    switch (icon) {
      case 'activity':
        return (
          <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        );
      case 'database':
        return (
          <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
          </svg>
        );
      case 'trending-up':
        return (
          <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
          </svg>
        );
      case 'clock':
        return (
          <svg className="w-5 h-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 p-8 rounded-[2rem] border border-slate-100 dark:border-slate-800 shadow-xl flex flex-col gap-6 hover:shadow-2xl transition-all hover:-translate-y-1">
      <div className="flex items-center justify-between">
        <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">{label}</span>
        <div className="p-3 bg-slate-50 dark:bg-slate-800 rounded-2xl">
          {getIcon()}
        </div>
      </div>
      <div className="text-3xl font-avenir-heavy text-slate-900 dark:text-white tracking-tighter uppercase">{value}</div>
    </div>
  );
};

export default StatsCard;
