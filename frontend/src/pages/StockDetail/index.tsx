import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Row, Col, Spin, message, Select, Space } from 'antd'
import { RiseOutlined, FallOutlined } from '@ant-design/icons'
import type { StockQuote, KlineData } from '@/types'
import { stockApi } from '@/services/api'
import KLineChart from '@/components/KLineChart'

const { Option } = Select

function StockDetail() {
  const { code } = useParams<{ code: string }>()
  const [quote, setQuote] = useState<StockQuote | null>(null)
  const [klineData, setKlineData] = useState<KlineData[]>([])
  const [loading, setLoading] = useState(false)
  const [period, setPeriod] = useState<string>('day')
  const [stockName, setStockName] = useState<string>('')

  useEffect(() => {
    if (code) {
      loadData(code)
    }
  }, [code, period])

  const loadData = async (stockCode: string) => {
    setLoading(true)
    try {
      const [quoteData, klineDataResult] = await Promise.all([
        stockApi.getStockQuote(stockCode),
        stockApi.getKlineData(stockCode, period, 200),
      ])
      setQuote(quoteData)
      setKlineData(klineDataResult)
      
      if (quoteData?.stockName) {
        setStockName(quoteData.stockName)
      }
    } catch (error) {
      message.error('加载股票数据失败')
      console.error('Failed to load stock data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePeriodChange = (value: string) => {
    setPeriod(value)
  }

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  if (!quote) {
    return <div style={{ color: '#8b949e' }}>股票不存在</div>
  }

  const displayTitle = stockName || code 
    ? `${code} - ${stockName || '股票详情'}` 
    : '股票详情'

  const isUp = quote.changePercent && quote.changePercent > 0

  return (
    <div>
      <h1 className="page-title">{displayTitle}</h1>

      {/* 行情数据 */}
      <Card style={{ marginBottom: 24 }} className="hover-card">
        <Row gutter={[24, 24]}>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">当前价格</div>
              <div className="stat-value" style={{ color: isUp ? '#ef4444' : '#22c55e' }}>
                {quote.price?.toFixed(2) || '-'}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">涨跌幅</div>
              <div className="stat-value" style={{ color: isUp ? '#ef4444' : '#22c55e' }}>
                {isUp ? <RiseOutlined style={{ marginRight: 8 }} /> : <FallOutlined style={{ marginRight: 8 }} />}
                {quote.changePercent ? `${isUp ? '+' : ''}${quote.changePercent.toFixed(2)}%` : '-'}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">成交量</div>
              <div className="stat-value">{quote.volume ? `${(quote.volume / 10000).toFixed(2)}万手` : '-'}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">成交额</div>
              <div className="stat-value">
                {quote.turnover ? `${(Number(quote.turnover) / 100000000).toFixed(2)}亿` : '-'}
              </div>
            </div>
          </Col>
        </Row>

        <Row gutter={[24, 24]} style={{ marginTop: 16 }}>
          <Col span={6}>
            <div className="stat-card" style={{ background: 'transparent', padding: 12 }}>
              <div className="stat-label">开盘价</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#f0f6fc' }}>
                {quote.openPrice?.toFixed(2) || '-'}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card" style={{ background: 'transparent', padding: 12 }}>
              <div className="stat-label">最高价</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#ef4444' }}>
                {quote.highPrice?.toFixed(2) || '-'}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card" style={{ background: 'transparent', padding: 12 }}>
              <div className="stat-label">最低价</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#22c55e' }}>
                {quote.lowPrice?.toFixed(2) || '-'}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card" style={{ background: 'transparent', padding: 12 }}>
              <div className="stat-label">昨收价</div>
              <div style={{ fontSize: 18, fontWeight: 600, color: '#f0f6fc' }}>
                {quote.preClose?.toFixed(2) || '-'}
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      {/* K线图 */}
      <Card 
        title="K线走势"
        className="hover-card"
        extra={
          <Space>
            <Select value={period} onChange={handlePeriodChange} style={{ width: 100 }}>
              <Option value="day">日K</Option>
              <Option value="week">周K</Option>
              <Option value="month">月K</Option>
            </Select>
          </Space>
        }
      >
        {klineData.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40, color: '#8b949e' }}>
            暂无K线数据
          </div>
        ) : (
          <KLineChart data={klineData} height={500} />
        )}
      </Card>
    </div>
  )
}

export default StockDetail