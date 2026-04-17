
export interface NetworkFlow {
  timestamp: string;
  source_ip: string;
  destination_ip: string;
  source_port: number;
  destination_port: number;
  protocol: string;
  length: number;
  info: string;
  packets?: number;
}

export interface Anomaly {
  id: string;
  type: string;
  severity: 'Low' | 'Medium' | 'High' | 'Critical';
  description: string;
  source: string;
  timestamp: string;
}

export interface ProtocolStats {
  protocol: string;
  count: number;
  bytes: number;
  packets: number;
}

export interface AnalysisResults {
  summary: {
    total_flows: number;
    total_packets: number;
    total_bytes: number;
    duration: string;
    avg_flow_size: number;
  };
  protocol_distribution: Record<string, number>;
  protocol_bytes_distribution: Record<string, number>;
  protocol_packets_distribution: Record<string, number>;
  flows: NetworkFlow[];
  anomalies: Anomaly[];
  top_talkers: { ip: string; bytes: number; flows: number }[];
}

export interface AIInsights {
  summary: string;
  risk_level: 'Low' | 'Medium' | 'High' | 'Critical' | 'Unknown';
  likely_attack_types: string[];
  explanation: string;
  preventive_measures: string[];
  recommended_actions: string[];
}

export type Theme = 'light' | 'dark';
