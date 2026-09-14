import React from 'react';
import { 
  CheckCircle, 
  ShieldAlert, 
  AlertTriangle, 
  EyeOff, 
  Cpu, 
  DollarSign, 
  Zap, 
  Leaf,
  ArrowUpRight,
  Clock
} from 'lucide-react';
import { AgentRunSummary, MetricsOverview, PageView, PolicyViolation } from '../types';

interface OverviewPageProps {
  metrics: MetricsOverview;
  recentRuns: AgentRunSummary[];
  recentViolations: PolicyViolation[];
  onSelectRun: (runId: string) => void;
  onNavigate: (view: PageView) => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  metrics,
  recentRuns,
  recentViolations,
  onSelectRun,
  onNavigate
}) => {
  return (
    <div>
      {/* KPI Grid */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Compliance Rate</span>
            <CheckCircle size={18} color="var(--accent-emerald)" />
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-emerald)' }}>
            {metrics.compliance_rate_percent}%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Across 10 deterministic guardrails
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Active Agent Runs</span>
            <Cpu size={18} color="var(--accent-cyan)" />
          </div>
          <div className="kpi-value">{metrics.total_runs}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Multi-tenant isolated telemetry
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Open Incidents</span>
            <AlertTriangle size={18} color="var(--accent-rose)" />
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-rose)' }}>
            {metrics.open_incidents}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Requires operator triage
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Masked Secrets</span>
            <EyeOff size={18} color="var(--accent-purple)" />
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-purple)' }}>
            {metrics.total_redactions}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            100% seeded PII & API keys masked
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Est. Financial Cost</span>
            <DollarSign size={18} color="var(--accent-amber)" />
          </div>
          <div className="kpi-value">${metrics.total_cost_usd.toFixed(3)}</div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Total {metrics.total_tokens.toLocaleString()} tokens
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Carbon Footprint</span>
            <Leaf size={18} color="#22c55e" />
          </div>
          <div className="kpi-value" style={{ color: '#22c55e' }}>
            {metrics.total_carbon_gco2eq.toFixed(1)} <span style={{ fontSize: '0.9rem' }}>gCO2</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            {metrics.total_energy_kwh.toFixed(4)} kWh compute
          </div>
        </div>
      </div>

      {/* Dual Section: Recent Runs & Policy Violations */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(480px, 1fr))', gap: '1.5rem' }}>
        
        {/* Recent Runs Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem' }}>Recent Agent Executions</h2>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
              onClick={() => onNavigate('live_runs')}
            >
              View All Runs <ArrowUpRight size={12} />
            </button>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Run ID</th>
                  <th>Agent</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.slice(0, 6).map((run) => (
                  <tr key={run.run_id}>
                    <td className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                      {run.run_id}
                    </td>
                    <td>{run.agent_name}</td>
                    <td>
                      <span className={`badge ${
                        run.status === 'success' ? 'badge-success' :
                        run.status === 'violated' ? 'badge-error' :
                        run.status === 'partial' || run.is_partial ? 'badge-partial' : 'badge-info'
                      }`}>
                        {run.is_partial ? 'PARTIAL' : run.status.toUpperCase()}
                      </span>
                    </td>
                    <td>{run.total_duration_ms > 0 ? `${run.total_duration_ms.toFixed(0)} ms` : '—'}</td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-secondary"
                        style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}
                        onClick={() => onSelectRun(run.run_id)}
                      >
                        Inspect Trace
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Security & Policy Violations Panel */}
        <div className="glass-panel" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.1rem' }}>Active Guardrail Violations</h2>
            <button
              type="button"
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }}
              onClick={() => onNavigate('policy_violations')}
            >
              View Triage Feed <ArrowUpRight size={12} />
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {recentViolations.slice(0, 4).map((v) => (
              <div 
                key={v.violation_id}
                style={{
                  padding: '0.85rem 1rem',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--border-subtle)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '0.35rem'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                    {v.rule_name}
                  </span>
                  <span className={`badge ${
                    v.severity === 'CRITICAL' ? 'badge-critical' :
                    v.severity === 'HIGH' ? 'badge-error' :
                    v.severity === 'MEDIUM' ? 'badge-warning' : 'badge-info'
                  }`}>
                    {v.severity}
                  </span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {v.evidence}
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  <span>Run: <strong className="font-mono">{v.run_id}</strong></span>
                  <span>Confidence: {(v.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
