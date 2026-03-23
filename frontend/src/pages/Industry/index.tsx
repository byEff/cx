import { useEffect, useState } from 'react'
import { Card, Table, Select, Space, Input, Button } from 'antd'
import { RiseOutlined, FallOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'

interface Industry {
  code: string
  name: string
  price: number | string
  change_percent: number | string
  volume: number
  turnover: number | string
  change_5d?: number | string
  change_ytd?: number | string
  change_1m?: number | string
  stock_count?: number | string
  lead_stock?: string
}

function IndustryPage() {
  const navigate = useNavigate()
  const [industries, setIndustries] = useState<Industry[]>([])
  const [loading, setLoading] = useState(false)
  const [sortBy, setSortBy] = useState<string>('change_percent')
  const [order, setOrder] = useState<string>('desc')
  const [searchText, setSearchText] = useState('')

  useEffect(() => {
    loadIndustries()
  }, [sortBy, order])

  const loadIndustries = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `/api/v1/market/industries?page=1&page_size=2000&sort_by=${sortBy}&order=${order}`
      )
      const result = await response.json()
      setIndustries(result.data || [])
    } catch (error) {
      console.error('Failed to load industries:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num: number | string, decimals: number = 2) => {
    if (!num) return '-'
    const n = typeof num === 'string' ? parseFloat(num) : num
    if (isNaN(n)) return '-'
    return n.toLocaleString('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
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

  const columns: ColumnsType<Industry> = [
    {
      title: '板块代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      fixed: 'left',
      render: (code: string) => (
        <a onClick={() => navigate(`/industry/${code}`)} style={{ color: '#58a6ff' }}>
          {code}
        </a>
      ),
    },
    {
      title: '板块名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      fixed: 'left',
      render: (name: string, record: Industry) => (
        <a onClick={() => navigate(`/industry/${record.code}`)}>{name}</a>
      ),
    },
    {
      title: '板块指数',
      dataIndex: 'price',
      key: 'price',
      width: 110,
      render: (price: number | string) => formatNumber(price),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      width: 100,
      sorter: true,
      render: (change: number | string) => {
        const num = typeof change === 'string' ? parseFloat(change) : change
        if (isNaN(num) || (!num && num !== 0)) return '-'
        const color = num >= 0 ? '#ef4444' : '#22c55e'
        return (
          <span style={{ color, fontWeight: 500 }}>
            {num >= 0 ? <RiseOutlined /> : <FallOutlined />} {Math.abs(num).toFixed(2)}%
          </span>
        )
      },
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      sorter: true,
      render: (volume: number) => {
        if (!volume) return '-'
        return formatLargeNumber(volume) + '手'
      },
    },
    {
      title: '成交额',
      dataIndex: 'turnover',
      key: 'turnover',
      width: 120,
      sorter: true,
      render: (turnover: number | string) => formatLargeNumber(turnover) + '元',
    },
  ]

  const filteredIndustries = industries.filter(
    (item) =>
      item.name.toLowerCase().includes(searchText.toLowerCase()) ||
      item.code.toLowerCase().includes(searchText.toLowerCase())
  )

  return (
    <div>
      <h1 className="page-title">行业板块</h1>

      <Card style={{ marginBottom: 24 }} className="hover-card">
        <Space style={{ marginBottom: 16, flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 500, color: '#f0f6fc' }}>排序：</span>
          <Select
            value={sortBy}
            onChange={setSortBy}
            style={{ width: 120 }}
            options={[
              { value: 'change_percent', label: '涨跌幅' },
              { value: 'turnover', label: '成交额' },
              { value: 'volume', label: '成交量' },
            ]}
          />
          <Select
            value={order}
            onChange={setOrder}
            style={{ width: 100 }}
            options={[
              { value: 'desc', label: '降序' },
              { value: 'asc', label: '升序' },
            ]}
          />
          <Input.Search
            placeholder="搜索板块名称或代码"
            style={{ width: 250 }}
            allowClear
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Button type="primary" icon={<ReloadOutlined />} onClick={loadIndustries}>
            刷新
          </Button>
        </Space>
        <div style={{ color: '#8b949e', fontSize: 14 }}>
          共 {filteredIndustries.length} 个板块
        </div>
      </Card>

      <Card className="hover-card">
        <Table
          columns={columns}
          dataSource={filteredIndustries}
          rowKey="code"
          loading={loading}
          pagination={false}
          scroll={{ x: 800, y: 600 }}
          size="middle"
          sticky
          onRow={(record) => ({
            onClick: () => navigate(`/industry/${record.code}`),
            style: { cursor: 'pointer' },
          })}
        />
      </Card>
    </div>
  )
}

export default IndustryPage