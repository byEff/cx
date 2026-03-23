import { useState, useEffect } from 'react'
import { Card, Table, Spin, message, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import { stockApi } from '@/services/api'
import type { Stock } from '@/types'

export default function Cyb() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [stocks, setStocks] = useState<Stock[]>([])

  useEffect(() => {
    fetchStocks()
  }, [])

  const fetchStocks = async () => {
    setLoading(true)
    try {
      const data = await stockApi.getCybStocks(200)
      setStocks(data)
    } catch (error) {
      message.error('获取创业板列表失败')
    } finally {
      setLoading(false)
    }
  }

  const formatLargeNumber = (num: number | string) => {
    if (!num) return '-'
    const n = typeof num === 'string' ? parseFloat(num) : num
    if (isNaN(n)) return '-'
    if (n >= 100000000) {
      return `${(n / 100000000).toFixed(2)}亿`
    }
    if (n >= 10000) {
      return `${(n / 10000).toFixed(2)}万`
    }
    return n.toLocaleString()
  }

  const columns: ColumnsType<Stock> = [
    {
      title: '代码',
      dataIndex: 'code',
      width: 90,
      fixed: 'left',
      render: (code: string) => (
        <a onClick={() => navigate(`/stock/${code}`)} style={{ color: '#58a6ff' }}>
          {code}
        </a>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      width: 100,
      render: (name: string, record: Stock) => (
        <a onClick={() => navigate(`/stock/${record.code}`)}>{name}</a>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      width: 80,
      sorter: (a, b) => (Number(a.price) || 0) - (Number(b.price) || 0),
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      dataIndex: 'changePercent',
      width: 90,
      sorter: (a, b) => (Number(a.changePercent) || 0) - (Number(b.changePercent) || 0),
      defaultSortOrder: 'descend',
      render: (v: number | string) => {
        if (v === undefined || v === null) return '-'
        const num = typeof v === 'string' ? parseFloat(v) : v
        if (!num && num !== 0) return '-'
        const color = num >= 0 ? '#ef4444' : '#22c55e'
        return <span style={{ color, fontWeight: 500 }}>{(num >= 0 ? '+' : '') + num.toFixed(2)}%</span>
      },
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      width: 100,
      sorter: (a, b) => (Number(a.volume) || 0) - (Number(b.volume) || 0),
      render: (v: number) => {
        if (!v) return '-'
        return v > 10000 ? `${(v / 10000).toFixed(2)}万手` : `${v}手`
      },
    },
    {
      title: '成交额',
      dataIndex: 'turnover',
      width: 100,
      sorter: (a, b) => (Number(a.turnover) || 0) - (Number(b.turnover) || 0),
      render: (v: number | string) => formatLargeNumber(v),
    },
    {
      title: '换手率',
      dataIndex: 'turnoverRate',
      width: 80,
      sorter: (a, b) => (Number(a.turnoverRate) || 0) - (Number(b.turnoverRate) || 0),
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) + '%' : '-'
      },
    },
    {
      title: '市值',
      dataIndex: 'totalMarketValue',
      width: 100,
      sorter: (a, b) => (Number(a.totalMarketValue) || 0) - (Number(b.totalMarketValue) || 0),
      render: (v: number | string) => formatLargeNumber(v),
    },
    {
      title: '市场',
      dataIndex: 'market',
      width: 70,
      render: () => <Tag color="purple">创业板</Tag>,
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '100px 0' }}>
        <Spin size="large" />
      </div>
    )
  }

  return (
    <div>
      <h1 className="page-title">创业板列表</h1>

      <Card className="hover-card">
        <Table
          dataSource={stocks}
          columns={columns}
          rowKey="code"
          scroll={{ x: 900 }}
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          size="small"
          onRow={(record) => ({
            onClick: () => navigate(`/stock/${record.code}`),
            style: { cursor: 'pointer' },
          })}
        />
      </Card>
    </div>
  )
}