
import React, { useState, useMemo } from 'react';
import { AnalysisResults, NetworkFlow } from '../types';
import StatsCard from './StatsCard';
import ProtocolStats from './ProtocolStats';
import FlowTable from './FlowTable';
import AnomaliesList from './AnomaliesList';
import FilterBar from './FilterBar';

interface DashboardProps {
  data: AnalysisResults;
  onRequestAI: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ data, onRequestAI }) => {
  const [filters, setFilters] = useState({
    protocol: 'All',
    search: '',
    destSearch: '',
    severity: 'All'
  });

  const filteredFlows = useMemo(() => {
    return data.flows.filter(flow => {
      const matchesProtocol = filters.protocol === 'All' || flow.protocol === filters.protocol;
      const matchesSource = flow.source_ip.toLowerCase().includes(filters.search.toLowerCase());
      const matchesDest = flow.destination_ip.toLowerCase().includes(filters.destSearch.toLowerCase());
      return matchesProtocol && matchesSource && matchesDest;
    });
  }, [data.flows, filters]);

  const filteredAnomalies = useMemo(() => {
    return data.anomalies.filter(a => {
      return filters.severity === 'All' || a.severity === filters.severity;
    });
  }, [data.anomalies, filters.severity]);

  return (
    <div className="space-y-12 animate-in fade-in duration-1000 pb-20">
      
      {/* 1. Intelligence Command (AI Insights CTA) */}
      <section className="relative overflow-hidden p-12 bg-slate-900 dark:bg-slate-900 rounded-[3rem] shadow-2xl border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-10 group">
        <div className="absolute top-0 right-0 -mt-20 -mr-20 w-[500px] h-[500px] bg-primary-500/10 blur-[120px] group-hover:bg-primary-500/20 transition-all duration-1000" />
        <div className="relative z-10 flex flex-col gap-5">
          <div className="flex items-center gap-4">
            <span className="px-4 py-1.5 bg-primary-500/10 text-primary-400 rounded-full text-[10px] font-black uppercase tracking-[0.25em] border border-primary-500/20">Telemetry Correlated</span>
            <div className="flex items-center gap-2">
               <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
               <span className="text-[10px] text-emerald-400 font-black uppercase tracking-widest">Autonomous Mode</span>
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-avenir-heavy text-white uppercase tracking-tighter leading-tight">
            Autonomous <span className="text-gradient-blue">Intelligence</span>
          </h1>
          <p className="text-slate-400 font-medium max-w-xl text-base leading-relaxed">
            Correlate {data.summary.total_flows.toLocaleString()} network sessions against known attack signatures and identify hidden exfiltration tunnels.
          </p>
        </div>
        <div className="relative z-10">
          <button 
            onClick={onRequestAI}
            className="flex items-center gap-4 px-10 py-6 bg-white text-slate-900 rounded-[2rem] font-black uppercase text-xs tracking-[0.2em] hover:scale-105 hover:-rotate-1 active:scale-95 transition-all shadow-[0_20px_40px_rgba(255,255,255,0.1)] hover:shadow-primary-500/40"
          >
            <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Synthesize Insights
          </button>
        </div>
      </section>

      {/* 2. Core Telemetry Matrix */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
        <StatsCard 
          label="Forensic Sessions" 
          value={data.summary.total_flows.toLocaleString()} 
          icon="activity" 
        />
        <StatsCard 
          label="Stream Volume" 
          value={`${(data.summary.total_bytes / 1024 / 1024).toFixed(2)} MB`} 
          icon="database" 
        />
        <StatsCard 
          label="Flow Velocity" 
          value={`${(data.summary.avg_flow_size / 1024).toFixed(1)} KB/s`} 
          icon="trending-up" 
        />
        <StatsCard 
          label="Collection Window" 
          value={data.summary.duration} 
          icon="clock" 
        />
      </section>

      {/* 3. Distribution & Network Producers */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8 h-full">
          <ProtocolStats 
            counts={data.protocol_distribution} 
            bytes={data.protocol_bytes_distribution} 
            totalFlows={data.summary.total_flows}
          />
        </div>
        <div className="lg:col-span-4 h-full">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[2.5rem] p-10 h-full shadow-xl flex flex-col">
            <h3 className="text-[11px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-10">Primary Sources</h3>
            <div className="space-y-6 flex-1">
              {data.top_talkers.map((talker, idx) => (
                <div key={idx} className="flex items-center justify-between p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-transparent hover:border-slate-100 dark:hover:border-slate-700 transition-all group">
                  <div className="flex flex-col gap-1">
                    <span className="text-sm font-mono font-bold text-slate-900 dark:text-white group-hover:text-primary-500 transition-colors">{talker.ip}</span>
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{talker.flows} sessions mapped</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-black text-slate-900 dark:text-white">{(talker.bytes / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 4. Forensic Deep Dive */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 h-full">
          <AnomaliesList anomalies={filteredAnomalies} />
        </div>
        <div className="lg:col-span-8 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-[3rem] shadow-2xl overflow-hidden flex flex-col h-full min-h-[600px]">
          <div className="p-10 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-white dark:bg-slate-900">
            <h3 className="text-xl font-avenir-heavy text-slate-900 dark:text-white uppercase tracking-tighter">Forensic Event Stream</h3>
            <span className="px-4 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-full text-[10px] font-black text-slate-500 dark:text-slate-400 uppercase tracking-widest">
              Displaying {filteredFlows.length} Nodes
            </span>
          </div>
          <FilterBar filters={filters} setFilters={setFilters} protocols={Object.keys(data.protocol_distribution)} />
          <div className="flex-1 overflow-hidden">
            <FlowTable flows={filteredFlows} />
          </div>
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
