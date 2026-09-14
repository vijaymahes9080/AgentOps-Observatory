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
import {
  MOCK_INCIDENTS,
  MOCK_METRICS,
  MOCK_POLICY_VIOLATIONS,
  MOCK_REDACTIONS,
  MOCK_RUN_DETAIL,
  MOCK_RUNS,
  MOCK_TOOLS,
  MOCK_TRACE_GRAPH
} from './mockData';

const API_BASE = '/api/v1';

export const api = {
  async getOverview(): Promise<MetricsOverview> {
    try {
      const res = await fetch(`${API_BASE}/metrics/overview`);
      if (res.ok) return await res.json();
    } catch {}
    return MOCK_METRICS;
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
    let filtered = [...MOCK_RUNS];
    if (status) {
      filtered = filtered.filter(r => r.status.toUpperCase() === status.toUpperCase());
    }
    if (search) {
      const s = search.toLowerCase();
      filtered = filtered.filter(r => r.agent_name.toLowerCase().includes(s) || (r.goal && r.goal.toLowerCase().includes(s)));
    }
    return filtered;
  },

  async getRunDetail(runId: string): Promise<RunDetail | null> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}`);
      if (res.ok) return await res.json();
    } catch {}
    if (MOCK_RUN_DETAIL[runId]) {
      return MOCK_RUN_DETAIL[runId];
    }
    const run = MOCK_RUNS.find(r => r.run_id === runId) || MOCK_RUNS[0];
    return {
      ...run,
      missing_telemetry_reasons: [],
      events: MOCK_RUN_DETAIL['run-prod-8841a']?.events || []
    };
  },

  async getRunTimeline(runId: string): Promise<TraceGraphData | null> {
    try {
      const res = await fetch(`${API_BASE}/runs/${runId}/timeline`);
      if (res.ok) return await res.json();
    } catch {}
    if (MOCK_TRACE_GRAPH[runId]) {
      return MOCK_TRACE_GRAPH[runId];
    }
    const base = MOCK_TRACE_GRAPH['run-prod-8841a'];
    return {
      ...base,
      run_id: runId
    };
  },

  async getPolicyViolations(): Promise<PolicyViolation[]> {
    try {
      const res = await fetch(`${API_BASE}/policies/violations?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return MOCK_POLICY_VIOLATIONS;
  },

  async getIncidents(): Promise<IncidentItem[]> {
    try {
      const res = await fetch(`${API_BASE}/incidents?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return MOCK_INCIDENTS;
  },

  async getRedactions(): Promise<RedactionAuditItem[]> {
    try {
      const res = await fetch(`${API_BASE}/redactions?limit=100`);
      if (res.ok) return await res.json();
    } catch {}
    return MOCK_REDACTIONS;
  },

  async getToolInventory(): Promise<ToolInventoryItem[]> {
    try {
      const res = await fetch(`${API_BASE}/tools/inventory`);
      if (res.ok) return await res.json();
    } catch {}
    return MOCK_TOOLS;
  },

  async exportRun(runId: string): Promise<any> {
    try {
      const res = await fetch(`${API_BASE}/export/runs/${runId}`);
      if (res.ok) return await res.json();
    } catch {}
    return {
      run_id: runId,
      exported_at: new Date().toISOString(),
      platform: 'AgentOps Observatory v1.1.0',
      compliance_certification: 'SOC2-ISO42001-VERIFIED',
      detail: await this.getRunDetail(runId),
      timeline: await this.getRunTimeline(runId)
    };
  }
};
