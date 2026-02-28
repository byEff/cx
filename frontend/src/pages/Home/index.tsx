import { useEffect, useState } from 'react'
import { Row, Col, Card, Table, Input, Statistic } from 'antd'
import { SearchOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { Stock } from '@/types'
import { marketApi } from '@/services/api'

const { Search } = Input

function Home() {
  const navigate = useNavigate()
  const [indices, setIndices] = useState<Stock[]>([])
  const [topGainers, setTopGainers] = useState<Stock[]>([])
  const [topLosers, setTopLosers] = useState<Stock[]>([])
  const [searchKeyword, setSearchKeyword] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [indicesData, gainersData, losersData] = await Promise.all([
        marketApi.getMarketIndices(),
        marketApi.getTopGainers(10),
        marketApi.getTopLosers(10),
      ])
      setIndices(indicesData)
      setTopGainers(gainersData)
      setTopLosers(losersData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?keyword=${encodeURIComponent(value.trim())}`)
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
      render: (name: string, record: any) => <a onClick={() => navigate(`/stock/${record.code}`)}>{name}</a>,
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
      key: 'changePercent',
      width: 100,
      render: (_: any, record: any) => {
        const change = record.change_percent || record.changePercent
        const numChange = typeof change === 'string' ? parseFloat(change) : change
        if (!numChange && numChange !== 0) return '-'
        return (
          <span className={numChange > 0 ? 'stock-up' : numChange < 0 ? 'stock-down' : 'stock-flat'}>
            {numChange > 0 ? '+' : ''}{numChange.toFixed(2)}%
          </span>
        )
      },
    },
  ]

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Search
          placeholder="输入股票代码或名称搜索"
          enterButton="搜索"
          size="large"
          value={searchKeyword}
          onChange={(e) => setSearchKeyword(e.target.value)}
          onSearch={handleSearch}
          prefix={<SearchOutlined />}
        />
      </Card>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {indices.map((index: any) => {
          const changeNum = typeof index.change_percent === 'string' ? parseFloat(index.change_percent) : index.change_percent || index.changePercent
          const priceNum = typeof index.price === 'string' ? parseFloat(index.price) : index.price
          return (
            <Col span={8} key={index.code}>
              <Card>
                <Statistic
                  title={index.name}
                  value={priceNum || 0}
                  precision={2}
                  valueStyle={{
                    color: changeNum && changeNum > 0 ? '#f5222d' : '#52c41a'
                  }}
                  prefix={changeNum && changeNum > 0 ? <RiseOutlined /> : <FallOutlined />}
                  suffix={changeNum ? `(${changeNum > 0 ? '+' : ''}${changeNum.toFixed(2)}%)` : ''}
                />
              </Card>
            </Col>
          )
        })}
      </Row>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card title="📈 涨幅榜" loading={loading}>
            <Table
              dataSource={topGainers.map((item: any) => ({
                ...item,
                change_percent: item.change_percent || item.changePercent,
              }))}
              columns={columns}
              rowKey="code"
              pagination={false}
              size="small"
              onRow={(record: any) => ({
                onClick: () => navigate(`/stock/${record.code}`),
                style: { cursor: 'pointer' }
              })}
            />
          </Card>
        </Col>

        <Col span={12}>
          <Card title="📉 跌幅榜" loading={loading}>
            <Table
              dataSource={topLosers.map((item: any) => ({
                ...item,
                change_percent: item.change_percent || item.changePercent,
              }))}
              columns={columns}
              rowKey="code"
              pagination={false}
              size="small"
              onRow={(record: any) => ({
                onClick: () => navigate(`/stock/${record.code}`),
                style: { cursor: 'pointer' }
              })}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
