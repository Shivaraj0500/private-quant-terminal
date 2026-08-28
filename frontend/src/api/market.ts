import { API_BASE_URL } from "./config";
import type { MarketQuote } from "../types/market";

export async function getLatestQuote(
  symbol: string,
): Promise<MarketQuote> {
  const response = await fetch(
    `${API_BASE_URL}/market-data/${symbol}/quote`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch ${symbol} quote: ${response.status}`,
    );
  }

  return response.json() as Promise<MarketQuote>;
}

export async function getMarketQuotes(
  symbols: string[],
): Promise<MarketQuote[]> {
  return Promise.all(
    symbols.map((symbol) => getLatestQuote(symbol)),
  );
}
