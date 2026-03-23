import { useState, useEffect } from 'react'
import { Card, Table, Input, Select, Spin, message, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import { etfApi } from '@/services/api'
import type { ETF } from '@/types'

const { Search } = Input
const { Option } = Select

export default function ETFPage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [etfList, setEtfList] = useState<ETF[]>([])
  const [filteredEtf, setFilteredEtf] = useState<ETF[]>([])
  const [etfType, setEtfType] = useState<string | undefined>(undefined)
  const [searchText, setSearchText] = useState('')

  useEffect(() => {
    fetchEtfList()
  }, [etfType])

  useEffect(() => {
    if (!searchText) {
      setFilteredEtf(etfList)
      return
    }
    const filtered = etfList.filter(
      (etf) =>
        etf.code.includes(searchText) ||
        etf.name.toLowerCase().includes(searchText.toLowerCase())
    )
    setFilteredEtf(filtered)
  }, [searchText, etfList])

  const fetchEtfList = async () => {
    setLoading(true)
    try {
      const data = await etfApi.getEtfList(200, etfType)
      setEtfList(data)
      setFilteredEtf(data)
    } catch (error) {
      message.error('获取ETF列表失败')
    } finally {
      setLoading(false)
    }
  }

  const columns: ColumnsType<ETF> = [
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
      width: 150,
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
        return num ? num.toFixed(3) : '-'
      },
    },
    {
      title: '涨跌幅',
      dataIndex: 'changePercent',
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
        return v > 10000 ? `${(v / 10000).toFixed(2)}万` : v.toString()
      },
    },
    {
      title: '成交额',
      dataIndex: 'turnover',
      width: 120,
      render: (v: number) => {
        if (!v) return '-'
        return v > 100000000
          ? `${(v / 100000000).toFixed(2)}亿`
          : v > 10000
          ? `${(v / 10000).toFixed(2)}万`
          : v.toFixed(2)
      },
    },
    {
      title: '市场',
      dataIndex: 'market',
      width: 80,
      render: (v: string) => (
        <Tag color={v === 'SH' ? 'blue' : 'green'}>{v}</Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'type',
      width: 100,
      ellipsis: true,
    },
  ]

  return (
    <div>
      <h1 className="page-title">ETF列表</h1>

      <Card className="hover-card">
        <div style={{ marginBottom: 16, display: 'flex', gap: 16 }}>
          <Search
            placeholder="搜索代码或名称"
            allowClear
            style={{ width: 300 }}
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Select
            style={{ width: 150 }}
            placeholder="ETF类型"
            allowClear
            value={etfType}
            onChange={setEtfType}
          >
            <Option value="股票型">股票型</Option>
            <Option value="债券型">债券型</Option>
            <Option value="货币型">货币型</Option>
            <Option value="QDII">QDII</Option>
            <Option value="商品型">商品型</Option>
          </Select>
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '50px 0' }}>
            <Spin size="large" />
          </div>
        ) : (
          <Table
            dataSource={filteredEtf}
            columns={columns}
            rowKey="code"
            scroll={{ x: 1000 }}
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
        )}
      </Card>
    </div>
  )
}