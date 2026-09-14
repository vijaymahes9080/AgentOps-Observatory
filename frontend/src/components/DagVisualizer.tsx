import React from 'react';
import { TraceGraphData, TraceNodeData } from '../types';
import { CornerDownRight, CheckCircle2, AlertCircle, AlertTriangle } from 'lucide-react';

interface DagVisualizerProps {
  graph: TraceGraphData;
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string) => void;
}

export const DagVisualizer: React.FC<DagVisualizerProps> = ({
  graph,
  selectedNodeId,
  onSelectNode
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
        <span>DAG Spans ({Object.keys(graph.nodes).length} nodes, {graph.edges.length} edges)</span>
        <span style={{ color: graph.is_partial ? 'var(--accent-amber)' : 'var(--accent-emerald)' }}>
          {graph.is_partial ? '⚠️ Trace Has Orphan Nodes' : '✓ Full Lineage Intact'}
        </span>
      </div>

      <div style={{
        background: 'rgba(11, 15, 25, 0.7)',
        borderRadius: 'var(--radius-md)',
        padding: '1rem',
        border: '1px solid var(--border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.6rem'
      }}>
        {Object.values(graph.nodes).map((node: TraceNodeData) => {
          const isSelected = selectedNodeId === node.id;
          const hasError = node.has_error;
          const isOrphan = node.is_partial_orphan;

          return (
            <div
              key={node.id}
              onClick={() => onSelectNode(node.id)}
              style={{
                marginLeft: node.parent_id ? '1.75rem' : '0',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-sm)',
                background: isSelected
                  ? 'rgba(56, 189, 248, 0.15)'
                  : hasError
                  ? 'rgba(244, 63, 94, 0.08)'
                  : isOrphan
                  ? 'rgba(245, 158, 11, 0.08)'
                  : 'rgba(255, 255, 255, 0.03)',
                border: isSelected
                  ? '1px solid var(--accent-cyan)'
                  : hasError
                  ? '1px solid rgba(244, 63, 94, 0.4)'
                  : isOrphan
                  ? '1px solid rgba(245, 158, 11, 0.4)'
                  : '1px solid var(--border-subtle)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                transition: 'all 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                {node.parent_id && <CornerDownRight size={15} color="var(--text-muted)" />}
                {hasError ? (
                  <AlertCircle size={16} color="var(--accent-rose)" />
                ) : isOrphan ? (
                  <AlertTriangle size={16} color="var(--accent-amber)" />
                ) : (
                  <CheckCircle2 size={16} color="var(--accent-emerald)" />
                )}
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>{node.name}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                    {node.event_type} • {node.duration_ms.toFixed(0)} ms
                  </div>
                </div>
              </div>

              <span className={`badge ${hasError ? 'badge-error' : isOrphan ? 'badge-partial' : 'badge-success'}`}>
                {node.status}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
