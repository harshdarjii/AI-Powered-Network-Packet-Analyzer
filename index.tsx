
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { Theme, AnalysisResults, AIInsights } from './types';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import Landing from './components/UploadArea';
import AIReport from './components/AIReport';

const App: React.FC = () => {
  const [theme, setTheme] = useState<Theme>('light');
  const [analysisData, setAnalysisData] = useState<AnalysisResults | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isAiLoading, setIsAiLoading] = useState(false);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);
  const [status, setStatus] = useState<'online' | 'offline'>('offline');

  useEffect(() => {
    // Sync theme
    const savedTheme = (localStorage.getItem('theme') as Theme) || 'light';
    setTheme(savedTheme);
    document.documentElement.classList.toggle('dark', savedTheme === 'dark');

    // Check system status
    const checkStatus = async () => {
      try {
        const res = await fetch('/status');
        const data = await res.json();
        if (data.status === 'online') setStatus('online');
      } catch {
        setStatus('offline');
      }
    };
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  const handleFileUpload = async (file: File) => {
    setIsAnalyzing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Analysis payload failed');
      }

      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Core Analysis Error:', error);
      alert('Neural synthesis engine failed. Ensure the Python backend is active.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRequestAI = async () => {
    if (!analysisData) return;
    setIsAiLoading(true);
    setIsAiModalOpen(true);
    
    try {
      const response = await fetch('/api/insights', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analysisData),
      });

      if (!response.ok) throw new Error('AI Intelligence request failed');
      const insights = await response.json();
      setAiInsights(insights);
    } catch (e) {
      console.error(e);
      setAiInsights({
        summary: "Intelligence synthesis interrupted.",
        risk_level: "Unknown",
        likely_attack_types: ["API Protocol Error"],
        explanation: "The AI Security Assistant was unable to process the forensic stream.",
        preventive_measures: ["Audit backend connectivity"],
        recommended_actions: ["Manually review high-severity anomalies"]
      });
    } finally {
      setIsAiLoading(false);
    }
  };

  return (
    <div className="min-h-screen transition-colors duration-500 bg-[#F8FAFC] dark:bg-[#020617]">
      <Header 
        theme={theme} 
        onToggleTheme={toggleTheme} 
        onReset={() => {
          setAnalysisData(null);
          setAiInsights(null);
          setIsAiModalOpen(false);
        }}
      />
      
      <main className="container mx-auto px-6 py-10 max-w-7xl">
        {!analysisData ? (
          <Landing onUpload={handleFileUpload} isLoading={isAnalyzing} />
        ) : (
          <Dashboard 
            data={analysisData} 
            onRequestAI={handleRequestAI}
          />
        )}
      </main>

      {isAiModalOpen && (
        <AIReport 
          insights={aiInsights} 
          isLoading={isAiLoading} 
          onClose={() => setIsAiModalOpen(false)} 
        />
      )}
      
      {/* System Pulse Indicator */}
      <div className="fixed bottom-6 right-6 flex items-center gap-2.5 px-4 py-2 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200 dark:border-slate-800 rounded-full shadow-sm z-50">
        <span className={`w-1.5 h-1.5 rounded-full ${status === 'online' ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]' : 'bg-red-500'}`} />
        <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-slate-500 dark:text-slate-400">
          Node: {status}
        </span>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root')!);
root.render(<App />);
