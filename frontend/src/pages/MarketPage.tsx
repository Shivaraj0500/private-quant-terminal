import {
  Activity,
  Database,
  LoaderCircle,
  TriangleAlert,
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
    isLoading,
    error,
  } = useMarketData();


  return (
    <div className="page market-page">
      <div className="page-header market-page-header">
        <div>
          <span className="page-eyebrow">MARKET INTELLIGENCE</span>

          <h2>Market Workspace</h2>

          <p>
            Monitor live instruments, market movement, and trading data
            from the Private Quant Terminal backend.
          </p>
        </div>

        <div className="market-status">
          <span className="market-status-icon">
            {isLoading ? (
              <LoaderCircle size={17} />
            ) : error ? (
              <TriangleAlert size={17} />
            ) : (
              <Activity size={17} />
            )}
          </span>

          <div>
            <span className="market-status-label">Market Data</span>

            <strong>
              {isLoading
                ? "Loading..."
                : error
                  ? "Connection Error"
                  : "Backend Connected"}
            </strong>
          </div>
        </div>
      </div>

      {error ? (
        <div className="market-data-info">
          <div className="market-data-info-icon">
            <TriangleAlert size={20} />
          </div>

          <div>
            <span className="panel-eyebrow">API ERROR</span>
            <h3>Unable to load market data</h3>
            <p>{error}</p>
          </div>
        </div>
      ) : null}

      {indices.length > 0 ? (
        <section className="market-index-grid">
          {indices.map((index) => (
            <MarketSummaryCard
              key={index.id}
              index={index}
            />
          ))}
        </section>
      ) : null}

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
            <span className="panel-eyebrow">LIVE BACKEND DATA</span>
            <h3>
              {instruments.length} Instruments Loaded
            </h3>

            <p>
              Quotes are fetched from the Private Quant Terminal backend and
              refresh automatically every 30 seconds.
            </p>
          </div>
        </div>
      </section>

      <MarketTable instruments={instruments} />
    </div>
  );
}
