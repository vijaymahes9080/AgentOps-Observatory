import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  ArrowLeft, 
  Download, 
  Clock, 
  Cpu, 
  DollarSign, 
  Zap, 
  FileText, 
  CheckCircle,
  Network,
  Lock,
  CornerDownRight
} from 'lucide-react';
import { RunDetail, TraceGraphData, RunEventItem } from '../types';
import { api } from '../services/api';

interface RunDetailPageProps {
  runId: string;
  onBack: () => void;
}

export const RunDetailPage: React.FC<RunDetailPageProps> = ({ runId, onBack }) => {
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [traceGraph, setTraceGraph] = useState<TraceGraphData | null>(null);
  const [selectedEvent, setSelectedEvent] = useState<RunEventItem | null>(null);
  const [activeTab, setActiveTab] = useState<'timeline' | 'dag' | 'events'>('timeline');

  useEffect(() => {
    async function load() {
      const d = await api.getRunDetail(runId);
      const tg = await api.getRunTimeline(runId);
      setDetail(d);
      setTraceGraph(tg);
      if (d && d.events.length > 0) {
        setSelectedEvent(d.events[0]);
      }
    }
    load();
  }, [runId]);

  if (!detail) {
    return (
      <div className="glass-panel" style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Loading run details for {runId}...</p>
      </div>
    );
  }

  const handleDownload = async () => {
    const data = await api.exportRun(runId);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `agentops-run-${runId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const maxDuration = Math.max(detail.total_duration_ms, 100);

  return (
    <div>
      {/* Back Button & Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onBack}
        >
          <ArrowLeft size={14} /> Back to Runs
        </button>

        <button
          type="button"
          className="btn btn-primary"
          onClick={handleDownload}
        >
          <Download size={14} /> Export Sanitized JSON
        </button>
      </div>

      {/* Partial Trace / Missing Telemetry Warning Banner */}
      {detail.is_partial && (
        <div className="alert-banner alert-warning">
          <AlertTriangle size={20} color="var(--accent-amber)" />
          <div>
            <strong>Partial Trace Warning: Incomplete Telemetry Detected</strong>
            <p style={{ fontSize: '0.8rem', marginTop: '0.2rem' }}>
              {detail.missing_telemetry_reasons && detail.missing_telemetry_reasons.length > 0
                ? detail.missing_telemetry_reasons.join(' | ')
                : 'Orphan child spans reference parent IDs not present in observatory storage. Full lineage cannot be guaranteed.'}
            </p>
          </div>
        </div>
      )}

      {/* Run Summary Card */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-display)' }}>{detail.agent_name}</h2>
              <span className={`badge ${
                detail.status === 'success' ? 'badge-success' :
                detail.status === 'violated' ? 'badge-error' :
                detail.is_partial ? 'badge-partial' : 'badge-info'
              }`}>
                {detail.is_partial ? 'PARTIAL' : detail.status.toUpperCase()}
              </span>
            </div>
            <div className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', marginTop: '0.25rem' }}>
              Run ID: {detail.run_id}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.85rem' }}>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Duration</div>
              <div style={{ fontWeight: 600 }}>{detail.total_duration_ms.toFixed(0)} ms</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Total Tokens</div>
              <div style={{ fontWeight: 600 }}>{detail.total_tokens.toLocaleString()}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Est. Cost</div>
              <div style={{ fontWeight: 600 }}>${detail.total_cost_usd.toFixed(4)}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Carbon</div>
              <div style={{ fontWeight: 600, color: '#22c55e' }}>{detail.total_carbon_gco2eq.toFixed(2)} gCO2</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-muted)' }}>Violations</div>
              <div style={{ fontWeight: 600, color: detail.policy_violation_count > 0 ? 'var(--accent-rose)' : 'inherit' }}>
                {detail.policy_violation_count}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem' }}>
        <button
          type="button"
          className={`btn ${activeTab === 'timeline' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('timeline')}
        >
          <Clock size={14} /> Timeline View
        </button>
        <button
          type="button"
          className={`btn ${activeTab === 'dag' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('dag')}
        >
          <Network size={14} /> DAG Span Tree
        </button>
        <button
          type="button"
          className={`btn ${activeTab === 'events' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('events')}
        >
          <FileText size={14} /> Event Stream ({detail.events.length})
        </button>
      </div>

      {/* Main Content Area */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(450px, 1.3fr) 1fr', gap: '1.5rem' }}>
        
        {/* Left: View Panel */}
        <div className="glass-panel" style={{ padding: '1.25rem', minHeight: '400px' }}>
          {activeTab === 'timeline' && traceGraph && (
            <div>
              <h3 style={{ fontSize: '0.95rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                Relative Timeline Latency Graph
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {traceGraph.timeline.map((item) => {
                  const widthPct = Math.max(8, (item.duration_ms / maxDuration) * 100);
                  const leftPct = Math.min(85, (item.offset_ms / maxDuration) * 100);
                  return (
                    <div 
                      key={item.event_id} 
                      onClick={() => {
                        const ev = detail.events.find(e => e.event_id === item.event_id);
                        if (ev) setSelectedEvent(ev);
                      }}
                      style={{
                        padding: '0.5rem 0.75rem',
                        borderRadius: 'var(--radius-sm)',
                        background: selectedEvent?.event_id === item.event_id ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                        border: selectedEvent?.event_id === item.event_id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                        cursor: 'pointer'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.35rem' }}>
                        <span style={{ fontWeight: 600 }}>{item.name}</span>
                        <span className="font-mono" style={{ color: 'var(--text-muted)' }}>
                          +{item.offset_ms.toFixed(0)}ms ({item.duration_ms.toFixed(0)}ms)
                        </span>
                      </div>
                      <div style={{ background: 'rgba(255, 255, 255, 0.05)', borderRadius: '4px', height: '8px', width: '100%', position: 'relative' }}>
                        <div 
                          className={`timeline-bar ${item.has_error ? 'error' : item.is_orphan ? 'partial' : ''}`}
                          style={{
                            left: `${leftPct}%`,
                            width: `${Math.min(100 - leftPct, widthPct)}%`,
                            position: 'absolute'
                          }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {activeTab === 'dag' && traceGraph && (
            <div>
              <h3 style={{ fontSize: '0.95rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                Directed Acyclic Graph (DAG) Spans & Model-to-Tool Links
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {Object.values(traceGraph.nodes).map((node) => (
                  <div
                    key={node.id}
                    onClick={() => {
                      const ev = detail.events.find(e => e.event_id === node.id);
                      if (ev) setSelectedEvent(ev);
                    }}
                    style={{
                      padding: '0.75rem 1rem',
                      borderRadius: 'var(--radius-sm)',
                      background: selectedEvent?.event_id === node.id ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                      border: selectedEvent?.event_id === node.id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                      marginLeft: node.parent_id ? '1.5rem' : '0',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {node.parent_id && <CornerDownRight size={14} color="var(--text-muted)" />}
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{node.name}</div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{node.event_type}</div>
                      </div>
                    </div>
                    <span className={`badge ${node.has_error ? 'badge-error' : node.is_partial_orphan ? 'badge-partial' : 'badge-success'}`}>
                      {node.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'events' && (
            <div>
              <h3 style={{ fontSize: '0.95rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>
                Chronological Event Stream
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {detail.events.map((e) => (
                  <div
                    key={e.event_id}
                    onClick={() => setSelectedEvent(e)}
                    style={{
                      padding: '0.65rem 0.85rem',
                      borderRadius: 'var(--radius-sm)',
                      background: selectedEvent?.event_id === e.event_id ? 'rgba(56, 189, 248, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                      border: selectedEvent?.event_id === e.event_id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                      cursor: 'pointer',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center'
                    }}
                  >
                    <div>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{e.name || e.event_type}</span>
                      <span className="font-mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: '0.5rem' }}>
                        {e.source}
                      </span>
                    </div>
                    <span className={`badge ${e.status === 'success' ? 'badge-success' : 'badge-error'}`}>
                      {e.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right: Payload & Hash Inspector */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '0.95rem', marginBottom: '1rem', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Lock size={14} color="var(--accent-cyan)" /> Cryptographic Audit & Redacted Payload
          </h3>

          {selectedEvent ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Event ID</div>
                <div className="font-mono" style={{ fontSize: '0.8rem', color: 'var(--text-primary)' }}>{selectedEvent.event_id}</div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Current Event SHA-256 Hash</div>
                <div className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', wordBreak: 'break-all' }}>
                  {selectedEvent.current_hash}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Previous Hash Chain Reference</div>
                <div className="font-mono" style={{ fontSize: '0.75rem', color: 'var(--text-muted)', wordBreak: 'break-all' }}>
                  {selectedEvent.prev_hash}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Redacted Payload JSON</div>
                <pre style={{
                  background: 'rgba(11, 15, 25, 0.9)',
                  padding: '0.75rem',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.75rem',
                  maxHeight: '320px',
                  overflow: 'auto',
                  border: '1px solid var(--border-subtle)',
                  color: '#e2e8f0'
                }}>
                  {JSON.stringify(selectedEvent.payload, null, 2)}
                </pre>
              </div>
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Select an event from the timeline or DAG to view payload and hashes.</p>
          )}
        </div>

      </div>
    </div>
  );
};
