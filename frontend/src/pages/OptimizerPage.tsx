import React, { useState } from 'react';
import { Cpu, DollarSign, ArrowRight, Zap, CheckCircle2 } from 'lucide-react';

export const OptimizerPage: React.FC = () => {
  const [prompt, setPrompt] = useState('Summarize the latest sales telemetry report into 3 bullet points.');
  const [currentModel, setCurrentModel] = useState('gpt-4o');
  const [recommendation, setRecommendation] = useState<{
    recommended_model: string;
    complexity_score: number;
    estimated_savings_percent: number;
    rationale: string;
    is_safe: boolean;
  }>({
    recommended_model: 'gpt-4o-mini',
    complexity_score: 0.25,
    estimated_savings_percent: 88.0,
    rationale: 'Task exhibits moderate complexity suitable for gpt-4o-mini, reducing cost by ~88%.',
    is_safe: true
  });

  const handleEvaluate = async () => {
    try {
      const res = await fetch('/api/v1/optimizer/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, current_model: currentModel })
      });
      if (res.ok) {
        const data = await res.json();
        setRecommendation({
          recommended_model: data.recommended_model,
          complexity_score: data.complexity_score,
          estimated_savings_percent: data.estimated_savings_percent,
          rationale: data.rationale,
          is_safe: data.is_safe_to_downgrade
        });
      }
    } catch {}
  };

  return (
    <div className="glass-panel" style={{ padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.25rem' }}>Intelligent Model Router & Cost Optimizer</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          Evaluate agent prompts in real time to recommend cheaper models without quality degradation.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Input Box */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Current Target Model</label>
            <select
              className="input-control"
              style={{ width: '100%', marginTop: '0.25rem' }}
              value={currentModel}
              onChange={(e) => setCurrentModel(e.target.value)}
            >
              <option value="gpt-4o">GPT-4o ($5.00 / $15.00)</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet ($3.00 / $15.00)</option>
              <option value="gemini-1.5-pro">Gemini 1.5 Pro ($3.50 / $10.50)</option>
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Agent System / User Prompt</label>
            <textarea
              className="input-control"
              style={{ width: '100%', minHeight: '140px', marginTop: '0.25rem', fontFamily: 'var(--font-sans)' }}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
            />
          </div>

          <button type="button" className="btn btn-primary" onClick={handleEvaluate}>
            <Zap size={14} /> Analyze Complexity & Compute Route
          </button>
        </div>

        {/* Output Recommendation Card */}
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ fontSize: '1rem' }}>Optimization Route Result</h3>
            <span className="badge badge-success">
              {recommendation.is_safe ? 'Safe Downgrade' : 'Keep Frontier Model'}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '1rem', background: 'rgba(56, 189, 248, 0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Current Model</div>
              <div style={{ fontWeight: 600 }}>{currentModel}</div>
            </div>
            <ArrowRight size={18} color="var(--accent-cyan)" />
            <div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Recommended Model</div>
              <div style={{ fontWeight: 700, color: 'var(--accent-cyan)' }}>{recommendation.recommended_model}</div>
            </div>
          </div>

          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Estimated Cost Reduction</div>
            <div style={{ fontSize: '2rem', fontFamily: 'var(--font-display)', fontWeight: 700, color: 'var(--accent-emerald)' }}>
              {recommendation.estimated_savings_percent}% SAVINGS
            </div>
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            {recommendation.rationale}
          </p>
        </div>
      </div>
    </div>
  );
};
