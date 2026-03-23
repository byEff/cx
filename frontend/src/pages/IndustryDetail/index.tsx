import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Table, Spin, message, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'

interface Stock {
  code: string
  name: string
  price: number | string
  change_percent: number | string
  volume: number
  turnover: number | string
  market: string
}

export default function IndustryDetail() {
  const { code } = useParams<{ code: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [stocks, setStocks] = useState<Stock[]>([])
  const [industryName, setIndustryName] = useState('')

  useEffect(() => {
    if (code) {
      loadStocks(code)
    }
  }, [code])

  const loadStocks = async (boardCode: string) => {
    setLoading(true)
    try {
      const response = await fetch(`/api/v1/market/industries/${boardCode}/stocks`)
      const data = await response.json()
      setStocks(data || [])
    } catch (error) {
      message.error('获取板块股票失败')
      console.error('Failed to load stocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<Stock> = [
    {
      title: '代码',
      dataIndex: 'code',
      width: 100,
      render: (code: string) => (
        <a onClick={() => navigate(`/stock/${code}`)} style={{ color: '#58a6ff' }}>
          {code}
        </a>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      width: 120,
      render: (name: string, record) => (
        <a onClick={() => navigate(`/stock/${record.code}`)}>{name}</a>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      width: 100,
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      width: 100,
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
      width: 120,
      render: (v: number) => {
        if (!v) return '-'
        return v > 10000 ? `${(v / 10000).toFixed(2)}万手` : `${v}手`
      },
    },
    {
      title: '市场',
      dataIndex: 'market',
      width: 80,
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
      <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/industry')}>
          返回板块列表
        </Button>
        <h1 className="page-title" style={{ margin: 0 }}>
          板块详情: {code}
        </h1>
      </div>

      <Card className="hover-card">
        <Table
          dataSource={stocks}
          columns={columns}
          rowKey="code"
          pagination={{
            pageSize: 50,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 只股票`,
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