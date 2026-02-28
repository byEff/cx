import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Card, Input, Select, Table, Row, Col, Button, message } from 'antd'
import { SearchOutlined } from '@ant-design/icons'
import type { Stock } from '@/types'
import { stockApi, watchlistApi } from '@/services/api'

const { Search } = Input
const { Option } = Select

function SearchPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [stocks, setStocks] = useState<Stock[]>([])
  const [loading, setLoading] = useState(false)
  const [keyword, setKeyword] = useState(searchParams.get('keyword') || '')
  const [industry, setIndustry] = useState<string>()
  const [minChange, setMinChange] = useState<number>()
  const [maxChange, setMaxChange] = useState<number>()

  useEffect(() => {
    const keywordParam = searchParams.get('keyword')
    if (keywordParam) {
      setKeyword(keywordParam)
      handleSearch(keywordParam)
    }
  }, [searchParams])

  const handleSearch = async (value?: string) => {
    const searchValue = value || keyword
    if (!searchValue.trim()) {
      message.warning('请输入搜索关键词')
      return
    }

    setLoading(true)
    try {
      const results = await stockApi.searchStocks(searchValue)
      setStocks(results)
    } catch (error) {
      message.error('搜索失败')
      console.error('Search failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilter = async () => {
    setLoading(true)
    try {
      const results = await stockApi.filterStocks({
        industry,
        minChange,
        maxChange,
        limit: 50,
      })
      setStocks(results)
    } catch (error) {
      message.error('筛选失败')
      console.error('Filter failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleAddToWatchlist = async (stockCode: string) => {
    try {
      await watchlistApi.addToWatchlist(stockCode)
      message.success('已添加到自选股')
    } catch (error) {
      message.error('添加失败')
      console.error('Add to watchlist failed:', error)
    }
  }

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      render: (code: string) => <a onClick={() => navigate(`/stock/${code}`)}>{code}</a>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
      render: (name: string, record: Stock) => <a onClick={() => navigate(`/stock/${record.code}`)}>{name}</a>,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number | string) => {
        const numPrice = typeof price === 'string' ? parseFloat(price) : price
        return numPrice ? numPrice.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      dataIndex: 'changePercent',
      key: 'changePercent',
      width: 100,
      render: (change: number | string) => {
        const numChange = typeof change === 'string' ? parseFloat(change) : change
        if (!numChange) return '-'
        return (
          <span className={numChange > 0 ? 'stock-up' : numChange < 0 ? 'stock-down' : 'stock-flat'}>
            {numChange > 0 ? '+' : ''}{numChange.toFixed(2)}%
          </span>
        )
      },
    },
    {
      title: '行业',
      dataIndex: 'industry',
      key: 'industry',
      width: 120,
    },
    {
      title: '市场',
      dataIndex: 'market',
      key: 'market',
      width: 100,
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_: any, record: Stock) => (
        <Button.Group>
          <Button type="link" onClick={() => navigate(`/stock/${record.code}`)}>
            详情
          </Button>
          <Button type="link" onClick={() => handleAddToWatchlist(record.code)}>
            自选
          </Button>
        </Button.Group>
      ),
    },
  ]

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Search
              placeholder="输入股票代码或名称搜索"
              enterButton="搜索"
              size="large"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              onSearch={handleSearch}
              prefix={<SearchOutlined />}
            />
          </Col>
        </Row>
      </Card>

      <Card title="筛选条件" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col span={6}>
            <Select
              placeholder="选择行业"
              value={industry}
              onChange={setIndustry}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value="电子">电子</Option>
              <Option value="计算机">计算机</Option>
              <Option value="医药生物">医药生物</Option>
              <Option value="化工">化工</Option>
              <Option value="机械设备">机械设备</Option>
            </Select>
          </Col>
          <Col span={6}>
            <Input
              placeholder="最小涨跌幅(%)"
              type="number"
              value={minChange}
              onChange={(e) => setMinChange(Number(e.target.value))}
            />
          </Col>
          <Col span={6}>
            <Input
              placeholder="最大涨跌幅(%)"
              type="number"
              value={maxChange}
              onChange={(e) => setMaxChange(Number(e.target.value))}
            />
          </Col>
          <Col span={6}>
            <Button type="primary" onClick={handleFilter}>
              筛选
            </Button>
          </Col>
        </Row>
      </Card>

      <Card title="搜索结果">
        <Table
          dataSource={stocks}
          columns={columns}
          rowKey="code"
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

export default SearchPage
