import React from 'react';
import { 
  Activity, 
  PlayCircle, 
  Wrench, 
  ShieldAlert, 
  AlertTriangle, 
  EyeOff, 
  Zap, 
  Workflow, 
  Server, 
  Download,
  Terminal,
  Layers
} from 'lucide-react';
import { PageView } from '../types';

interface SidebarProps {
  currentView: PageView;
  onSelectView: (view: PageView) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onSelectView }) => {
  const navItems: Array<{ id: PageView; label: string; icon: React.ReactNode; section: string }> = [
    { id: 'overview', label: 'Overview', icon: <Activity size={18} />, section: 'Telemetry' },
    { id: 'live_runs', label: 'Live Runs', icon: <PlayCircle size={18} />, section: 'Telemetry' },
    { id: 'tool_inventory', label: 'Tool Inventory', icon: <Wrench size={18} />, section: 'Telemetry' },
    
    { id: 'incidents', label: 'Incidents', icon: <AlertTriangle size={18} />, section: 'Governance' },
    { id: 'policy_violations', label: 'Policy Violations', icon: <ShieldAlert size={18} />, section: 'Governance' },
    { id: 'redaction_events', label: 'Redaction Audit', icon: <EyeOff size={18} />, section: 'Governance' },
    
    { id: 'cost_energy', label: 'Cost & Carbon', icon: <Zap size={18} />, section: 'Ecosystem' },
    { id: 'mcp_view', label: 'MCP Servers', icon: <Server size={18} />, section: 'Ecosystem' },
    { id: 'n8n_view', label: 'n8n Workflows', icon: <Workflow size={18} />, section: 'Ecosystem' },
    { id: 'exports', label: 'Exports & Reports', icon: <Download size={18} />, section: 'Ecosystem' },
  ];

  let lastSection = '';

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem', padding: '0 0.5rem' }}>
        <div style={{
          width: '34px',
          height: '34px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 16px rgba(14, 165, 233, 0.4)'
        }}>
          <Terminal size={20} color="#fff" />
        </div>
        <div>
          <div style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: '1rem', letterSpacing: '-0.02em' }}>
            AGENTOPS
          </div>
          <div style={{ fontSize: '0.68rem', color: 'var(--accent-cyan)', fontWeight: 600, letterSpacing: '0.08em' }}>
            OBSERVATORY
          </div>
        </div>
      </div>

      {/* Nav List */}
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {navItems.map((item) => {
          const showSection = item.section !== lastSection;
          lastSection = item.section;
          return (
            <React.Fragment key={item.id}>
              {showSection && <div className="nav-section-title">{item.section}</div>}
              <button
                type="button"
                className={`nav-item ${currentView === item.id ? 'active' : ''}`}
                onClick={() => onSelectView(item.id)}
                style={{ width: '100%', textAlign: 'left', background: 'none' }}
              >
                {item.icon}
                <span>{item.label}</span>
              </button>
            </React.Fragment>
          );
        })}
      </nav>

      {/* Footer Status */}
      <div style={{
        marginTop: 'auto',
        padding: '0.85rem',
        borderRadius: 'var(--radius-sm)',
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid var(--border-subtle)',
        fontSize: '0.75rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
          <span style={{ color: 'var(--text-muted)' }}>Collector Engine</span>
          <span className="badge badge-success" style={{ fontSize: '0.65rem' }}>Operational</span>
        </div>
        <div style={{ color: 'var(--text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
          <span>Version</span>
          <span className="font-mono">v1.0.0-prod</span>
        </div>
      </div>
    </aside>
  );
};
