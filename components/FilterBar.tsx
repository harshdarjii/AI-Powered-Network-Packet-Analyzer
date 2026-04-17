
import React from 'react';

interface FilterBarProps {
  filters: { protocol: string; search: string; destSearch: string; severity: string };
  setFilters: React.Dispatch<React.SetStateAction<{ protocol: string; search: string; destSearch: string; severity: string }>>;
  protocols: string[];
}

const FilterBar: React.FC<FilterBarProps> = ({ filters, setFilters, protocols }) => {
  return (
    <div className="p-4 bg-slate-50/50 dark:bg-slate-800/20 border-b border-slate-200 dark:border-slate-800 flex flex-wrap gap-4 items-center">
      <div className="flex-1 min-w-[200px] relative">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          type="text" 
          placeholder="Search source IP..." 
          className="w-full pl-9 pr-4 py-2 text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md focus:ring-1 focus:ring-primary-500 transition-all outline-none"
          value={filters.search}
          onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
        />
      </div>

      <div className="flex-1 min-w-[200px] relative">
        <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          type="text" 
          placeholder="Search destination IP..." 
          className="w-full pl-9 pr-4 py-2 text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md focus:ring-1 focus:ring-primary-500 transition-all outline-none"
          value={filters.destSearch}
          onChange={(e) => setFilters(prev => ({ ...prev, destSearch: e.target.value }))}
        />
      </div>

      <select 
        className="px-3 py-2 text-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-md outline-none focus:ring-1 focus:ring-primary-500"
        value={filters.protocol}
        onChange={(e) => setFilters(prev => ({ ...prev, protocol: e.target.value }))}
      >
        <option value="All">All Protocols</option>
        {protocols.map(p => <option key={p} value={p}>{p}</option>)}
      </select>

      <button 
        onClick={() => setFilters({ protocol: 'All', search: '', destSearch: '', severity: 'All' })}
        className="px-4 py-2 text-sm text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white font-medium"
      >
        Reset
      </button>
    </div>
  );
};

export default FilterBar;
