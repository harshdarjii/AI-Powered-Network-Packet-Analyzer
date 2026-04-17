
import { AnalysisResults, AIInsights } from "../types";

export const getAIInsights = async (results: AnalysisResults): Promise<AIInsights> => {
  try {
    const response = await fetch('/api/insights', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(results),
    });

    if (!response.ok) {
      throw new Error('AI Insights request failed');
    }

    return await response.json();
  } catch (error) {
    console.error("AI Forensic Analysis Error:", error);
    return {
      summary: "Neural synthesis engine encountered a processing error.",
      risk_level: "Unknown",
      likely_attack_types: ["Forensic Timeout"],
      explanation: "The intelligence module was unable to correlate the provided telemetry stream in the allotted window.",
      preventive_measures: ["Check network forensic logging pipeline", "Verify API gateway configuration"],
      recommended_actions: ["Restart analysis stream", "Contact system administrator if persistent"]
    };
  }
};
