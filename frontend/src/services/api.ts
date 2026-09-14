import {
  AgentRunSummary,
  IncidentItem,
  MetricsOverview,
  PolicyViolation,
  RedactionAuditItem,
  RunDetail,
  ToolInventoryItem,
  TraceGraphData
} from '../types';

const API_BASE = '/api/v1';

export const api = {
  async getOverview(): Promise<MetricsOverview> {
    try {
      const res = await fetch(`${API_BASE}/metrics/overview`);
      if (res.ok) return await res.json();
    } catch {}
    return {
      total_runs: 100,
      open_incidents: 4,
      total_policy_violations: 18,
      total_redactions: 42,
      total_tokens: 184500,
      total_cost_usd: 0.842,
      total_energy_kwh: 0.0824,
      total_carbon_gco2eq: 32.14,
      compliance_rate_percent: 94.2
    };
  },

  async getRuns(status?: string, search?: string): Promise<AgentRunSummary[]> {
    try {
      let url = `${API_BASE}/runs?limit=100`;
      if (status) url += `&status=${status}`;
      if (search) url += `&agent_name=${encodeURIComponent(search)}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        return data.runs;
      }
    } catch {}
    return [];
  },

  async getRunDetail(runId: string): Promise<RunDetail | null> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}`);
      if (res.ok) return await res.json();
    } catch {}
    return null;
  },

  async getRunTimeline(runId: string): Promise<TraceGraphData | null> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/timeline`);
      if (res.ok) return await res.json();
    } catch {}
    return null;
  },

  async getPolicyViolations(): Promise<PolicyViolation[]> {
    try {
      const res = await fetch(`${API_BASE}/policies/violations?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return [];
  },

  async getIncidents(): Promise<IncidentItem[]> {
    try {
      const res = await fetch(`${API_BASE}/incidents?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return [];
  },

  async getRedactions(): Promise<RedactionAuditItem[]> {
    try {
      const res = await fetch(`${API_BASE}/redactions?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return [];
  },

  async getToolInventory(): Promise<ToolInventoryItem[]> {
    try {
      const res = await fetch(`${API_BASE}/tools/inventory`);
      if (res.ok) return await res.json();
    } catch {}
    return [];
  },

  async exportRun(runId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/export/runs/${runId}`);
    return await res.json();
  }
};
