import axios from 'axios'
import type { StockQuote, KlineData, WatchlistItem, Alert, TechnicalIndicators, MarketNews, Stock, UpDownDistribution, LimitUpStats, ETF, ETFQuote, PortfolioGroup, Position, ProfitLossSummary } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export const stockApi = {
  getRealtimeQuotes: async (codes?: string[]): Promise<StockQuote[]> => {
    const params = codes ? { codes: codes.join(',') } : {}
    const { data } = await api.get('/stocks/realtime', { params })
    return data
  },

  getStockQuote: async (code: string): Promise<StockQuote> => {
    const { data } = await api.get(`/stocks/${code}/quote`)
    return data
  },

  getKlineData: async (
    code: string,
    period: string = 'day',
    limit: number = 200
  ): Promise<KlineData[]> => {
    const { data } = await api.get(`/stocks/${code}/kline`, {
      params: { period, limit }
    })
    return data
  },

  searchStocks: async (keyword: string): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/search', {
      params: { keyword }
    })
    return data
  },

  filterStocks: async (params: {
    industry?: string
    minChange?: number
    maxChange?: number
    minVolume?: number
    limit?: number
  }): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/filter', { params })
    return data
  },

  getTechnicalAnalysis: async (code: string): Promise<TechnicalIndicators> => {
    const { data } = await api.get(`/stocks/${code}/analysis`)
    return data
  },

  // 高级筛选
  getLimitUpStocks: async (limit: number = 50): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/limit-up', { params: { limit } })
    return data
  },

  getLimitDownStocks: async (limit: number = 50): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/limit-down', { params: { limit } })
    return data
  },

  getNewStocks: async (limit: number = 50): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/new-listing', { params: { limit } })
    return data
  },

  getKcbStocks: async (limit: number = 50): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/kcb', { params: { limit } })
    return data
  },

  getCybStocks: async (limit: number = 50): Promise<Stock[]> => {
    const { data } = await api.get('/stocks/cyb', { params: { limit } })
    return data
  },
}

export const watchlistApi = {
  getWatchlist: async (): Promise<WatchlistItem[]> => {
    const { data } = await api.get('/watchlist')
    return data
  },

  addToWatchlist: async (stockCode: string, addPrice?: number): Promise<WatchlistItem> => {
    const { data } = await api.post('/watchlist', { stock_code: stockCode, add_price: addPrice })
    return data
  },

  removeFromWatchlist: async (id: number): Promise<void> => {
    await api.delete(`/watchlist/${id}`)
  },
}

export const alertApi = {
  getAlerts: async (): Promise<Alert[]> => {
    const { data } = await api.get('/alerts')
    return data
  },

  createAlert: async (stockCode: string, alertType: string, threshold: number): Promise<Alert> => {
    const { data } = await api.post('/alerts', {
      stock_code: stockCode,
      alert_type: alertType,
      threshold
    })
    return data
  },

  deactivateAlert: async (id: number): Promise<void> => {
    await api.put(`/alerts/${id}/deactivate`)
  },

  deleteAlert: async (id: number): Promise<void> => {
    await api.delete(`/alerts/${id}`)
  },
}

export const marketApi = {
  getMarketNews: async (limit: number = 20): Promise<MarketNews[]> => {
    const { data } = await api.get('/market/news', { params: { limit } })
    return data
  },

  getMarketIndices: async (): Promise<Stock[]> => {
    const { data } = await api.get('/market/index')
    return data
  },

  getTopGainers: async (limit: number = 10): Promise<Stock[]> => {
    const { data } = await api.get('/market/top-gainers', { params: { limit } })
    return data
  },

  getTopLosers: async (limit: number = 10): Promise<Stock[]> => {
    const { data } = await api.get('/market/top-losers', { params: { limit } })
    return data
  },

  getHotSectors: async (): Promise<any[]> => {
    const { data } = await api.get('/market/hot-sectors')
    return data
  },

  // 市场情绪
  getUpDownDistribution: async (): Promise<UpDownDistribution> => {
    const { data } = await api.get('/market/up-down-distribution')
    return data
  },

  getLimitUpStats: async (): Promise<LimitUpStats> => {
    const { data } = await api.get('/market/limit-up-stats')
    return data
  },

  getHotStocks: async (limit: number = 20): Promise<Stock[]> => {
    const { data } = await api.get('/market/hot-stocks', { params: { limit } })
    return data
  },
}

// ETF API
export const etfApi = {
  getEtfList: async (limit: number = 100, etfType?: string): Promise<ETF[]> => {
    const params: any = { limit }
    if (etfType) params.etf_type = etfType
    const { data } = await api.get('/etf/list', { params })
    return data
  },

  getEtfQuote: async (code: string): Promise<ETFQuote> => {
    const { data } = await api.get(`/etf/${code}/quote`)
    return data
  },

  getEtfQuotes: async (codes: string[]): Promise<ETFQuote[]> => {
    const { data } = await api.get('/etf/quotes', { params: { codes: codes.join(',') } })
    return data
  },
}

// Portfolio API
export const portfolioApi = {
  // 分组管理
  getGroups: async (): Promise<PortfolioGroup[]> => {
    const { data } = await api.get('/portfolio/groups')
    return data
  },

  createGroup: async (name: string): Promise<PortfolioGroup> => {
    const { data } = await api.post('/portfolio/groups', { name })
    return data
  },

  deleteGroup: async (id: number): Promise<void> => {
    await api.delete(`/portfolio/groups/${id}`)
  },

  // 持仓管理
  getPositions: async (groupId?: number): Promise<Position[]> => {
    const params = groupId ? { group_id: groupId } : {}
    const { data } = await api.get('/portfolio/positions', { params })
    return data
  },

  createPosition: async (position: {
    group_id: number
    stock_code: string
    stock_name?: string
    cost_price: number
    quantity: number
  }): Promise<Position> => {
    const { data } = await api.post('/portfolio/positions', position)
    return data
  },

  updatePosition: async (id: number, updates: {
    cost_price?: number
    quantity?: number
  }): Promise<Position> => {
    const { data } = await api.put(`/portfolio/positions/${id}`, updates)
    return data
  },

  deletePosition: async (id: number): Promise<void> => {
    await api.delete(`/portfolio/positions/${id}`)
  },

  // 盈亏计算
  getProfitLoss: async (groupId?: number): Promise<ProfitLossSummary> => {
    const params = groupId ? { group_id: groupId } : {}
    const { data } = await api.get('/portfolio/profit-loss', { params })
    return data
  },
}

export default api
