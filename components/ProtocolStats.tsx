
import React from 'react';

interface ProtocolStatsProps {
  counts: Record<string, number>;
  bytes: Record<string, number>;
  totalFlows: number;
}

const ProtocolStats: React.FC<ProtocolStatsProps> = ({ counts, bytes, totalFlows }) => {
  const sortedProtocols = (Object.entries(counts) as [string, number][]).sort((a, b) => b[1] - a[1]);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2rem] p-8 shadow-xl">
      <div className="flex items-center justify-between mb-10">
        <h3 className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em]">Protocol Mapping</h3>
        <div className="px-3 py-1 bg-slate-50 dark:bg-slate-800 rounded-lg text-[10px] font-bold text-slate-400 tracking-wider">
          {sortedProtocols.length} Protocols
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
        {sortedProtocols.map(([proto, count]) => {
          const percentage = (count / totalFlows) * 100;
          return (
            <div key={proto} className="space-y-3 group">
              <div className="flex justify-between items-end">
                <div className="flex flex-col">
                  <span className="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1">Source Tag</span>
                  <span className="text-base font-avenir-heavy text-slate-900 dark:text-white uppercase tracking-tight">{proto}</span>
                </div>
                <div className="text-right flex flex-col items-end">
                  <span className="text-sm font-bold text-slate-900 dark:text-white">{percentage.toFixed(1)}%</span>
                  <span className="text-[10px] text-slate-400 font-medium">{count.toLocaleString()} sessions</span>
                </div>
              </div>
              <div className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-primary-500 group-hover:bg-primary-400 rounded-full transition-all duration-700 ease-out" 
                  style={{ width: `${percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProtocolStats;
