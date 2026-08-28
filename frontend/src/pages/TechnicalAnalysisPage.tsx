import {
  Activity,
  BarChart3,
  CandlestickChart,
  ChevronDown,
  Clock3,
  TrendingDown,
  TrendingUp,
  Waves,
} from "lucide-react";

const indicators = [
  {
    name: "RSI (14)",
    value: "58.42",
    status: "Neutral",
    description: "Momentum remains balanced.",
  },
  {
    name: "MACD",
    value: "Bullish",
    status: "Positive",
    description: "MACD remains above the signal line.",
  },
  {
    name: "EMA Trend",
    value: "Bullish",
    status: "Positive",
    description: "Price is trading above key moving averages.",
  },
  {
    name: "ADX (14)",
    value: "24.18",
    status: "Moderate",
    description: "Moderate trend strength detected.",
  },
];

export function TechnicalAnalysisPage() {
  return (
    <section className="workspace-page">
      <div className="page-heading">
        <div>
          <span className="page-eyebrow">TECHNICAL INTELLIGENCE</span>
          <h2>Technical Analysis Workspace</h2>
          <p>
            Analyze price action, indicators, trends, momentum, and research
            signals.
          </p>
        </div>

        <div className="analysis-controls">
          <button type="button" className="control-button">
            <CandlestickChart size={17} />
            <span>NIFTY 50</span>
            <ChevronDown size={15} />
          </button>

          <button type="button" className="control-button">
            <Clock3 size={17} />
            <span>1 Day</span>
            <ChevronDown size={15} />
          </button>
        </div>
      </div>

      <div className="analysis-summary-grid">
        <article className="metric-card">
          <div className="metric-card-header">
            <span>Current Price</span>
            <TrendingUp size={20} />
          </div>

          <strong className="metric-value">22,495.15</strong>

          <span className="metric-change positive">
            +128.35 (+0.57%)
          </span>
        </article>

        <article className="metric-card">
          <div className="metric-card-header">
            <span>Trend</span>
            <TrendingUp size={20} />
          </div>

          <strong className="metric-value metric-text positive">
            Bullish
          </strong>

          <span className="metric-caption">
            Above major moving averages
          </span>
        </article>

        <article className="metric-card">
          <div className="metric-card-header">
            <span>Momentum</span>
            <Activity size={20} />
          </div>

          <strong className="metric-value">58.42</strong>

          <span className="metric-caption">
            RSI indicates balanced momentum
          </span>
        </article>

        <article className="metric-card">
          <div className="metric-card-header">
            <span>Signal</span>
            <Waves size={20} />
          </div>

          <strong className="metric-value metric-text positive">
            Positive
          </strong>

          <span className="metric-caption">
            3 bullish indicators active
          </span>
        </article>
      </div>

      <div className="analysis-main-grid">
        <article className="terminal-card chart-card">
          <div className="terminal-card-header">
            <div>
              <span className="card-eyebrow">PRICE ACTION</span>
              <h3>NIFTY 50 Chart</h3>
            </div>

            <div className="chart-legend">
              <span>
                <i className="legend-dot positive-dot" />
                Price
              </span>
              <span>
                <i className="legend-dot neutral-dot" />
                EMA 20
              </span>
              <span>
                <i className="legend-dot muted-dot" />
                EMA 50
              </span>
            </div>
          </div>

          <div className="chart-placeholder">
            <BarChart3 size={42} />
            <strong>Chart Engine Ready</strong>
            <span>
              Historical OHLC data and indicator overlays will appear here.
            </span>
          </div>

          <div className="ohlc-grid">
            <div>
              <span>Open</span>
              <strong>22,410.20</strong>
            </div>

            <div>
              <span>High</span>
              <strong>22,530.80</strong>
            </div>

            <div>
              <span>Low</span>
              <strong>22,365.45</strong>
            </div>

            <div>
              <span>Close</span>
              <strong>22,495.15</strong>
            </div>
          </div>
        </article>

        <article className="terminal-card signal-card">
          <div className="terminal-card-header">
            <div>
              <span className="card-eyebrow">ANALYSIS ENGINE</span>
              <h3>Signal Summary</h3>
            </div>

            <span className="signal-badge positive">
              Bullish
            </span>
          </div>

          <div className="signal-list">
            <div className="signal-row">
              <div>
                <TrendingUp size={18} />
                <span>Trend</span>
              </div>
              <strong className="positive">Bullish</strong>
            </div>

            <div className="signal-row">
              <div>
                <Activity size={18} />
                <span>Momentum</span>
              </div>
              <strong>Neutral</strong>
            </div>

            <div className="signal-row">
              <div>
                <TrendingUp size={18} />
                <span>Moving Averages</span>
              </div>
              <strong className="positive">Positive</strong>
            </div>

            <div className="signal-row">
              <div>
                <TrendingDown size={18} />
                <span>Volatility</span>
              </div>
              <strong>Moderate</strong>
            </div>
          </div>

          <div className="signal-conclusion">
            <span>Research Conclusion</span>
            <strong>
              Current technical conditions show a positive directional bias.
            </strong>
          </div>
        </article>
      </div>

      <div className="indicators-section">
        <div className="section-heading">
          <div>
            <span className="page-eyebrow">INDICATOR ENGINE</span>
            <h3>Technical Indicators</h3>
          </div>

          <span className="section-meta">Development Data</span>
        </div>

        <div className="indicator-grid">
          {indicators.map((indicator) => (
            <article key={indicator.name} className="indicator-card">
              <div className="indicator-card-top">
                <span>{indicator.name}</span>

                <span
                  className={
                    indicator.status === "Positive"
                      ? "indicator-status positive"
                      : "indicator-status"
                  }
                >
                  {indicator.status}
                </span>
              </div>

              <strong>{indicator.value}</strong>

              <p>{indicator.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
