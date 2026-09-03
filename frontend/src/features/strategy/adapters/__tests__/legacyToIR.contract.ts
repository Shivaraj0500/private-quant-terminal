import type { StrategyCreateRequest } from "../../../../api/strategy";
import { legacyStrategyToIR } from "../legacyToIR";

const legacyStrategy: StrategyCreateRequest = {
  strategy_id: "reliance-momentum",
  name: "Reliance Momentum",
  description: "Legacy momentum strategy.",
  instruments: ["reliance"],
  timeframe: "5m",

  entry_conditions: [
    {
      indicator: "close",
      operator: ">",
      value: 100,
    },
    {
      indicator: "EMA_20",
      operator: ">=",
      value: 95,
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
    slippage_bps: 2,
    transaction_cost_bps: 1,
  },
};

export const legacyToIRContractExample =
  legacyStrategyToIR(legacyStrategy);
