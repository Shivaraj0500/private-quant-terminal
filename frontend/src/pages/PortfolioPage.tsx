import {
  BriefcaseBusiness,
  CircleDollarSign,
  PieChart,
  ShieldAlert,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react";

const positions = [
  {
    symbol: "RELIANCE",
    name: "Reliance Industries",
    quantity: 25,
    average: "₹2,720.40",
    current: "₹2,894.65",
    pnl: "+₹4,356.25",
    change: "+6.40%",
    positive: true,
  },
  {
    symbol: "INFY",
    name: "Infosys",
    quantity: 40,
    average: "₹1,505.20",
    current: "₹1,548.35",
    pnl: "+₹1,726.00",
    change: "+2.87%",
    positive: true,
  },
  {
    symbol: "HDFCBANK",
    name: "HDFC Bank",
    quantity: 30,
    average: "₹1,710.50",
    current: "₹1,687.90",
    pnl: "-₹678.00",
    change: "-1.32%",
    positive: false,
  },
  {
    symbol: "ICICIBANK",
    name: "ICICI Bank",
    quantity: 35,
    average: "₹1,210.30",
    current: "₹1,234.80",
    pnl: "+₹857.50",
    change: "+2.02%",
    positive: true,
  },
];

export function PortfolioPage() {
  return (
    <section className="workspace-page">
      <div className="workspace-header">
        <div>
          <span className="workspace-eyebrow">PORTFOLIO INTELLIGENCE</span>
          <h2 className="workspace-title">Portfolio Workspace</h2>
          <p className="workspace-description">
            Analyze positions, exposure, performance, risk, and portfolio
            structure from one research workspace.
          </p>
        </div>

        <div className="workspace-mode-card">
          <div className="workspace-mode-icon">
            <BriefcaseBusiness size={22} />
          </div>
          <div>
            <span>Portfolio Engine</span>
            <strong>Development Mode</strong>
          </div>
        </div>
      </div>

      <div className="portfolio-summary-grid">
        <div className="metric-card">
          <div className="metric-card-top">
            <span>Total Portfolio Value</span>
            <div className="metric-icon">
              <Wallet size={20} />
            </div>
          </div>
          <strong className="metric-value">₹2,14,680</strong>
          <span className="metric-positive">+₹6,261 today</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Unrealized P&amp;L</span>
            <div className="metric-icon">
              <TrendingUp size={20} />
            </div>
          </div>
          <strong className="metric-value">+₹6,261</strong>
          <span className="metric-positive">+3.01% overall</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Active Positions</span>
            <div className="metric-icon">
              <PieChart size={20} />
            </div>
          </div>
          <strong className="metric-value">4</strong>
          <span className="metric-muted">Across 3 sectors</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Portfolio Risk</span>
            <div className="metric-icon metric-icon-warning">
              <ShieldAlert size={20} />
            </div>
          </div>
          <strong className="metric-value">Moderate</strong>
          <span className="metric-warning">Diversification improving</span>
        </div>
      </div>

      <div className="portfolio-main-grid">
        <article className="workspace-card portfolio-positions-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">POSITIONS</span>
              <h3>Current Holdings</h3>
            </div>

            <span className="card-badge">4 ACTIVE</span>
          </div>

          <div className="positions-table">
            <div className="positions-row positions-header-row">
              <span>Instrument</span>
              <span>Qty</span>
              <span>Average</span>
              <span>Current</span>
              <span>P&amp;L</span>
            </div>

            {positions.map((position) => (
              <div className="positions-row" key={position.symbol}>
                <div className="position-instrument">
                  <strong>{position.symbol}</strong>
                  <span>{position.name}</span>
                </div>

                <span>{position.quantity}</span>
                <span>{position.average}</span>
                <span>{position.current}</span>

                <div
                  className={
                    position.positive
                      ? "position-pnl position-pnl-positive"
                      : "position-pnl position-pnl-negative"
                  }
                >
                  <strong>{position.pnl}</strong>
                  <span>{position.change}</span>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="workspace-card portfolio-allocation-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">EXPOSURE</span>
              <h3>Portfolio Allocation</h3>
            </div>
          </div>

          <div className="allocation-list">
            <div className="allocation-item">
              <div className="allocation-item-header">
                <span>Financials</span>
                <strong>42%</strong>
              </div>
              <div className="allocation-track">
                <div className="allocation-fill allocation-financials" />
              </div>
            </div>

            <div className="allocation-item">
              <div className="allocation-item-header">
                <span>Technology</span>
                <strong>29%</strong>
              </div>
              <div className="allocation-track">
                <div className="allocation-fill allocation-technology" />
              </div>
            </div>

            <div className="allocation-item">
              <div className="allocation-item-header">
                <span>Energy</span>
                <strong>21%</strong>
              </div>
              <div className="allocation-track">
                <div className="allocation-fill allocation-energy" />
              </div>
            </div>

            <div className="allocation-item">
              <div className="allocation-item-header">
                <span>Cash Reserve</span>
                <strong>8%</strong>
              </div>
              <div className="allocation-track">
                <div className="allocation-fill allocation-cash" />
              </div>
            </div>
          </div>

          <div className="allocation-insight">
            <CircleDollarSign size={18} />
            <span>
              Financial sector exposure is currently the largest portfolio
              concentration.
            </span>
          </div>
        </article>
      </div>

      <div className="portfolio-bottom-grid">
        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">PERFORMANCE</span>
              <h3>Portfolio Performance</h3>
            </div>

            <span className="performance-positive">+3.01%</span>
          </div>

          <div className="performance-placeholder">
            <TrendingUp size={34} />
            <strong>Performance Engine Ready</strong>
            <span>
              Historical portfolio equity curve and benchmark comparison will
              appear here.
            </span>
          </div>
        </article>

        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">RISK ENGINE</span>
              <h3>Risk Summary</h3>
            </div>
          </div>

          <div className="risk-list">
            <div className="risk-item">
              <span>Concentration Risk</span>
              <strong className="risk-moderate">Moderate</strong>
            </div>

            <div className="risk-item">
              <span>Largest Position</span>
              <strong>Reliance</strong>
            </div>

            <div className="risk-item">
              <span>Sector Exposure</span>
              <strong>Financials 42%</strong>
            </div>

            <div className="risk-item">
              <span>Drawdown Monitor</span>
              <strong className="risk-positive">Normal</strong>
            </div>
          </div>

          <div className="portfolio-risk-note">
            <TrendingDown size={17} />
            <span>
              Full VaR, beta, correlation, and drawdown analytics will connect
              to the portfolio backend engine.
            </span>
          </div>
        </article>
      </div>
    </section>
  );
}
