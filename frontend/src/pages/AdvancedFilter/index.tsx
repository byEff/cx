import { useState, useEffect } from 'react'
import { Card, Tabs, Table, Spin, message, Tag } from 'antd'
import type { ColumnsType, TableProps } from 'antd/es/table'
import { useNavigate } from 'react-router-dom'
import { stockApi } from '@/services/api'
import type { Stock } from '@/types'

export default function AdvancedFilter() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState<Record<string, boolean>>({
    limitUp: false,
    limitDown: false,
    newStocks: false,
    kcb: false,
  })
  const [limitUpStocks, setLimitUpStocks] = useState<Stock[]>([])
  const [limitDownStocks, setLimitDownStocks] = useState<Stock[]>([])
  const [newStocks, setNewStocks] = useState<Stock[]>([])
  const [kcbStocks, setKcbStocks] = useState<Stock[]>([])

  useEffect(() => {
    fetchLimitUpStocks()
  }, [])

  const fetchLimitUpStocks = async () => {
    setLoading((prev) => ({ ...prev, limitUp: true }))
    try {
      const data = await stockApi.getLimitUpStocks(100)
      setLimitUpStocks(data)
    } catch (error) {
      message.error('获取涨停板列表失败')
    } finally {
      setLoading((prev) => ({ ...prev, limitUp: false }))
    }
  }

  const fetchLimitDownStocks = async () => {
    setLoading((prev) => ({ ...prev, limitDown: true }))
    try {
      const data = await stockApi.getLimitDownStocks(100)
      setLimitDownStocks(data)
    } catch (error) {
      message.error('获取跌停板列表失败')
    } finally {
      setLoading((prev) => ({ ...prev, limitDown: false }))
    }
  }

  const fetchNewStocks = async () => {
    setLoading((prev) => ({ ...prev, newStocks: true }))
    try {
      const data = await stockApi.getNewStocks(100)
      setNewStocks(data)
    } catch (error) {
      message.error('获取次新股列表失败')
    } finally {
      setLoading((prev) => ({ ...prev, newStocks: false }))
    }
  }

  const fetchKcbStocks = async () => {
    setLoading((prev) => ({ ...prev, kcb: true }))
    try {
      const data = await stockApi.getKcbStocks(100)
      setKcbStocks(data)
    } catch (error) {
      message.error('获取科创板列表失败')
    } finally {
      setLoading((prev) => ({ ...prev, kcb: false }))
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
      render: (name: string, record) => (
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
      render: (v: number | string) => formatLargeNumber(v) + '元',
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
      render: (v: string) => (
        <Tag color={v === 'SH' ? 'blue' : 'green'}>{v}</Tag>
      ),
    },
  ]

  const renderTable = (data: Stock[], isLoading: boolean) => {
    if (isLoading) {
      return (
        <div style={{ textAlign: 'center', padding: '50px 0' }}>
          <Spin size="large" />
        </div>
      )
    }
    return (
      <Table
        dataSource={data}
        columns={columns}
        rowKey="code"
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `共 ${total} 条`,
        }}
        size="small"
        scroll={{ x: 900 }}
        onRow={(record) => ({
          onClick: () => navigate(`/stock/${record.code}`),
          style: { cursor: 'pointer' },
        })}
      />
    )
  }

  const items = [
    {
      key: 'limitUp',
      label: `涨停板 (${limitUpStocks.length})`,
      children: renderTable(limitUpStocks, loading.limitUp),
    },
    {
      key: 'limitDown',
      label: `跌停板 (${limitDownStocks.length})`,
      children: renderTable(limitDownStocks, loading.limitDown),
    },
    {
      key: 'newStocks',
      label: `次新股 (${newStocks.length})`,
      children: renderTable(newStocks, loading.newStocks),
    },
    {
      key: 'kcb',
      label: `科创板 (${kcbStocks.length})`,
      children: renderTable(kcbStocks, loading.kcb),
    },
  ]

  const handleTabChange = (key: string) => {
    switch (key) {
      case 'limitUp':
        if (limitUpStocks.length === 0) fetchLimitUpStocks()
        break
      case 'limitDown':
        if (limitDownStocks.length === 0) fetchLimitDownStocks()
        break
      case 'newStocks':
        if (newStocks.length === 0) fetchNewStocks()
        break
      case 'kcb':
        if (kcbStocks.length === 0) fetchKcbStocks()
        break
    }
  }

  return (
    <div>
      <h1 className="page-title">高级筛选</h1>

      <Card className="hover-card">
        <Tabs items={items} onChange={handleTabChange} />
      </Card>
    </div>
  )
}