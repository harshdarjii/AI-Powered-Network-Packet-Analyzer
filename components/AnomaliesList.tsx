
import React from 'react';
import { Anomaly } from '../types';
import { SEVERITY_COLORS } from '../constants';

interface AnomaliesListProps {
  anomalies: Anomaly[];
}

const AnomaliesList: React.FC<AnomaliesListProps> = ({ anomalies }) => {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2rem] shadow-xl flex flex-col h-full overflow-hidden">
      <div className="p-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-900/50">
        <h3 className="text-lg font-avenir-heavy text-slate-900 dark:text-white uppercase tracking-tighter">Heuristics</h3>
        <span className="px-3 py-1 bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400 rounded-full text-[10px] font-black uppercase tracking-widest">
          {anomalies.length} Alerts
        </span>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-8 space-y-6">
        {anomalies.map((anomaly) => (
          <div 
            key={anomaly.id} 
            className="p-6 rounded-2xl border border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-800/20 space-y-4 hover:shadow-md transition-all"
          >
            <div className="flex justify-between items-center">
              <span className={`px-4 py-1 rounded-xl text-[9px] font-black uppercase tracking-widest border ${SEVERITY_COLORS[anomaly.severity] || SEVERITY_COLORS.Unknown}`}>
                {anomaly.severity}
              </span>
              <span className="text-[10px] text-slate-400 uppercase font-black tracking-widest">
                {new Date(anomaly.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
            <div className="space-y-2">
              <h4 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-tight">{anomaly.type}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed font-medium">{anomaly.description}</p>
            </div>
            <div className="pt-2 flex items-center gap-2">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-300" />
              <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-tight">Source: {anomaly.source}</span>
            </div>
          </div>
        ))}
        {anomalies.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 opacity-30">
            <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="text-xs font-black uppercase tracking-[0.3em]">Traffic Stable</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnomaliesList;
