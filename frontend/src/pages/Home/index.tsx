import { useEffect, useState } from 'react'
import { Row, Col, Card, Table, Statistic } from 'antd'
import { RiseOutlined, FallOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import type { Stock } from '@/types'
import { marketApi } from '@/services/api'

function Home() {
  const navigate = useNavigate()
  const [indices, setIndices] = useState<Stock[]>([])
  const [topGainers, setTopGainers] = useState<Stock[]>([])
  const [topLosers, setTopLosers] = useState<Stock[]>([])
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

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 90,
      render: (code: string) => (
        <a onClick={() => navigate(`/stock/${code}`)} style={{ color: '#58a6ff' }}>
          {code}
        </a>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 100,
      render: (name: string, record: any) => (
        <a onClick={() => navigate(`/stock/${record.code}`)}>{name}</a>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 80,
      render: (price: number | string) => {
        const numPrice = typeof price === 'string' ? parseFloat(price) : price
        return numPrice ? numPrice.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      key: 'changePercent',
      width: 90,
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
      <h1 className="page-title">市场总览</h1>

      {/* 指数卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        {indices.map((index: any) => {
          const changeNum = typeof index.change_percent === 'string' ? parseFloat(index.change_percent) : index.change_percent || index.changePercent
          const priceNum = typeof index.price === 'string' ? parseFloat(index.price) : index.price
          const isUp = changeNum && changeNum > 0
          
          return (
            <Col span={8} key={index.code}>
              <Card 
                className="hover-card"
                style={{ 
                  background: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)',
                  border: '1px solid #30363d',
                }}
              >
                <div style={{ marginBottom: 8, color: '#8b949e', fontSize: 14 }}>
                  {index.name}
                </div>
                <div style={{ 
                  fontSize: 28, 
                  fontWeight: 700, 
                  color: isUp ? '#ef4444' : '#22c55e',
                  marginBottom: 4,
                }}>
                  {priceNum ? priceNum.toFixed(2) : '-'}
                </div>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 4,
                  color: isUp ? '#ef4444' : '#22c55e',
                  fontSize: 14,
                }}>
                  {isUp ? <RiseOutlined /> : <FallOutlined />}
                  <span>{changeNum ? `${isUp ? '+' : ''}${changeNum.toFixed(2)}%` : '-'}</span>
                </div>
              </Card>
            </Col>
          )
        })}
      </Row>

      {/* 涨跌榜 */}
      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card 
            title={
              <span style={{ color: '#ef4444' }}>
                <RiseOutlined style={{ marginRight: 8 }} />
                涨幅榜
              </span>
            }
            loading={loading}
            className="hover-card"
          >
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
          <Card 
            title={
              <span style={{ color: '#22c55e' }}>
                <FallOutlined style={{ marginRight: 8 }} />
                跌幅榜
              </span>
            }
            loading={loading}
            className="hover-card"
          >
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