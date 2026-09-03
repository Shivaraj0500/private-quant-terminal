import type { StrategyIR } from "../ir";

export const strategyIRContractExample: StrategyIR = {
  strategy_id: "atr-straddle",
  name: "ATR Re-centering Short Straddle",
  description: "Stateful multi-leg options strategy.",
  version: 1,
  status: "DRAFT",

  instruments: ["NIFTY"],
  timeframe: "5m",

  variables: [
    {
      name: "anchor_price",
      type: "NUMBER",
      scope: "STRATEGY",
      value: 0,
    },
  ],

  rules: [
    {
      rule_id: "initial-entry",
      condition: {
        left: {
          type: "INDICATOR",
          indicator: "ATR_14",
        },
        operator: ">",
        right: {
          type: "VALUE",
          value: 10,
        },
      },
      actions: [
        {
          type: "ENTER",
          position_group: {
            group_id: "short-straddle",
            name: "Short Straddle",
            legs: [
              {
                instrument_type: "OPTION",
                action: "SELL",
                option_type: "CALL",
                strike: "ATM",
                expiry: "CURRENT",
                quantity: 1,
              },
              {
                instrument_type: "OPTION",
                action: "SELL",
                option_type: "PUT",
                strike: "ATM",
                expiry: "CURRENT",
                quantity: 1,
              },
            ],
          },
        },
      ],
    },
  ],

  states: [
    {
      state_id: "initial",
      name: "Initial",
      initial: true,
    },
    {
      state_id: "recentered",
      name: "Recentered",
    },
  ],

  transitions: [
    {
      transition_id: "move-to-recentered",
      from_state: "initial",
      to_state: "recentered",
      condition: {
        left: {
          type: "PRICE",
          symbol: "NIFTY",
        },
        operator: ">",
        right: {
          type: "VARIABLE",
          variable: "anchor_price",
        },
      },
      actions: [
        {
          type: "EXIT",
          group_id: "short-straddle",
        },
      ],
    },
  ],

  data_requirements: [
    {
      requirement_id: "nifty-5m",
      source: "market",
      symbol: "NIFTY",
      timeframe: "5m",
      fields: ["open", "high", "low", "close"],
    },
  ],

  position_groups: [],

  session: {
    mode: "INTRADAY",
  },

  position_sizing: {
    method: "FIXED",
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
    slippage_bps: 2,
    transaction_cost_bps: 1,
  },
};
