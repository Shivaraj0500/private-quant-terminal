import {
  ArrowDownRight,
  ArrowUpRight,
} from "lucide-react";

import type { MarketMover } from "../types/market";

interface MarketMoversProps {
  title: string;
  movers: MarketMover[];
  type: "gainers" | "losers";
}

export function MarketMovers({
  title,
  movers,
  type,
}: MarketMoversProps) {
  const isGainer = type === "gainers";

  return (
    <section className="market-movers-panel">
      <div className="market-movers-header">
        <div>
          <span className="panel-eyebrow">MARKET MOVERS</span>
          <h3>{title}</h3>
        </div>

        <span
          className={
            isGainer
              ? "movers-header-icon positive"
              : "movers-header-icon negative"
          }
        >
          {isGainer ? (
            <ArrowUpRight size={18} />
          ) : (
            <ArrowDownRight size={18} />
          )}
        </span>
      </div>

      <div className="movers-list">
        {movers.map((mover) => (
          <div className="mover-row" key={mover.symbol}>
            <div>
              <strong>{mover.symbol}</strong>
              <span>{mover.name}</span>
            </div>

            <div className="mover-price">
              <strong>
                ₹
                {mover.price.toLocaleString("en-IN", {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
              </strong>

              <span
                className={
                  mover.changePercent >= 0
                    ? "positive"
                    : "negative"
                }
              >
                {mover.changePercent >= 0 ? "+" : ""}
                {mover.changePercent.toFixed(2)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
