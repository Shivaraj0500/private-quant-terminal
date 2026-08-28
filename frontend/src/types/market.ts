export interface MarketQuote {
  symbol: string;
  exchange: string;
  timestamp: string;
  last_price: number;
  open: number | null;
  high: number | null;
  low: number | null;
  previous_close: number | null;
  volume: number | null;
}
