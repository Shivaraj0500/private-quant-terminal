import {
  Activity,
  AlertCircle,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  Play,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
} from "lucide-react";
import { useEffect, useState } from "react";
import {
  executeResearchRun,
  type ResearchRunResponse,
} from "../api/research";
import {
  getStrategyVersion,
  listStrategies,
  type StrategyVersion,
} from "../api/strategy";

const initialPayload = {
  strategy_id: "",
  strategy_version: 1,
  symbol: "RELIANCE",
  timeframe: "5m",
  parameters: "{}",
  initial_equity: 100000,
};

export function ResearchPage() {
  const [strategies, setStrategies] = useState<StrategyVersion[]>([]);
  const [strategyId, setStrategyId] = useState(initialPayload.strategy_id);
  const [strategyVersion, setStrategyVersion] = useState(
    initialPayload.strategy_version,
  );
  const [symbol, setSymbol] = useState(initialPayload.symbol);
  const [timeframe, setTimeframe] = useState(initialPayload.timeframe);
  const [parameters, setParameters] = useState(initialPayload.parameters);
  const [initialEquity, setInitialEquity] = useState(
    initialPayload.initial_equity,
  );

  const [result, setResult] = useState<ResearchRunResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStrategies, setLoadingStrategies] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadStrategies() {
      setLoadingStrategies(true);
      setError("");

      try {
        const response = await listStrategies();

        setStrategies(response.versions);

        if (response.versions.length > 0) {
          const first = response.versions[0];

          setStrategyId(first.strategy_id);
          setStrategyVersion(first.version);
          setSymbol(first.instruments[0] ?? "RELIANCE");
          setTimeframe(first.timeframe);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Unable to load strategies.",
        );
      } finally {
        setLoadingStrategies(false);
      }
    }

    void loadStrategies();
  }, []);

  async function handleRunResearch() {
    setLoading(true);
    setError("");

    try {
      const parsedParameters = JSON.parse(parameters) as Record<
        string,
        unknown
      >;

      await getStrategyVersion(strategyId.trim(), strategyVersion);

      const researchResult = await executeResearchRun({
        strategy_id: strategyId.trim(),
        strategy_version: strategyVersion,
        symbol: symbol.trim(),
        timeframe,
        parameters: parsedParameters,
        initial_equity: initialEquity,
      });

      setResult(researchResult);
    } catch (err) {
      setResult(null);
      setError(
        err instanceof Error
          ? err.message
          : "Unable to execute research run.",
      );
    } finally {
      setLoading(false);
    }
  }

  const performance = result?.performance;

  return (
    <section className="workspace-page">
      <div className="workspace-header">
        <div>
          <span className="workspace-eyebrow">RESEARCH ENGINE</span>
          <h1>Research Terminal</h1>
          <p>
            Execute deterministic strategy research and inspect the resulting
            performance evidence.
          </p>
        </div>

        <div className="workspace-mode-card">
          <div className="workspace-mode-icon">
            <FlaskConical size={22} />
          </div>

          <div>
            <span>Execution Mode</span>
            <strong>Deterministic Research</strong>
          </div>
        </div>
      </div>

      <article className="workspace-card research-run-card">
        <div className="card-header">
          <div>
            <span className="card-eyebrow">RESEARCH CONFIGURATION</span>
            <h3>Configure Research Run</h3>
          </div>

          {result && (
            <span className="card-badge">
              {result.run.status}
            </span>
          )}
        </div>

        <div className="research-form-grid">
          <label className="research-field">
            <span>Strategy</span>

            <select
              value={
                strategyId
                  ? `${strategyId}:${strategyVersion}`
                  : ""
              }
              disabled={
                loadingStrategies ||
                strategies.length === 0
              }
              onChange={(event) => {
                const [selectedId, selectedVersion] =
                  event.target.value.split(":");

                const version = Number(selectedVersion);

                const selected = strategies.find(
                  (strategy) =>
                    strategy.strategy_id === selectedId &&
                    strategy.version === version,
                );

                setStrategyId(selectedId);
                setStrategyVersion(version);

                if (selected) {
                  setSymbol(
                    selected.instruments[0] ?? "RELIANCE",
                  );
                  setTimeframe(selected.timeframe);
                }
              }}
            >
              {loadingStrategies ? (
                <option value="">
                  Loading strategies...
                </option>
              ) : strategies.length === 0 ? (
                <option value="">
                  No strategies available
                </option>
              ) : (
                strategies.map((strategy) => (
                  <option
                    key={`${strategy.strategy_id}:${strategy.version}`}
                    value={`${strategy.strategy_id}:${strategy.version}`}
                  >
                    {strategy.name} · v{strategy.version}
                  </option>
                ))
              )}
            </select>
          </label>

          <label className="research-field">
            <span>Strategy Version</span>
            <input
              type="number"
              value={strategyVersion}
              readOnly
            />
          </label>

          <label className="research-field">
            <span>Symbol</span>
            <input
              value={symbol}
              onChange={(event) => setSymbol(event.target.value)}
              placeholder="RELIANCE"
            />
          </label>

          <label className="research-field">
            <span>Timeframe</span>
            <select
              value={timeframe}
              onChange={(event) => setTimeframe(event.target.value)}
            >
              <option value="1m">1m</option>
              <option value="5m">5m</option>
              <option value="15m">15m</option>
              <option value="30m">30m</option>
              <option value="1h">1h</option>
              <option value="4h">4h</option>
              <option value="1d">1d</option>
            </select>
          </label>

          <label className="research-field">
            <span>Initial Equity</span>
            <input
              type="number"
              min={0}
              value={initialEquity}
              onChange={(event) =>
                setInitialEquity(Number(event.target.value))
              }
            />
          </label>

          <label className="research-field research-field-wide">
            <span>Parameters JSON</span>
            <textarea
              value={parameters}
              onChange={(event) => setParameters(event.target.value)}
              rows={3}
              spellCheck={false}
            />
          </label>
        </div>

        {error && (
          <div className="research-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <button
          type="button"
          className="research-run-button"
          onClick={handleRunResearch}
          disabled={loading || !strategyId.trim() || !symbol.trim()}
        >
          {loading ? (
            <>
              <Activity size={18} />
              Running Research...
            </>
          ) : (
            <>
              <Play size={18} />
              Run Research
            </>
          )}
        </button>
      </article>

      {!result && !loading && (
        <article className="workspace-card research-empty-state">
          <BarChart3 size={34} />
          <strong>No research run loaded</strong>
          <span>
            Configure a persisted strategy version above and execute a research
            run to populate the terminal.
          </span>
        </article>
      )}

      {result && performance && (
        <>
          <div className="metric-grid">
            <MetricCard
              label="Final Equity"
              value={formatNumber(result.execution.final_equity)}
              icon={TrendingUp}
            />
            <MetricCard
              label="Net P&L"
              value={formatNumber(performance.total_pnl)}
              icon={
                performance.total_pnl >= 0 ? TrendingUp : TrendingDown
              }
            />
            <MetricCard
              label="Win Rate"
              value={`${formatNumber(performance.win_rate)}%`}
              icon={CheckCircle2}
            />
            <MetricCard
              label="Profit Factor"
              value={formatNumber(performance.profit_factor)}
              icon={BarChart3}
            />
            <MetricCard
              label="Max Drawdown"
              value={formatNumber(performance.max_drawdown)}
              icon={TrendingDown}
            />
            <MetricCard
              label="Sharpe"
              value={formatNumber(performance.sharpe_ratio)}
              icon={Activity}
            />
            <MetricCard
              label="Sortino"
              value={formatNumber(performance.sortino_ratio)}
              icon={Activity}
            />
            <MetricCard
              label="Calmar"
              value={formatNumber(performance.calmar_ratio)}
              icon={ShieldCheck}
            />
          </div>

          <div className="research-result-grid">
            <article className="workspace-card">
              <div className="card-header">
                <div>
                  <span className="card-eyebrow">RUN IDENTITY</span>
                  <h3>Research Evidence</h3>
                </div>
              </div>

              <div className="research-identity-list">
                <IdentityRow label="Run ID" value={result.run.run_id} />
                <IdentityRow
                  label="Strategy"
                  value={`${result.run.strategy_id} v${result.run.strategy_version}`}
                />
                <IdentityRow
                  label="Strategy Hash"
                  value={result.run.strategy_hash}
                />
                <IdentityRow
                  label="Dataset Hash"
                  value={result.run.dataset_hash}
                />
                <IdentityRow
                  label="Parameters Hash"
                  value={result.run.parameters_hash}
                />
                <IdentityRow
                  label="Dataset"
                  value={`${result.run.symbol} · ${result.run.timeframe}`}
                />
              </div>
            </article>

            <article className="workspace-card">
              <div className="card-header">
                <div>
                  <span className="card-eyebrow">EXECUTION</span>
                  <h3>Run Summary</h3>
                </div>
              </div>

              <div className="research-summary">
                <div>
                  <span>Status</span>
                  <strong>{result.run.status}</strong>
                </div>
                <div>
                  <span>Trades</span>
                  <strong>{result.execution.trades.length}</strong>
                </div>
                <div>
                  <span>Winning Trades</span>
                  <strong>{performance.winning_trades}</strong>
                </div>
                <div>
                  <span>Losing Trades</span>
                  <strong>{performance.losing_trades}</strong>
                </div>
                <div>
                  <span>Start</span>
                  <strong>{formatDate(result.run.start_time)}</strong>
                </div>
                <div>
                  <span>End</span>
                  <strong>{formatDate(result.run.end_time)}</strong>
                </div>
              </div>
            </article>
          </div>

          <article className="workspace-card">
            <div className="card-header">
              <div>
                <span className="card-eyebrow">EQUITY CURVE</span>
                <h3>Research Performance</h3>
              </div>

              <span className="card-badge">
                {result.execution.equity_curve.length} points
              </span>
            </div>

            <div className="equity-curve">
              {result.execution.equity_curve.map((value, index) => {
                const curve = result.execution.equity_curve;
                const minimum = Math.min(...curve);
                const maximum = Math.max(...curve);
                const range = maximum - minimum || 1;
                const height = ((value - minimum) / range) * 100;

                return (
                  <div
                    className="equity-bar"
                    key={`${index}-${value}`}
                    title={`₹${formatNumber(value)}`}
                  >
                    <div style={{ height: `${Math.max(height, 4)}%` }} />
                  </div>
                );
              })}
            </div>
          </article>

          <article className="workspace-card">
            <div className="card-header">
              <div>
                <span className="card-eyebrow">TRADE LEDGER</span>
                <h3>Completed Trades</h3>
              </div>

              <span className="card-badge">
                {result.execution.trades.length} TRADES
              </span>
            </div>

            {result.execution.trades.length === 0 ? (
              <div className="research-empty-state">
                <span>No completed trades were produced.</span>
              </div>
            ) : (
              <div className="research-table-wrapper">
                <table className="research-table">
                  <thead>
                    <tr>
                      <th>Symbol</th>
                      <th>Entry</th>
                      <th>Exit</th>
                      <th>Qty</th>
                      <th>Entry Price</th>
                      <th>Exit Price</th>
                      <th>Gross P&L</th>
                      <th>Costs</th>
                      <th>Net P&L</th>
                    </tr>
                  </thead>

                  <tbody>
                    {result.execution.trades.map((trade) => (
                      <tr
                        key={`${trade.entry_time}-${trade.exit_time}-${trade.symbol}`}
                      >
                        <td>{trade.symbol}</td>
                        <td>{formatDate(trade.entry_time)}</td>
                        <td>{formatDate(trade.exit_time)}</td>
                        <td>{trade.quantity}</td>
                        <td>{formatNumber(trade.entry_price)}</td>
                        <td>{formatNumber(trade.exit_price)}</td>
                        <td>{formatNumber(trade.gross_pnl)}</td>
                        <td>{formatNumber(trade.transaction_cost)}</td>
                        <td
                          className={
                            trade.net_pnl >= 0
                              ? "performance-positive"
                              : "performance-negative"
                          }
                        >
                          {formatNumber(trade.net_pnl)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </article>
        </>
      )}
    </section>
  );
}

function MetricCard({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string;
  icon: typeof TrendingUp;
}) {
  return (
    <article className="metric-card">
      <div className="metric-card-top">
        <span>{label}</span>
        <div className="metric-icon">
          <Icon size={20} />
        </div>
      </div>

      <strong>{value}</strong>
      <p>Research result</p>
    </article>
  );
}

function IdentityRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="research-identity-row">
      <span>{label}</span>
      <strong title={value}>{value}</strong>
    </div>
  );
}

function formatNumber(value: number) {
  return Number.isFinite(value) ? value.toFixed(2) : "∞";
}

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}
