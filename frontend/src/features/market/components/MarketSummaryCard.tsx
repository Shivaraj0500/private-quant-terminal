import {
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import type { MarketIndex } from "../types/market";

interface MarketSummaryCardProps {
  index: MarketIndex;
}

export function MarketSummaryCard({
  index,
}: MarketSummaryCardProps) {
  const isPositive = index.change >= 0;

  return (
    <article className="market-summary-card">
      <div className="market-summary-top">
        <div>
          <span className="market-summary-name">{index.name}</span>
          <span className="market-summary-symbol">{index.symbol}</span>
        </div>

        <span
          className={
            isPositive
              ? "market-direction market-direction-up"
              : "market-direction market-direction-down"
          }
        >
          {isPositive ? (
            <TrendingUp size={18} />
          ) : (
            <TrendingDown size={18} />
          )}
        </span>
      </div>

      <div className="market-summary-value">
        {index.value.toLocaleString("en-IN", {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })}
      </div>

      <div
        className={
          isPositive
            ? "market-summary-change positive"
            : "market-summary-change negative"
        }
      >
        <span>
          {isPositive ? "+" : ""}
          {index.change.toFixed(2)}
        </span>

        <span>
          ({isPositive ? "+" : ""}
          {index.changePercent.toFixed(2)}%)
        </span>
      </div>
    </article>
  );
}
