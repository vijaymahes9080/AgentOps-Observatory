import React from 'react';
import { Search, Shield, RefreshCw, Radio } from 'lucide-react';
import { PageView } from '../types';

interface HeaderProps {
  currentView: PageView;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onRefresh: () => void;
  selectedRunId?: string | null;
}

export const Header: React.FC<HeaderProps> = ({
  currentView,
  searchQuery,
  onSearchChange,
  onRefresh,
  selectedRunId
}) => {
  const getTitle = () => {
    switch (currentView) {
      case 'overview': return 'Observatory Overview & Governance Health';
      case 'live_runs': return 'Agent Execution Telemetry Stream';
      case 'run_detail': return `Trace Timeline & DAG Inspector: ${selectedRunId || ''}`;
      case 'tool_inventory': return 'Tool & MCP Capability Registry';
      case 'incidents': return 'Security & Operational Incidents';
      case 'policy_violations': return 'Guardrails & Policy Violation Triage';
      case 'redaction_events': return 'Deterministic Redaction Audit Trail';
      case 'cost_energy': return 'Cost, Latency & Carbon Footprint Analytics';
      case 'mcp_view': return 'Model Context Protocol (MCP) Servers';
      case 'n8n_view': return 'n8n Workflow Automation Telemetry';
      case 'exports': return 'Compliance & Audit Report Exports';
      default: return 'AgentOps Observatory';
    }
  };

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      paddingBottom: '1.5rem',
      marginBottom: '1.5rem',
      borderBottom: '1px solid var(--border-subtle)',
      gap: '1rem',
      flexWrap: 'wrap'
    }}>
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <h1 style={{ fontSize: '1.5rem', color: 'var(--text-primary)' }}>{getTitle()}</h1>
          <span className="badge badge-success" style={{ gap: '0.25rem', padding: '0.15rem 0.45rem' }}>
            <Radio size={10} className="animate-pulse" /> LIVE
          </span>
        </div>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
          Zero-trust agent observability, append-only hash chains, and automated guardrails
        </p>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Search Bar */}
        <div style={{ position: 'relative', width: '240px' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="input-control"
            placeholder="Search run, tool, or hash..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            style={{ width: '100%', paddingLeft: '2rem' }}
          />
        </div>

        {/* Refresh Button */}
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onRefresh}
          title="Refresh telemetry stream"
        >
          <RefreshCw size={14} /> Refresh
        </button>

        {/* Role Pill */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '0.4rem',
          padding: '0.4rem 0.75rem',
          background: 'rgba(56, 189, 248, 0.08)',
          border: '1px solid rgba(56, 189, 248, 0.25)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.8rem',
          color: 'var(--accent-cyan)'
        }}>
          <Shield size={14} />
          <span>Admin: <strong>Vijay Mahes</strong></span>
        </div>
      </div>
    </header>
  );
};
