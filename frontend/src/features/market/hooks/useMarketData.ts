import {
  mockMarketIndices,
  mockMarketInstruments,
  mockTopGainers,
  mockTopLosers,
} from "../data/mockMarketData";

export function useMarketData() {
  return {
    indices: mockMarketIndices,
    instruments: mockMarketInstruments,
    topGainers: mockTopGainers,
    topLosers: mockTopLosers,
    isLoading: false,
    error: null,
  };
}
