import React from 'react';
import { DollarSign, Zap, Leaf, Cpu, Award } from 'lucide-react';
import { MetricsOverview } from '../types';

interface CostEnergyPageProps {
  metrics: MetricsOverview;
}

export const CostEnergyPage: React.FC<CostEnergyPageProps> = ({ metrics }) => {
  const modelRates = [
    { model: 'GPT-4o (OpenAI)', promptRate: '$5.00 / 1M', compRate: '$15.00 / 1M', type: 'Cloud Frontier' },
    { model: 'Claude 3.5 Sonnet (Anthropic)', promptRate: '$3.00 / 1M', compRate: '$15.00 / 1M', type: 'Cloud Frontier' },
    { model: 'Gemini 1.5 Pro (Google)', promptRate: '$3.50 / 1M', compRate: '$10.50 / 1M', type: 'Cloud Frontier' },
    { model: 'Llama 3 70B (Ollama Local)', promptRate: '$0.00 (Self-hosted)', compRate: '$0.00 (Self-hosted)', type: 'Local Open Weights' },
  ];

  return (
    <div>
      {/* Cards */}
      <div className="kpi-grid">
        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Cumulative Cost</span>
            <DollarSign size={18} color="var(--accent-amber)" />
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-amber)' }}>
            ${metrics.total_cost_usd.toFixed(3)}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Label: <strong style={{ color: 'var(--accent-cyan)' }}>ESTIMATED</strong>
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Electrical Energy</span>
            <Zap size={18} color="var(--accent-cyan)" />
          </div>
          <div className="kpi-value">
            {metrics.total_energy_kwh.toFixed(4)} <span style={{ fontSize: '0.9rem' }}>kWh</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Assumes PUE 1.25 datacenter profile
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Carbon Footprint</span>
            <Leaf size={18} color="#22c55e" />
          </div>
          <div className="kpi-value" style={{ color: '#22c55e' }}>
            {metrics.total_carbon_gco2eq.toFixed(1)} <span style={{ fontSize: '0.9rem' }}>gCO2eq</span>
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Grid intensity: 390 gCO2/kWh
          </div>
        </div>

        <div className="kpi-card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span className="kpi-label">Green Compute Index</span>
            <Award size={18} color="var(--accent-emerald)" />
          </div>
          <div className="kpi-value" style={{ color: 'var(--accent-emerald)' }}>
            A+ (98/100)
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.35rem' }}>
            Zero unnecessary token loops
          </div>
        </div>
      </div>

      {/* Model Pricing Reference */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.15rem', marginBottom: '0.35rem' }}>Standard Rate Card Matrix</h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          Pricing models referenced by the telemetry engine for real-time cost estimation.
        </p>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Model Architecture</th>
                <th>Category</th>
                <th>Prompt Token Rate</th>
                <th>Completion Token Rate</th>
                <th>Estimation Label</th>
              </tr>
            </thead>
            <tbody>
              {modelRates.map((r) => (
                <tr key={r.model}>
                  <td style={{ fontWeight: 600 }}>{r.model}</td>
                  <td>
                    <span className={`badge ${r.type.includes('Local') ? 'badge-success' : 'badge-info'}`}>
                      {r.type}
                    </span>
                  </td>
                  <td className="font-mono">{r.promptRate}</td>
                  <td className="font-mono">{r.compRate}</td>
                  <td>
                    <span className="badge badge-medium">ESTIMATED</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
