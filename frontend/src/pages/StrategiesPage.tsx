import {
  Activity,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  Play,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

const strategies = [
  {
    name: "NIFTY Momentum Breakout",
    version: "v1.0.0",
    type: "Momentum",
    status: "Validated",
    performance: "+18.42%",
    positive: true,
    description:
      "Breakout strategy using momentum confirmation and trend filters.",
  },
  {
    name: "EMA Trend Following",
    version: "v0.8.2",
    type: "Trend Following",
    status: "Research",
    performance: "+9.86%",
    positive: true,
    description:
      "Multi-timeframe moving-average strategy with directional filtering.",
  },
  {
    name: "Mean Reversion Engine",
    version: "v0.4.1",
    type: "Mean Reversion",
    status: "Testing",
    performance: "-2.14%",
    positive: false,
    description:
      "Statistical reversion model for temporary price dislocations.",
  },
];

export function StrategiesPage() {
  return (
    <section className="workspace-page">
      <div className="workspace-header">
        <div>
          <span className="workspace-eyebrow">STRATEGY RESEARCH</span>
          <h2 className="workspace-title">Strategies Workspace</h2>
          <p className="workspace-description">
            Develop, validate, compare, and version systematic trading
            strategies inside a controlled research environment.
          </p>
        </div>

        <div className="workspace-mode-card">
          <div className="workspace-mode-icon">
            <FlaskConical size={22} />
          </div>
          <div>
            <span>Strategy Engine</span>
            <strong>Research Mode</strong>
          </div>
        </div>
      </div>

      <div className="strategy-summary-grid">
        <div className="metric-card">
          <div className="metric-card-top">
            <span>Active Strategies</span>
            <div className="metric-icon">
              <FlaskConical size={20} />
            </div>
          </div>
          <strong className="metric-value">3</strong>
          <span className="metric-positive">Research pipeline active</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Validated</span>
            <div className="metric-icon">
              <CheckCircle2 size={20} />
            </div>
          </div>
          <strong className="metric-value">1</strong>
          <span className="metric-positive">Robustness checks passed</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Backtest Runs</span>
            <div className="metric-icon">
              <BarChart3 size={20} />
            </div>
          </div>
          <strong className="metric-value">24</strong>
          <span className="metric-muted">Development environment</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Deployment Ready</span>
            <div className="metric-icon">
              <ShieldCheck size={20} />
            </div>
          </div>
          <strong className="metric-value">1</strong>
          <span className="metric-positive">Paper trading eligible</span>
        </div>
      </div>

      <div className="strategy-main-grid">
        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">STRATEGY REGISTRY</span>
              <h3>Research Strategies</h3>
            </div>

            <span className="card-badge">3 REGISTERED</span>
          </div>

          <div className="strategy-list">
            {strategies.map((strategy) => (
              <div className="strategy-item" key={strategy.name}>
                <div className="strategy-item-icon">
                  <TrendingUp size={20} />
                </div>

                <div className="strategy-item-main">
                  <div className="strategy-item-title">
                    <strong>{strategy.name}</strong>
                    <span>{strategy.version}</span>
                  </div>

                  <p>{strategy.description}</p>

                  <div className="strategy-tags">
                    <span>{strategy.type}</span>
                    <span
                      className={
                        strategy.status === "Validated"
                          ? "strategy-status strategy-status-validated"
                          : strategy.status === "Testing"
                            ? "strategy-status strategy-status-testing"
                            : "strategy-status"
                      }
                    >
                      {strategy.status}
                    </span>
                  </div>
                </div>

                <div className="strategy-performance">
                  <strong
                    className={
                      strategy.positive
                        ? "performance-positive"
                        : "performance-negative"
                    }
                  >
                    {strategy.performance}
                  </strong>
                  <span>Backtest return</span>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">RESEARCH PIPELINE</span>
              <h3>Validation Workflow</h3>
            </div>
          </div>

          <div className="validation-list">
            <div className="validation-step validation-step-complete">
              <div className="validation-step-icon">
                <CheckCircle2 size={18} />
              </div>
              <div>
                <strong>Hypothesis Defined</strong>
                <span>Strategy rules documented</span>
              </div>
            </div>

            <div className="validation-step validation-step-complete">
              <div className="validation-step-icon">
                <CheckCircle2 size={18} />
              </div>
              <div>
                <strong>Historical Backtest</strong>
                <span>Historical behavior evaluated</span>
              </div>
            </div>

            <div className="validation-step validation-step-active">
              <div className="validation-step-icon">
                <Activity size={18} />
              </div>
              <div>
                <strong>Robustness Testing</strong>
                <span>Parameter and regime validation</span>
              </div>
            </div>

            <div className="validation-step">
              <div className="validation-step-icon">
                <Play size={18} />
              </div>
              <div>
                <strong>Paper Deployment</strong>
                <span>Forward validation pending</span>
              </div>
            </div>
          </div>
        </article>
      </div>

      <div className="strategy-bottom-grid">
        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">STRATEGY ANALYTICS</span>
              <h3>Research Comparison</h3>
            </div>
          </div>

          <div className="strategy-chart-placeholder">
            <BarChart3 size={34} />
            <strong>Strategy Analytics Ready</strong>
            <span>
              Equity curves, drawdowns, win rates, Sharpe ratios, and
              benchmark comparisons will appear here.
            </span>
          </div>
        </article>

        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">CURRENT FOCUS</span>
              <h3>Research Notes</h3>
            </div>
          </div>

          <div className="research-note-list">
            <div className="research-note">
              <span className="research-note-dot" />
              <div>
                <strong>Momentum strategy validated</strong>
                <p>Initial historical robustness criteria completed.</p>
              </div>
            </div>

            <div className="research-note">
              <span className="research-note-dot" />
              <div>
                <strong>Trend strategy under refinement</strong>
                <p>Multi-timeframe filters are being evaluated.</p>
              </div>
            </div>

            <div className="research-note">
              <span className="research-note-dot research-note-dot-muted" />
              <div>
                <strong>Mean reversion testing</strong>
                <p>Additional market-regime testing required.</p>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>
  );
}
