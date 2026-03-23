export interface Stock {
  code: string
  name: string
  price?: number
  changePercent?: number
  volume?: number
  turnover?: number
  turnoverRate?: number
  amplitude?: number
  peRatio?: number
  totalMarketValue?: number
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

// Market Sentiment Types
export interface UpDownDistribution {
  upCount: number
  downCount: number
  flatCount: number
  limitUp: number
  limitDown: number
  upLimitCount?: number
  downLimitCount?: number
  timestamp: string
}

export interface LimitUpStats {
  totalCount: number
  sealCount: number
  openCount: number
  timeDistribution?: Record<string, number>
  boardDistribution?: Record<string, number>
  timestamp: string
}

// ETF Types
export interface ETF {
  code: string
  name: string
  price?: number
  changePercent?: number
  volume?: number
  turnover?: number
  market?: string
  type?: string
}

export interface ETFQuote {
  code: string
  name: string
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

// Portfolio Types
export interface PortfolioGroup {
  id: number
  name: string
  userId: number
  createdAt: string
}

export interface Position {
  id: number
  groupId: number
  stockCode: string
  stockName?: string
  costPrice: number
  quantity: number
  createdAt: string
}

export interface ProfitLossItem {
  positionId: number
  stockCode: string
  stockName?: string
  quantity: number
  costPrice: number
  currentPrice?: number
  marketValue?: number
  profitLoss?: number
  profitLossPercent?: number
}

export interface ProfitLossSummary {
  totalCost: number
  totalMarketValue?: number
  totalProfitLoss?: number
  totalProfitLossPercent?: number
  positions: ProfitLossItem[]
}
