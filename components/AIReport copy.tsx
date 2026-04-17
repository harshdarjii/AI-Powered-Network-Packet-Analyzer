
import React from 'react';
import { AIInsights } from '../types';
import { SEVERITY_COLORS } from '../constants';

interface AIReportProps {
  insights: AIInsights | null;
  isLoading: boolean;
  onClose: () => void;
}

const AIReport: React.FC<AIReportProps> = ({ insights, isLoading, onClose }) => {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6">
      <div 
        className="absolute inset-0 bg-slate-950/20 backdrop-blur-sm transition-opacity" 
        onClick={onClose} 
      />
      
      <div className="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-[2.5rem] shadow-[0_40px_100px_-20px_rgba(0,0,0,0.3)] overflow-hidden flex flex-col animate-in zoom-in-95 fade-in duration-300 border border-slate-200 dark:border-slate-800">
        
        {/* Modal Header */}
        <div className="px-10 py-8 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 flex items-center justify-center rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-lg">
              <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h2 className="text-xl font-avenir-heavy text-slate-900 dark:text-white uppercase tracking-tight leading-none">AI Security Assistant</h2>
              <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mt-1 opacity-60">Synthesis Engine v4.1</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-400 transition-all"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-24 gap-8">
              <div className="w-12 h-12 border-2 border-slate-200 dark:border-slate-800 border-t-primary-500 rounded-full animate-spin" />
              <div className="text-center">
                <h4 className="text-lg font-bold text-slate-900 dark:text-white uppercase tracking-tight">Synthesizing Telemetry</h4>
                <p className="text-xs text-slate-500 dark:text-slate-400 font-medium">Correlating signatures with global threat datasets...</p>
              </div>
            </div>
          ) : insights ? (
            <div className="p-10 space-y-12">
              <section className="space-y-4">
                <div className="flex items-center gap-2">
                  <span className={`px-4 py-1 rounded-full text-[10px] font-black uppercase tracking-widest ${SEVERITY_COLORS[insights.risk_level] || SEVERITY_COLORS.Unknown}`}>
                    {insights.risk_level} RISK
                  </span>
                </div>
                <h3 className="text-2xl font-medium text-slate-800 dark:text-slate-200 leading-snug tracking-tight">
                  {insights.summary}
                </h3>
              </section>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div className="space-y-8">
                  <div className="space-y-4">
                    <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Deep Analysis</h4>
                    <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed font-medium">
                      {insights.explanation}
                    </p>
                  </div>

                  <div className="space-y-4">
                    <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Identified Attack Profiles</h4>
                    <div className="flex flex-wrap gap-2">
                      {insights.likely_attack_types.map((type, i) => (
                        <span key={i} className="px-3 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-[11px] font-bold text-slate-600 dark:text-slate-300">
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="space-y-8">
                  <div className="p-6 bg-slate-50 dark:bg-slate-800/40 rounded-2xl border border-slate-100 dark:border-slate-800 space-y-4">
                    <h4 className="text-[11px] font-black text-slate-900 dark:text-white uppercase tracking-widest">Response Strategy</h4>
                    <ul className="space-y-3">
                      {insights.recommended_actions.map((action, i) => (
                        <li key={i} className="flex gap-3 text-xs font-bold text-slate-700 dark:text-slate-300">
                          <span className="text-primary-500">→</span>
                          {action}
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div className="p-6 space-y-4">
                    <h4 className="text-[11px] font-black text-slate-400 uppercase tracking-widest">Systemic Hardening</h4>
                    <ul className="space-y-3">
                      {insights.preventive_measures.map((measure, i) => (
                        <li key={i} className="flex gap-3 text-xs text-slate-500 dark:text-slate-400 font-medium">
                          <span className="w-1.5 h-1.5 mt-1.5 rounded-full bg-slate-300 dark:bg-slate-700 flex-shrink-0" />
                          {measure}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          ) : null}
        </div>

        <div className="px-10 py-6 bg-slate-50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-800 flex justify-end">
          <button 
            onClick={onClose}
            className="px-6 py-2.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-black uppercase tracking-widest hover:opacity-90 active:scale-95 transition-all"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIReport;
