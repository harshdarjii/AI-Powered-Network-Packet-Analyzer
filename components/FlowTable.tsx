
import React from 'react';
import { NetworkFlow } from '../types';

interface FlowTableProps {
  flows: NetworkFlow[];
}

const FlowTable: React.FC<FlowTableProps> = ({ flows }) => {
  if (flows.length === 0) {
    return (
      <div className="p-20 text-center text-slate-500 dark:text-slate-400">
        No flows match the current filters
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm border-collapse">
        <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 dark:text-slate-400 font-medium">
          <tr>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">Protocol</th>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">Source</th>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800 text-center">→</th>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">Destination</th>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">Length</th>
            <th className="px-4 py-3 border-b border-slate-200 dark:border-slate-800">Info</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
          {flows.map((flow, idx) => (
            <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors">
              <td className="px-4 py-3">
                <span className={`
                  px-2 py-0.5 rounded text-[10px] font-bold uppercase
                  ${flow.protocol === 'TCP' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300' : 
                    flow.protocol === 'UDP' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300' :
                    'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300'}
                `}>
                  {flow.protocol}
                </span>
              </td>
              <td className="px-4 py-3 font-mono text-xs">{flow.source_ip}:{flow.source_port}</td>
              <td className="px-4 py-3 text-center text-slate-300">→</td>
              <td className="px-4 py-3 font-mono text-xs">{flow.destination_ip}:{flow.destination_port}</td>
              <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{flow.length}</td>
              <td className="px-4 py-3 text-slate-500 max-w-[200px] truncate" title={flow.info}>{flow.info}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FlowTable;
