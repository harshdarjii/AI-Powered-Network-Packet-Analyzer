
import React, { useState, useRef } from 'react';
import { LOGO } from '../constants';

interface UploadAreaProps {
  onUpload: (file: File) => void;
  isLoading: boolean;
}

const Landing: React.FC<UploadAreaProps> = ({ onUpload, isLoading }) => {
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) validateAndUpload(file);
  };

  const validateAndUpload = (file: File) => {
    const validExtensions = ['.pcap', '.pcapng', '.csv'];
    const fileName = file.name.toLowerCase();
    if (validExtensions.some(ext => fileName.endsWith(ext))) {
      onUpload(file);
    } else {
      alert("Invalid file type. Please upload a .pcap, .pcapng, or .csv file.");
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[80vh] gap-12 animate-in fade-in duration-1000">
        <div className="relative z-10 flex flex-col items-center gap-10">
          <div className="relative flex items-center justify-center">
            <div className="w-32 h-32 border-2 border-slate-200 dark:border-slate-800 rounded-full" />
            <div className="absolute inset-0 w-32 h-32 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
            <div className="absolute scale-75 opacity-20">
              {LOGO}
            </div>
          </div>
          <div className="text-center space-y-4">
            <h3 className="text-2xl font-avenir-heavy text-slate-900 dark:text-white uppercase tracking-tighter">Parsing Forensics</h3>
            <p className="text-slate-500 dark:text-slate-400 font-medium max-w-sm mx-auto leading-relaxed text-sm">
              Our neural engine is mapping protocol entropy and identifying traffic signatures.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative min-h-[90vh] flex flex-col items-center justify-center px-6 py-20 overflow-hidden">

      {/* Hero Content Container */}
      <div className="relative z-10 max-w-5xl w-full text-center space-y-24">

        {/* Headline Section */}
        <div className="space-y-10 animate-in fade-in slide-in-from-bottom-8 duration-700 fill-mode-both">
          <h1 className="text-7xl md:text-9xl font-avenir-heavy text-slate-900 dark:text-white uppercase leading-[0.85] tracking-tighter">
            ELITE NETWORK <br />
            <span className="text-gradient-blue">FORENSICS.</span>
          </h1>
          <p className="text-xl md:text-2xl text-slate-500 dark:text-slate-400 font-medium leading-relaxed max-w-3xl mx-auto tracking-tight opacity-80">
            Autonomous packet analysis and threat intelligence. DeepTrace reconstructs network sessions to identify exfiltration and lateral movement in real-time.
          </p>
        </div>

        {/* Functionality Overview - Information Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-left animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
          <div className="space-y-4 p-8 bg-white/50 dark:bg-slate-900/50 rounded-3xl border border-slate-200/50 dark:border-slate-800/50 backdrop-blur-sm shadow-sm group hover:border-primary-500/30 transition-all">
            <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-900 dark:text-white group-hover:bg-primary-500 group-hover:text-white transition-all">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h4 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Protocol Ingestion</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
              Upload raw PCAP/CSV telemetry. DeepTrace automatically extracts flows, packet counts, and byte distributions for deep protocol dissection.
            </p>
          </div>
          <div className="space-y-4 p-8 bg-white/50 dark:bg-slate-900/50 rounded-3xl border border-slate-200/50 dark:border-slate-800/50 backdrop-blur-sm shadow-sm group hover:border-primary-500/30 transition-all">
            <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-900 dark:text-white group-hover:bg-primary-500 group-hover:text-white transition-all">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h4 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Heuristic Mapping</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
              Our forensic engine detects port scans, unusual data Producer/Consumer ratios, and identifies suspicious communication endpoints.
            </p>
          </div>
          <div className="space-y-4 p-8 bg-white/50 dark:bg-slate-900/50 rounded-3xl border border-slate-200/50 dark:border-slate-800/50 backdrop-blur-sm shadow-sm group hover:border-primary-500/30 transition-all">
            <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center text-slate-900 dark:text-white group-hover:bg-primary-500 group-hover:text-white transition-all">
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <h4 className="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Neural Synthesis</h4>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-medium leading-relaxed">
              Leverage Gemini AI to correlate findings across the forensic stream, producing executive risk reports and preventive action directives.
            </p>
          </div>
        </div>

        {/* Upload Action Area */}
        <div className="max-w-2xl mx-auto w-full animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-500 fill-mode-both">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              relative w-full p-1.5 rounded-[3rem] border border-dashed transition-all duration-700 cursor-pointer group/upload
              ${isDragging
                ? 'border-primary-500 bg-primary-50/30 dark:bg-primary-900/10 scale-105 shadow-2xl'
                : 'border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-slate-400 dark:hover:border-slate-600 shadow-xl hover:shadow-2xl hover:-translate-y-1'}
            `}
          >
            <input
              type="file"
              ref={fileInputRef}
              className="hidden"
              onChange={(e) => e.target.files?.[0] && validateAndUpload(e.target.files[0])}
              accept=".pcap,.pcapng,.csv"
            />
            <div className="p-12 md:p-16 text-center space-y-10 flex flex-col items-center">
              <div className="w-24 h-24 rounded-[2.2rem] bg-slate-900 dark:bg-white text-white dark:text-slate-900 flex items-center justify-center shadow-[0_20px_50px_rgba(0,0,0,0.15)] group-hover/upload:scale-110 group-hover/upload:rotate-3 transition-all duration-500">
                <svg className="w-12 h-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <div className="space-y-3">
                <h4 className="text-3xl font-avenir-heavy text-slate-900 dark:text-white tracking-tighter uppercase">Initiate Analysis</h4>
                <p className="text-base text-slate-500 dark:text-slate-400 font-medium tracking-tight">Stream PCAP, PCAPNG, or CSV telemetry to the core</p>
              </div>
              <div className="flex gap-4">
                {['PCAP', 'PCAPNG', 'CSV'].map(ext => (
                  <span key={ext} className="px-5 py-2 bg-slate-100/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-2xl text-[11px] font-black text-slate-500 dark:text-slate-400 tracking-[0.2em]">{ext}</span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-16 flex flex-wrap justify-center items-center gap-x-16 gap-y-6 opacity-40">
            {/* <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-primary-500" />
              <span className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400">Secure AES-256</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400">Neural Node 4.1</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
              <span className="text-[11px] font-black uppercase tracking-[0.3em] text-slate-400">Zero Trust Ingestion</span>
            </div> */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Landing;
