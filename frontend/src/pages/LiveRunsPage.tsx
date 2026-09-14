import React, { useState } from 'react';
import { PlayCircle, AlertTriangle, ArrowRight, Filter } from 'lucide-react';
import { AgentRunSummary } from '../types';

interface LiveRunsPageProps {
  runs: AgentRunSummary[];
  onSelectRun: (runId: string) => void;
}

export const LiveRunsPage: React.FC<LiveRunsPageProps> = ({ runs, onSelectRun }) => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const filteredRuns = runs.filter((r) => {
    const matchesStatus = 
      statusFilter === 'all' ||
      (statusFilter === 'partial' ? r.is_partial : r.status === statusFilter);
    const matchesSearch =
      r.run_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      r.agent_name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      {/* Header Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem' }}>Agent Execution Telemetry Stream</h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Real-time feed of multi-agent spans, tool executions, and partial traces.
          </p>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status:</span>
          {['all', 'success', 'violated', 'error', 'partial'].map((st) => (
            <button
              key={st}
              type="button"
              className={`btn ${statusFilter === st ? 'btn-primary' : 'btn-secondary'}`}
              style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
              onClick={() => setStatusFilter(st)}
            >
              {st.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Run ID</th>
              <th>Agent Identity</th>
              <th>Status</th>
              <th>Telemetry Integrity</th>
              <th>Duration</th>
              <th>Tokens</th>
              <th>Cost ($)</th>
              <th>Carbon</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredRuns.map((r) => (
              <tr key={r.run_id}>
                <td className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
                  {r.run_id}
                </td>
                <td style={{ fontWeight: 500 }}>{r.agent_name}</td>
                <td>
                  <span className={`badge ${
                    r.status === 'success' ? 'badge-success' :
                    r.status === 'violated' ? 'badge-error' :
                    r.status === 'partial' || r.is_partial ? 'badge-partial' : 'badge-info'
                  }`}>
                    {r.is_partial ? 'PARTIAL' : r.status.toUpperCase()}
                  </span>
                </td>
                <td>
                  {r.is_partial ? (
                    <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--accent-amber)', fontSize: '0.75rem', fontWeight: 600 }}>
                      <AlertTriangle size={13} /> Missing Spans
                    </span>
                  ) : (
                    <span style={{ color: 'var(--accent-emerald)', fontSize: '0.75rem' }}>
                      Complete (100%)
                    </span>
                  )}
                </td>
                <td>{r.total_duration_ms > 0 ? `${r.total_duration_ms.toFixed(0)} ms` : '—'}</td>
                <td>{r.total_tokens > 0 ? r.total_tokens.toLocaleString() : '—'}</td>
                <td>${r.total_cost_usd.toFixed(4)}</td>
                <td style={{ color: '#22c55e', fontSize: '0.8rem' }}>
                  {r.total_carbon_gco2eq > 0 ? `${r.total_carbon_gco2eq.toFixed(2)} g` : '0 g'}
                </td>
                <td>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                    onClick={() => onSelectRun(r.run_id)}
                  >
                    View DAG <ArrowRight size={12} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
