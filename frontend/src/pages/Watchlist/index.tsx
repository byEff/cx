import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Table, Button, Popconfirm, message, Statistic, Row, Col } from 'antd'
import { DeleteOutlined } from '@ant-design/icons'
import type { WatchlistItem, StockQuote } from '@/types'
import { watchlistApi, stockApi } from '@/services/api'

function WatchlistPage() {
  const navigate = useNavigate()
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([])
  const [quotes, setQuotes] = useState<Map<string, StockQuote>>(new Map())
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadWatchlist()
  }, [])

  const loadWatchlist = async () => {
    setLoading(true)
    try {
      const data = await watchlistApi.getWatchlist()
      setWatchlist(data)
      
      if (data.length > 0) {
        const codes = data.map(item => item.stockCode)
        const quotesData = await stockApi.getRealtimeQuotes(codes)
        const quotesMap = new Map(quotesData.map(q => [q.stockCode, q]))
        setQuotes(quotesMap)
      }
    } catch (error) {
      message.error('加载自选股失败')
      console.error('Failed to load watchlist:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRemove = async (id: number) => {
    try {
      await watchlistApi.removeFromWatchlist(id)
      message.success('已从自选股删除')
      loadWatchlist()
    } catch (error) {
      message.error('删除失败')
      console.error('Remove failed:', error)
    }
  }

  const columns = [
    {
      title: '代码',
      dataIndex: 'stockCode',
      key: 'stockCode',
      width: 100,
      render: (code: string) => <a onClick={() => navigate(`/stock/${code}`)}>{code}</a>,
    },
    {
      title: '加入价格',
      dataIndex: 'addPrice',
      key: 'addPrice',
      width: 120,
      render: (price: number | string) => {
        const num = typeof price === 'string' ? parseFloat(price) : price
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '当前价格',
      key: 'currentPrice',
      width: 120,
      render: (_: any, record: WatchlistItem) => {
        const quote = quotes.get(record.stockCode)
        if (!quote) return '-'
        const price = typeof quote.price === 'string' ? parseFloat(quote.price) : quote.price
        return price ? price.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      key: 'changePercent',
      width: 120,
      render: (_: any, record: WatchlistItem) => {
        const quote = quotes.get(record.stockCode)
        if (!quote) return '-'
        const change = typeof quote.changePercent === 'string' ? parseFloat(quote.changePercent) : quote.changePercent
        if (!change) return '-'
        return (
          <span className={change > 0 ? 'stock-up' : 'stock-down'}>
            {change > 0 ? '+' : ''}{change.toFixed(2)}%
          </span>
        )
      },
    },
    {
      title: '盈亏',
      key: 'profit',
      width: 120,
      render: (_: any, record: WatchlistItem) => {
        const quote = quotes.get(record.stockCode)
        const price = quote ? (typeof quote.price === 'string' ? parseFloat(quote.price) : quote.price) : 0
        const addPrice = typeof record.addPrice === 'string' ? parseFloat(record.addPrice) : record.addPrice
        
        if (!quote || !addPrice) return '-'
        const profit = ((price - addPrice) / addPrice) * 100
        return (
          <span className={profit > 0 ? 'stock-up' : 'stock-down'}>
            {profit > 0 ? '+' : ''}{profit.toFixed(2)}%
          </span>
        )
      },
    },
    {
      title: '加入时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 180,
      render: (time: string) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: WatchlistItem) => (
        <>
          <Button type="link" onClick={() => navigate(`/stock/${record.stockCode}`)}>
            详情
          </Button>
          <Popconfirm
            title="确定要删除吗?"
            onConfirm={() => handleRemove(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </>
      ),
    },
  ]

  const getTotalProfit = () => {
    let total = 0
    watchlist.forEach(item => {
      const quote = quotes.get(item.stockCode)
      if (quote && item.addPrice) {
        total += ((quote.price - item.addPrice) / item.addPrice) * 100
      }
    })
    return total / watchlist.length || 0
  }

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col span={8}>
            <Statistic
              title="自选股数量"
              value={watchlist.length}
              suffix="只"
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="平均盈亏"
              value={getTotalProfit()}
              precision={2}
              suffix="%"
              valueStyle={{
                color: getTotalProfit() > 0 ? '#f5222d' : '#52c41a'
              }}
            />
          </Col>
          <Col span={8}>
            <Button type="primary" onClick={loadWatchlist}>
              刷新数据
            </Button>
          </Col>
        </Row>
      </Card>

      <Card title="我的自选股">
        <Table
          dataSource={watchlist}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>
    </div>
  )
}

export default WatchlistPage
