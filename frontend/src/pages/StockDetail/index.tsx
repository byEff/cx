import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Row, Col, Statistic, Spin, message, Select, Space } from 'antd'
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
    return <div>股票不存在</div>
  }

  const displayTitle = stockName || code 
    ? `${code} - ${stockName || '股票详情'}` 
    : '股票详情'

  return (
    <div>
      <Card title={displayTitle} style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Statistic
              title="当前价格"
              value={quote.price}
              precision={2}
              valueStyle={{
                color: quote.changePercent && quote.changePercent > 0 ? '#f5222d' : '#52c41a'
              }}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="涨跌幅"
              value={quote.changePercent || 0}
              precision={2}
              suffix="%"
              valueStyle={{
                color: quote.changePercent && quote.changePercent > 0 ? '#f5222d' : '#52c41a'
              }}
              prefix={quote.changePercent && quote.changePercent > 0 ? <RiseOutlined /> : <FallOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成交量"
              value={quote.volume || 0}
              suffix="手"
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="成交额"
              value={quote.turnover || 0}
              precision={2}
              suffix="元"
            />
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col span={6}>
            <Statistic
              title="开盘价"
              value={quote.openPrice || 0}
              precision={2}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最高价"
              value={quote.highPrice || 0}
              precision={2}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="最低价"
              value={quote.lowPrice || 0}
              precision={2}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="昨收价"
              value={quote.preClose || 0}
              precision={2}
            />
          </Col>
        </Row>
      </Card>

      <Card 
        title="K线走势" 
        style={{ marginBottom: 24 }}
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
          <div style={{ textAlign: 'center', padding: 40, color: '#999' }}>
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
