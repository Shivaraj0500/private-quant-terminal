import { useQueries } from "@tanstack/react-query";

import { getLatestQuote } from "../../../api/market";
import type {
  MarketIndex,
  MarketInstrument,
  MarketMover,
} from "../types/market";

const MARKET_SYMBOLS = [
  "RELIANCE",
  "TCS",
  "HDFCBANK",
  "INFY",
  "ICICIBANK",
  "SBIN",
  "ITC",
  "LT",
] as const;

const INSTRUMENT_NAMES: Record<string, string> = {
  RELIANCE: "Reliance Industries",
  TCS: "Tata Consultancy Services",
  HDFCBANK: "HDFC Bank",
  INFY: "Infosys",
  ICICIBANK: "ICICI Bank",
  SBIN: "State Bank of India",
  ITC: "ITC Limited",
  LT: "Larsen & Toubro",
};

function calculateChange(
  lastPrice: number,
  previousClose: number | null,
) {
  if (previousClose === null || previousClose === 0) {
    return {
      change: 0,
      changePercent: 0,
    };
  }

  const change = lastPrice - previousClose;

  return {
    change,
    changePercent: (change / previousClose) * 100,
  };
}

function formatVolume(volume: number | null): string {
  if (volume === null || volume === undefined) {
    return "—";
  }

  if (volume >= 1_000_000) {
    return `${(volume / 1_000_000).toFixed(2)}M`;
  }

  if (volume >= 1_000) {
    return `${(volume / 1_000).toFixed(2)}K`;
  }

  return volume.toFixed(0);
}

export function useMarketData() {
  const quoteQueries = useQueries({
    queries: MARKET_SYMBOLS.map((symbol) => ({
      queryKey: ["market-data", "quote", symbol],
      queryFn: () => getLatestQuote(symbol),
      refetchInterval: 30_000,
      staleTime: 10_000,
      retry: 1,
    })),
  });

  const failedSymbols = new Set(
    quoteQueries
      .map((query, index) =>
        query.error ? MARKET_SYMBOLS[index] : null,
      )
      .filter((symbol) => symbol !== null),
  );

  const successfulQuotes = quoteQueries
    .map((query) => query.data)
    .filter((quote) => quote !== undefined);

  const isLoading =
    successfulQuotes.length === 0 &&
    quoteQueries.some((query) => query.isLoading);

  const hasAnyData = successfulQuotes.length > 0;

  const error =
    !hasAnyData && failedSymbols.size > 0
      ? "Unable to connect to the market data backend."
      : null;

  const instruments: MarketInstrument[] = successfulQuotes.map(
    (quote) => {
      const { change, changePercent } = calculateChange(
        quote.last_price,
        quote.previous_close,
      );

      return {
        symbol: quote.symbol,
        name: INSTRUMENT_NAMES[quote.symbol] ?? quote.symbol,
        lastPrice: quote.last_price,
        change,
        changePercent,
        open: quote.open ?? 0,
        high: quote.high ?? 0,
        low: quote.low ?? 0,
        volume: formatVolume(quote.volume),
      };
    },
  );

  const sortedByPerformance = [...instruments].sort(
    (a, b) => b.changePercent - a.changePercent,
  );

  const topGainers: MarketMover[] = sortedByPerformance
    .filter((instrument) => instrument.changePercent > 0)
    .slice(0, 4)
    .map((instrument) => ({
      symbol: instrument.symbol,
      name: instrument.name,
      price: instrument.lastPrice,
      changePercent: instrument.changePercent,
    }));

  const topLosers: MarketMover[] = sortedByPerformance
    .filter((instrument) => instrument.changePercent < 0)
    .slice(0, 4)
    .reverse()
    .map((instrument) => ({
      symbol: instrument.symbol,
      name: instrument.name,
      price: instrument.lastPrice,
      changePercent: instrument.changePercent,
    }));

  const indices: MarketIndex[] = [];

  return {
    indices,
    instruments,
    topGainers,
    topLosers,
    isLoading,
    error,
    failedSymbols: Array.from(failedSymbols),
    loadedCount: instruments.length,
  };
}
