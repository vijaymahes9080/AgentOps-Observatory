import React, { useState, useEffect } from 'react';
import { Search, Activity, PlayCircle, ShieldAlert, AlertTriangle, EyeOff, Zap, Server, Workflow, Download, X } from 'lucide-react';
import { PageView } from '../types';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectView: (view: PageView) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({
  isOpen,
  onClose,
  onSelectView
}) => {
  const [query, setQuery] = useState('');

  const commands: Array<{ id: PageView; title: string; category: string; icon: React.ReactNode }> = [
    { id: 'overview', title: 'System Overview & KPIs', category: 'Telemetry', icon: <Activity size={16} /> },
    { id: 'live_runs', title: 'Live Agent Runs & Spans', category: 'Telemetry', icon: <PlayCircle size={16} /> },
    { id: 'incidents', title: 'Security Incidents', category: 'Governance', icon: <AlertTriangle size={16} /> },
    { id: 'policy_violations', title: 'Policy Violations Triage', category: 'Governance', icon: <ShieldAlert size={16} /> },
    { id: 'redaction_events', title: 'Redaction Audit Log', category: 'Privacy', icon: <EyeOff size={16} /> },
    { id: 'cost_energy', title: 'Cost & Carbon Analytics', category: 'ESG', icon: <Zap size={16} /> },
    { id: 'mcp_view', title: 'Model Context Protocol (MCP) Servers', category: 'Integrations', icon: <Server size={16} /> },
    { id: 'n8n_view', title: 'n8n Workflow Telemetry', category: 'Integrations', icon: <Workflow size={16} /> },
    { id: 'exports', title: 'Compliance Report Exporter', category: 'Exports', icon: <Download size={16} /> },
  ];

  const filtered = commands.filter((c) =>
    c.title.toLowerCase().includes(query.toLowerCase()) ||
    c.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        onClose();
      }
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'flex-start',
      justifyContent: 'center',
      paddingTop: '15vh',
      zIndex: 100
    }} onClick={onClose}>
      <div style={{
        width: '560px',
        background: '#0f172a',
        border: '1px solid var(--border-medium)',
        borderRadius: 'var(--radius-md)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.8)',
        overflow: 'hidden'
      }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', alignItems: 'center', padding: '0.85rem 1rem', borderBottom: '1px solid var(--border-subtle)' }}>
          <Search size={18} color="var(--accent-cyan)" style={{ marginRight: '0.75rem' }} />
          <input
            autoFocus
            type="text"
            className="input-control"
            placeholder="Type a command or jump to page..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ width: '100%', border: 'none', background: 'transparent', padding: 0 }}
          />
          <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        <div style={{ maxHeight: '320px', overflowY: 'auto', padding: '0.5rem' }}>
          {filtered.map((cmd) => (
            <div
              key={cmd.id}
              onClick={() => {
                onSelectView(cmd.id);
                onClose();
              }}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '0.65rem 0.85rem',
                borderRadius: '6px',
                cursor: 'pointer',
                transition: 'background 0.1s ease',
                color: 'var(--text-primary)'
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(56, 189, 248, 0.1)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <span style={{ color: 'var(--accent-cyan)' }}>{cmd.icon}</span>
                <span style={{ fontSize: '0.875rem' }}>{cmd.title}</span>
              </div>
              <span className="font-mono" style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {cmd.category}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
