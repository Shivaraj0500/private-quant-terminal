export type MarketDirection = "up" | "down" | "neutral";

export interface MarketIndex {
  id: string;
  name: string;
  symbol: string;
  value: number;
  change: number;
  changePercent: number;
}

export interface MarketInstrument {
  symbol: string;
  name: string;
  lastPrice: number;
  change: number;
  changePercent: number;
  open: number;
  high: number;
  low: number;
  volume: string;
}

export interface MarketMover {
  symbol: string;
  name: string;
  price: number;
  changePercent: number;
}
