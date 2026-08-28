import {
  Activity,
  Database,
} from "lucide-react";

import { MarketMovers } from "../features/market/components/MarketMovers";
import { MarketSummaryCard } from "../features/market/components/MarketSummaryCard";
import { MarketTable } from "../features/market/components/MarketTable";
import { useMarketData } from "../features/market/hooks/useMarketData";

export function MarketPage() {
  const {
    indices,
    instruments,
    topGainers,
    topLosers,
  } = useMarketData();

  return (
    <div className="page market-page">
      <div className="page-header market-page-header">
        <div>
          <span className="page-eyebrow">MARKET INTELLIGENCE</span>

          <h2>Market Workspace</h2>

          <p>
            Monitor indices, instruments, market movement, and trading data
            from a unified research workspace.
          </p>
        </div>

        <div className="market-status">
          <span className="market-status-icon">
            <Activity size={17} />
          </span>

          <div>
            <span className="market-status-label">Market Data</span>
            <strong>Development Mode</strong>
          </div>
        </div>
      </div>

      <section className="market-index-grid">
        {indices.map((index) => (
          <MarketSummaryCard
            key={index.id}
            index={index}
          />
        ))}
      </section>

      <section className="market-movers-grid">
        <MarketMovers
          title="Top Gainers"
          movers={topGainers}
          type="gainers"
        />

        <MarketMovers
          title="Top Losers"
          movers={topLosers}
          type="losers"
        />

        <div className="market-data-info">
          <div className="market-data-info-icon">
            <Database size={20} />
          </div>

          <div>
            <span className="panel-eyebrow">DATA SOURCE</span>
            <h3>Backend Integration Ready</h3>

            <p>
              The Market module currently uses a structured mock data layer.
              The same interface will later connect directly to the Private
              Quant backend API.
            </p>
          </div>
        </div>
      </section>

      <MarketTable instruments={instruments} />
    </div>
  );
}
