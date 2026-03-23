import { useState, useEffect } from 'react'
import { Card, Row, Col, Table, Spin, message } from 'antd'
import { Pie } from '@ant-design/plots'
import { marketApi } from '@/services/api'
import type { UpDownDistribution, LimitUpStats, Stock } from '@/types'

export default function MarketSentiment() {
  const [loading, setLoading] = useState(false)
  const [distribution, setDistribution] = useState<UpDownDistribution | null>(null)
  const [limitUpStats, setLimitUpStats] = useState<LimitUpStats | null>(null)
  const [hotStocks, setHotStocks] = useState<Stock[]>([])

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    setLoading(true)
    try {
      const [dist, stats, hot] = await Promise.all([
        marketApi.getUpDownDistribution(),
        marketApi.getLimitUpStats(),
        marketApi.getHotStocks(20),
      ])
      setDistribution(dist)
      setLimitUpStats(stats)
      setHotStocks(hot)
    } catch (error) {
      message.error('获取市场情绪数据失败')
    } finally {
      setLoading(false)
    }
  }

  const pieData = distribution
    ? [
        { type: '上涨', value: distribution.upCount },
        { type: '下跌', value: distribution.downCount },
        { type: '平盘', value: distribution.flatCount },
      ]
    : []

  const total = pieData.reduce((sum, item) => sum + item.value, 0)

  const pieConfig = {
    appendPadding: 10,
    data: pieData,
    angleField: 'value',
    colorField: 'type',
    radius: 0.8,
    innerRadius: 0.6,
    color: ['#ef4444', '#22c55e', '#6b7280'],
    label: {
      text: 'type',
      position: 'outside',
      formatter: (datum: any) => {
        const percent = total > 0 ? ((datum.value / total) * 100).toFixed(1) : 0
        return `${datum.type} ${percent}%`
      },
    },
    legend: {
      color: {
        position: 'bottom',
      },
    },
  }

  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      width: 90,
      render: (code: string) => (
        <a onClick={() => window.location.href = `/stock/${code}`} style={{ color: '#58a6ff' }}>
          {code}
        </a>
      ),
    },
    {
      title: '名称',
      dataIndex: 'name',
      width: 100,
    },
    {
      title: '价格',
      dataIndex: 'price',
      width: 80,
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '涨跌幅',
      dataIndex: 'changePercent',
      width: 90,
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
      render: (v: number) => {
        if (!v) return '-'
        return v > 10000 ? `${(v / 10000).toFixed(2)}万手` : `${v}手`
      },
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
      <h1 className="page-title">市场情绪</h1>

      <Row gutter={[16, 16]}>
        {/* 涨跌分布 */}
        <Col span={12}>
          <Card title="涨跌分布" className="hover-card">
            {distribution && (
              <>
                <Pie {...pieConfig} />
                <Row style={{ marginTop: 24, textAlign: 'center' }}>
                  <Col span={6}>
                    <div className="stat-card" style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
                      <div className="stat-value stat-up">{distribution.upCount}</div>
                      <div className="stat-label">上涨</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="stat-card" style={{ background: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                      <div className="stat-value stat-down">{distribution.downCount}</div>
                      <div className="stat-label">下跌</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="stat-card" style={{ background: 'rgba(245, 158, 11, 0.1)', border: '1px solid rgba(245, 158, 11, 0.3)' }}>
                      <div className="stat-value stat-warning">{distribution.limitUp}</div>
                      <div className="stat-label">涨停</div>
                    </div>
                  </Col>
                  <Col span={6}>
                    <div className="stat-card" style={{ background: 'rgba(14, 165, 233, 0.1)', border: '1px solid rgba(14, 165, 233, 0.3)' }}>
                      <div className="stat-value" style={{ color: '#0ea5e9' }}>{distribution.limitDown}</div>
                      <div className="stat-label">跌停</div>
                    </div>
                  </Col>
                </Row>
              </>
            )}
          </Card>
        </Col>

        {/* 涨停统计 */}
        <Col span={12}>
          <Card title="涨停统计" className="hover-card">
            {limitUpStats && (
              <Row gutter={16}>
                <Col span={8}>
                  <div className="stat-card" style={{ background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(239, 68, 68, 0.05) 100%)' }}>
                    <div className="stat-value stat-up">{limitUpStats.totalCount}</div>
                    <div className="stat-label">涨停家数</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="stat-card" style={{ background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(34, 197, 94, 0.05) 100%)' }}>
                    <div className="stat-value stat-down">{limitUpStats.sealCount}</div>
                    <div className="stat-label">封板家数</div>
                  </div>
                </Col>
                <Col span={8}>
                  <div className="stat-card" style={{ background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(245, 158, 11, 0.05) 100%)' }}>
                    <div className="stat-value stat-warning">{limitUpStats.openCount}</div>
                    <div className="stat-label">开板家数</div>
                  </div>
                </Col>
              </Row>
            )}
          </Card>
        </Col>

        {/* 热门股票 */}
        <Col span={24}>
          <Card title="热门股票" className="hover-card">
            <Table
              dataSource={hotStocks}
              columns={columns}
              rowKey="code"
              pagination={false}
              size="small"
              onRow={(record) => ({
                onClick: () => window.location.href = `/stock/${record.code}`,
                style: { cursor: 'pointer' },
              })}
            />
          </Card>
        </Col>
      </Row>
    </div>
  )
}