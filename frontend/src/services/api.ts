import axios from 'axios'
import type { StockQuote, KlineData, WatchlistItem, Alert, TechnicalIndicators, MarketNews, Stock } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
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
}

export default api
