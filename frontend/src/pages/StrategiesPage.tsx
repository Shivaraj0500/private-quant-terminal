import { useState } from "react";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  FlaskConical,
  Play,
  Plus,
  ShieldCheck,
  TrendingUp,
  X,
} from "lucide-react";

import {
  createStrategy,
  type StrategyCondition,
  type StrategyCreateRequest,
  type StrategyVersion,
} from "../api/strategy";

type RegistryStrategy = {
  name: string;
  version: string;
  type: string;
  status: string;
  performance: string;
  positive: boolean;
  description: string;
  strategyId?: string;
};

const initialStrategies: RegistryStrategy[] = [
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

const timeframeOptions = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"];

const operatorOptions = [">", ">=", "<", "<=", "==", "!="];

const positionSizingOptions = [
  "FIXED_QUANTITY",
  "FIXED_NOTIONAL",
  "PERCENT_OF_EQUITY",
  "RISK_BASED",
];

const stopLossOptions = ["NONE", "ABSOLUTE", "PERCENT", "ATR_MULTIPLE"];

const takeProfitOptions = ["NONE", "ABSOLUTE", "PERCENT", "RISK_REWARD"];

const orderTypeOptions = ["MARKET", "LIMIT"];

const emptyCondition = (): StrategyCondition => ({
  indicator: "",
  operator: ">",
  value: 0,
});

const defaultForm = (): StrategyCreateRequest => ({
  strategy_id: "",
  name: "",
  description: "",
  instruments: ["RELIANCE"],
  timeframe: "5m",
  entry_conditions: [
    {
      indicator: "close",
      operator: ">",
      value: 100,
    },
  ],
  exit_conditions: [
    {
      indicator: "close",
      operator: "<",
      value: 95,
    },
  ],
  position_sizing: {
    method: "FIXED_QUANTITY",
    value: 1,
  },
  stop_loss: {
    type: "NONE",
    value: null,
  },
  take_profit: {
    type: "NONE",
    value: null,
  },
  execution: {
    order_type: "MARKET",
    slippage_bps: 0,
    transaction_cost_bps: 0,
  },
});

export function StrategiesPage() {
  const [strategies, setStrategies] =
    useState<RegistryStrategy[]>(initialStrategies);

  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<StrategyCreateRequest>(defaultForm);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [createdVersion, setCreatedVersion] =
    useState<StrategyVersion | null>(null);

  const updateCondition = (
    type: "entry_conditions" | "exit_conditions",
    index: number,
    field: keyof StrategyCondition,
    value: string | number,
  ) => {
    setForm((current) => ({
      ...current,
      [type]: current[type].map((condition, conditionIndex) =>
        conditionIndex === index
          ? {
              ...condition,
              [field]: value,
            }
          : condition,
      ),
    }));
  };

  const addCondition = (
    type: "entry_conditions" | "exit_conditions",
  ) => {
    setForm((current) => ({
      ...current,
      [type]: [...current[type], emptyCondition()],
    }));
  };

  const removeCondition = (
    type: "entry_conditions" | "exit_conditions",
    index: number,
  ) => {
    setForm((current) => ({
      ...current,
      [type]: current[type].filter(
        (_, conditionIndex) => conditionIndex !== index,
      ),
    }));
  };

  const openCreate = () => {
    setForm(defaultForm());
    setError("");
    setCreatedVersion(null);
    setShowCreate(true);
  };

  const closeCreate = () => {
    if (submitting) {
      return;
    }

    setShowCreate(false);
    setError("");
    setCreatedVersion(null);
  };

  const submitStrategy = async () => {
    setError("");
    setCreatedVersion(null);

    if (!form.strategy_id.trim()) {
      setError("Strategy ID is required.");
      return;
    }

    if (!form.name.trim()) {
      setError("Strategy name is required.");
      return;
    }

    if (form.entry_conditions.some(
      (condition) => !condition.indicator.trim(),
    )) {
      setError("Every entry condition needs an indicator.");
      return;
    }

    if (form.exit_conditions.some(
      (condition) => !condition.indicator.trim(),
    )) {
      setError("Every exit condition needs an indicator.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await createStrategy(form);
      const version = response.version;

      setCreatedVersion(version);

      setStrategies((current) => [
        {
          name: version.name,
          version: `v${version.version}.0.0`,
          type: "Systematic",
          status: version.status,
          performance: "—",
          positive: true,
          description: version.description || "Newly validated strategy.",
          strategyId: version.strategy_id,
        },
        ...current,
      ]);

      setShowCreate(false);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to create strategy.",
      );
    } finally {
      setSubmitting(false);
    }
  };

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

      {error && (
        <div className="strategy-form-error">
          <strong>Strategy creation failed</strong>
          <span>{error}</span>
        </div>
      )}

      {createdVersion && (
        <div className="strategy-form-success">
          <CheckCircle2 size={18} />
          <div>
            <strong>
              Strategy {createdVersion.strategy_id} v
              {createdVersion.version} created successfully
            </strong>
            <span>
              Status: {createdVersion.status} · Hash:{" "}
              {createdVersion.strategy_hash}
            </span>
          </div>
        </div>
      )}

      <div className="strategy-summary-grid">
        <div className="metric-card">
          <div className="metric-card-top">
            <span>Active Strategies</span>
            <div className="metric-icon">
              <FlaskConical size={20} />
            </div>
          </div>
          <strong className="metric-value">{strategies.length}</strong>
          <span className="metric-positive">
            Research pipeline active
          </span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Validated</span>
            <div className="metric-icon">
              <CheckCircle2 size={20} />
            </div>
          </div>
          <strong className="metric-value">
            {
              strategies.filter(
                (strategy) => strategy.status === "VALIDATED",
              ).length + 1
            }
          </strong>
          <span className="metric-positive">
            Validation pipeline
          </span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Backtest Runs</span>
            <div className="metric-icon">
              <BarChart3 size={20} />
            </div>
          </div>
          <strong className="metric-value">24</strong>
          <span className="metric-muted">
            Development environment
          </span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span>Deployment Ready</span>
            <div className="metric-icon">
              <ShieldCheck size={20} />
            </div>
          </div>
          <strong className="metric-value">1</strong>
          <span className="metric-positive">
            Paper trading eligible
          </span>
        </div>
      </div>

      {showCreate && (
        <article className="workspace-card strategy-create-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">STRATEGY BUILDER</span>
              <h3>Create Strategy</h3>
            </div>

            <button
              type="button"
              className="strategy-form-close"
              onClick={closeCreate}
              aria-label="Close strategy builder"
            >
              <X size={18} />
            </button>
          </div>

          <div className="strategy-form">
            <div className="strategy-form-grid strategy-form-grid-two">
              <label className="strategy-field">
                <span>Strategy ID</span>
                <input
                  value={form.strategy_id}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      strategy_id: event.target.value,
                    }))
                  }
                  placeholder="reliance-momentum"
                />
              </label>

              <label className="strategy-field">
                <span>Name</span>
                <input
                  value={form.name}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  placeholder="Reliance Momentum Strategy"
                />
              </label>
            </div>

            <label className="strategy-field">
              <span>Description</span>
              <textarea
                value={form.description}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    description: event.target.value,
                  }))
                }
                placeholder="Describe the research hypothesis and intended behavior."
                rows={3}
              />
            </label>

            <div className="strategy-form-grid strategy-form-grid-two">
              <label className="strategy-field">
                <span>Instrument</span>
                <input
                  value={form.instruments[0] ?? ""}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      instruments: [event.target.value],
                    }))
                  }
                  placeholder="RELIANCE"
                />
              </label>

              <label className="strategy-field">
                <span>Timeframe</span>
                <select
                  value={form.timeframe}
                  onChange={(event) =>
                    setForm((current) => ({
                      ...current,
                      timeframe: event.target.value,
                    }))
                  }
                >
                  {timeframeOptions.map((timeframe) => (
                    <option key={timeframe} value={timeframe}>
                      {timeframe}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <StrategyConditionEditor
              title="Entry Conditions"
              conditions={form.entry_conditions}
              onAdd={() => addCondition("entry_conditions")}
              onRemove={(index) =>
                removeCondition("entry_conditions", index)
              }
              onChange={(index, field, value) =>
                updateCondition(
                  "entry_conditions",
                  index,
                  field,
                  value,
                )
              }
            />

            <StrategyConditionEditor
              title="Exit Conditions"
              conditions={form.exit_conditions}
              onAdd={() => addCondition("exit_conditions")}
              onRemove={(index) =>
                removeCondition("exit_conditions", index)
              }
              onChange={(index, field, value) =>
                updateCondition(
                  "exit_conditions",
                  index,
                  field,
                  value,
                )
              }
            />

            <div className="strategy-form-section">
              <div className="strategy-form-section-header">
                <span>Position Sizing</span>
              </div>

              <div className="strategy-form-grid strategy-form-grid-two">
                <label className="strategy-field">
                  <span>Method</span>
                  <select
                    value={form.position_sizing.method}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        position_sizing: {
                          ...current.position_sizing,
                          method: event.target.value,
                        },
                      }))
                    }
                  >
                    {positionSizingOptions.map((method) => (
                      <option key={method} value={method}>
                        {method}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="strategy-field">
                  <span>Value</span>
                  <input
                    type="number"
                    min="0"
                    value={form.position_sizing.value}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        position_sizing: {
                          ...current.position_sizing,
                          value: Number(event.target.value),
                        },
                      }))
                    }
                  />
                </label>
              </div>
            </div>

            <div className="strategy-form-grid strategy-form-grid-two">
              <RuleSelect
                label="Stop Loss"
                value={form.stop_loss.type}
                options={stopLossOptions}
                onChange={(value) =>
                  setForm((current) => ({
                    ...current,
                    stop_loss: {
                      type: value,
                      value: value === "NONE"
                        ? null
                        : current.stop_loss.value ?? 0,
                    },
                  }))
                }
              />

              <RuleSelect
                label="Take Profit"
                value={form.take_profit.type}
                options={takeProfitOptions}
                onChange={(value) =>
                  setForm((current) => ({
                    ...current,
                    take_profit: {
                      type: value,
                      value: value === "NONE"
                        ? null
                        : current.take_profit.value ?? 0,
                    },
                  }))
                }
              />
            </div>

            <div className="strategy-form-section">
              <div className="strategy-form-section-header">
                <span>Execution Assumptions</span>
              </div>

              <div className="strategy-form-grid strategy-form-grid-three">
                <label className="strategy-field">
                  <span>Order Type</span>
                  <select
                    value={form.execution.order_type}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        execution: {
                          ...current.execution,
                          order_type: event.target.value,
                        },
                      }))
                    }
                  >
                    {orderTypeOptions.map((orderType) => (
                      <option key={orderType} value={orderType}>
                        {orderType}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="strategy-field">
                  <span>Slippage (bps)</span>
                  <input
                    type="number"
                    min="0"
                    value={form.execution.slippage_bps}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        execution: {
                          ...current.execution,
                          slippage_bps: Number(
                            event.target.value,
                          ),
                        },
                      }))
                    }
                  />
                </label>

                <label className="strategy-field">
                  <span>Transaction Cost (bps)</span>
                  <input
                    type="number"
                    min="0"
                    value={form.execution.transaction_cost_bps}
                    onChange={(event) =>
                      setForm((current) => ({
                        ...current,
                        execution: {
                          ...current.execution,
                          transaction_cost_bps: Number(
                            event.target.value,
                          ),
                        },
                      }))
                    }
                  />
                </label>
              </div>
            </div>

            <div className="strategy-form-actions">
              <button
                type="button"
                className="strategy-secondary-button"
                onClick={closeCreate}
                disabled={submitting}
              >
                Cancel
              </button>

              <button
                type="button"
                className="strategy-primary-button"
                onClick={submitStrategy}
                disabled={submitting}
              >
                {submitting ? "Creating..." : "Create & Validate"}
              </button>
            </div>
          </div>
        </article>
      )}

      <div className="strategy-main-grid">
        <article className="workspace-card">
          <div className="card-header">
            <div>
              <span className="card-eyebrow">STRATEGY REGISTRY</span>
              <h3>Research Strategies</h3>
            </div>

            <div className="strategy-registry-actions">
              <span className="card-badge">
                {strategies.length} REGISTERED
              </span>

              <button
                type="button"
                className="strategy-create-button"
                onClick={openCreate}
              >
                <Plus size={15} />
                Create Strategy
              </button>
            </div>
          </div>

          <div className="strategy-list">
            {strategies.map((strategy) => (
              <div
                className="strategy-item"
                key={`${strategy.strategyId ?? strategy.name}-${strategy.version}`}
              >
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
                        strategy.status === "Validated" ||
                        strategy.status === "VALIDATED"
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

function StrategyConditionEditor({
  title,
  conditions,
  onAdd,
  onRemove,
  onChange,
}: {
  title: string;
  conditions: StrategyCondition[];
  onAdd: () => void;
  onRemove: (index: number) => void;
  onChange: (
    index: number,
    field: keyof StrategyCondition,
    value: string | number,
  ) => void;
}) {
  return (
    <div className="strategy-form-section">
      <div className="strategy-form-section-header">
        <span>{title}</span>
        <button
          type="button"
          className="strategy-inline-button"
          onClick={onAdd}
        >
          <Plus size={14} />
          Add condition
        </button>
      </div>

      <div className="strategy-condition-list">
        {conditions.map((condition, index) => (
          <div className="strategy-condition-row" key={index}>
            <input
              value={condition.indicator}
              onChange={(event) =>
                onChange(
                  index,
                  "indicator",
                  event.target.value,
                )
              }
              placeholder="close / EMA_20 / RSI_14"
            />

            <select
              value={condition.operator}
              onChange={(event) =>
                onChange(
                  index,
                  "operator",
                  event.target.value,
                )
              }
            >
              {operatorOptions.map((operator) => (
                <option key={operator} value={operator}>
                  {operator}
                </option>
              ))}
            </select>

            <input
              type="number"
              value={condition.value}
              onChange={(event) =>
                onChange(
                  index,
                  "value",
                  Number(event.target.value),
                )
              }
            />

            <button
              type="button"
              className="strategy-condition-remove"
              onClick={() => onRemove(index)}
              disabled={conditions.length <= 1}
              aria-label={`Remove ${title.toLowerCase()} condition`}
            >
              <X size={15} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

function RuleSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (value: string) => void;
}) {
  return (
    <label className="strategy-field">
      <span>{label}</span>
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </label>
  );
}
