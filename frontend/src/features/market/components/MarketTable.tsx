import { Search } from "lucide-react";
import { useMemo, useState } from "react";

import type { MarketInstrument } from "../types/market";

interface MarketTableProps {
  instruments: MarketInstrument[];
}

export function MarketTable({
  instruments,
}: MarketTableProps) {
  const [search, setSearch] = useState("");

  const filteredInstruments = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return instruments;
    }

    return instruments.filter(
      (instrument) =>
        instrument.symbol.toLowerCase().includes(query) ||
        instrument.name.toLowerCase().includes(query),
    );
  }, [instruments, search]);

  return (
    <section className="market-table-panel">
      <div className="market-table-header">
        <div>
          <span className="panel-eyebrow">INSTRUMENTS</span>
          <h3>Market Watch</h3>
        </div>

        <label className="market-table-search">
          <Search size={16} />

          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search symbol or company..."
            aria-label="Search market instruments"
          />
        </label>
      </div>

      <div className="market-table-scroll">
        <table className="market-table">
          <thead>
            <tr>
              <th>Instrument</th>
              <th>Last Price</th>
              <th>Change</th>
              <th>Change %</th>
              <th>Open</th>
              <th>High</th>
              <th>Low</th>
              <th>Volume</th>
            </tr>
          </thead>

          <tbody>
            {filteredInstruments.map((instrument) => {
              const isPositive = instrument.change >= 0;

              return (
                <tr key={instrument.symbol}>
                  <td>
                    <div className="instrument-cell">
                      <strong>{instrument.symbol}</strong>
                      <span>{instrument.name}</span>
                    </div>
                  </td>

                  <td>
                    ₹
                    {instrument.lastPrice.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </td>

                  <td
                    className={
                      isPositive
                        ? "market-positive"
                        : "market-negative"
                    }
                  >
                    {isPositive ? "+" : ""}
                    {instrument.change.toFixed(2)}
                  </td>

                  <td
                    className={
                      isPositive
                        ? "market-positive"
                        : "market-negative"
                    }
                  >
                    {isPositive ? "+" : ""}
                    {instrument.changePercent.toFixed(2)}%
                  </td>

                  <td>
                    ₹
                    {instrument.open.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                    })}
                  </td>

                  <td>
                    ₹
                    {instrument.high.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                    })}
                  </td>

                  <td>
                    ₹
                    {instrument.low.toLocaleString("en-IN", {
                      minimumFractionDigits: 2,
                    })}
                  </td>

                  <td>{instrument.volume}</td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredInstruments.length === 0 ? (
          <div className="market-empty-state">
            No instruments found.
          </div>
        ) : null}
      </div>
    </section>
  );
}
