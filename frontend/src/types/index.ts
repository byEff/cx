export interface Stock {
  code: string
  name: string
  price?: number
  changePercent?: number
  industry?: string
  market?: string
}

export interface StockQuote {
  id: number
  stockCode: string
  stockName?: string
  price: number
  openPrice?: number
  highPrice?: number
  lowPrice?: number
  preClose?: number
  changePercent?: number
  volume?: number
  turnover?: number
  timestamp: string
}

export interface KlineData {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface WatchlistItem {
  id: number
  stockCode: string
  addPrice?: number
  createdAt: string
}

export interface Alert {
  id: number
  stockCode: string
  alertType: string
  threshold: number
  isActive: boolean
  triggeredAt?: string
  createdAt: string
}

export interface TechnicalIndicators {
  ma5?: number
  ma10?: number
  ma20?: number
  macd?: number
  macdSignal?: number
  macdHist?: number
  rsi?: number
  kdjK?: number
  kdjD?: number
  kdjJ?: number
}

export interface MarketNews {
  id: number
  title: string
  content?: string
  source?: string
  newsTime?: string
  url?: string
  createdAt: string
}
