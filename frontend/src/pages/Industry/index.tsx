import { useEffect, useState } from 'react'
import { Card, Table, Select, Space, Tag, Input, Button } from 'antd'
import { RiseOutlined, FallOutlined, ReloadOutlined } from '@ant-design/icons'
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table'
import type { SorterResult } from 'antd/es/table/interface'

interface Industry {
  code: string
  name: string
  price: number
  change_percent: number
  volume: number
  turnover: number
  change_5d: number
  change_ytd: number
  change_1m: number
  stock_count: number
  lead_stock: string
}

interface IndustryResponse {
  data: Industry[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

function IndustryPage() {
  const [industries, setIndustries] = useState<Industry[]>([])
  const [loading, setLoading] = useState(false)
  const [sortBy, setSortBy] = useState<string>('change_percent')
  const [order, setOrder] = useState<string>('desc')
  const [searchText, setSearchText] = useState('')
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0,
  })

  useEffect(() => {
    loadIndustries()
  }, [pagination.current, pagination.pageSize, sortBy, order])

  const loadIndustries = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `http://localhost:8001/api/v1/market/industries?page=${pagination.current}&page_size=${pagination.pageSize}&sort_by=${sortBy}&order=${order}`
      )
      const result: IndustryResponse = await response.json()
      setIndustries(result.data)
      setPagination(prev => ({
        ...prev,
        total: result.total,
      }))
    } catch (error) {
      console.error('Failed to load industries:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTableChange = (
    pagination: TablePaginationConfig,
    filters: any,
    sorter: any
  ) => {
    setPagination(prev => ({
      ...prev,
      current: pagination.current || 1,
      pageSize: pagination.pageSize || 50,
    }))
  }

  const formatNumber = (num: number, decimals: number = 2) => {
    if (!num) return '-'
    return num.toLocaleString('zh-CN', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    })
  }

  const formatLargeNumber = (num: number) => {
    if (!num) return '-'
    if (num >= 100000000) {
      return `${(num / 100000000).toFixed(2)}亿`
    }
    if (num >= 10000) {
      return `${(num / 10000).toFixed(2)}万`
    }
    return num.toLocaleString()
  }

  const columns: ColumnsType<Industry> = [
    {
      title: '行业代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
      fixed: 'left',
    },
    {
      title: '行业名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      fixed: 'left',
      render: (name: string, record: Industry) => (
        <div>
          <div style={{ fontWeight: 500 }}>{name}</div>
          <div style={{ fontSize: 12, color: '#999' }}>龙头：{record.lead_stock}</div>
        </div>
      ),
    },
    {
      title: '当前价',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => formatNumber(price),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      width: 100,
      sorter: true,
      sortOrder: sortBy === 'change_percent' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (change: number) => (
        <span className={change > 0 ? 'stock-up' : change < 0 ? 'stock-down' : 'stock-flat'}>
          {change > 0 ? <RiseOutlined /> : change < 0 ? <FallOutlined /> : null}
          {formatNumber(Math.abs(change))}%
        </span>
      ),
    },
    {
      title: '5 日涨幅',
      dataIndex: 'change_5d',
      key: 'change_5d',
      width: 100,
      sorter: true,
      sortOrder: sortBy === 'change_5d' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (change: number) => (
        <span className={change > 0 ? 'stock-up' : change < 0 ? 'stock-down' : 'stock-flat'}>
          {formatNumber(Math.abs(change))}%
        </span>
      ),
    },
    {
      title: '本月涨幅',
      dataIndex: 'change_1m',
      key: 'change_1m',
      width: 100,
      sorter: true,
      sortOrder: sortBy === 'change_1m' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (change: number) => (
        <span className={change > 0 ? 'stock-up' : change < 0 ? 'stock-down' : 'stock-flat'}>
          {formatNumber(Math.abs(change))}%
        </span>
      ),
    },
    {
      title: '今年涨幅',
      dataIndex: 'change_ytd',
      key: 'change_ytd',
      width: 100,
      sorter: true,
      sortOrder: sortBy === 'change_ytd' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (change: number) => (
        <span className={change > 0 ? 'stock-up' : change < 0 ? 'stock-down' : 'stock-flat'}>
          {formatNumber(Math.abs(change))}%
        </span>
      ),
    },
    {
      title: '成交量 (手)',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      sorter: true,
      sortOrder: sortBy === 'volume' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (volume: number) => formatLargeNumber(volume),
    },
    {
      title: '成交额 (元)',
      dataIndex: 'turnover',
      key: 'turnover',
      width: 120,
      sorter: true,
      sortOrder: sortBy === 'turnover' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (turnover: number) => formatLargeNumber(turnover),
    },
    {
      title: '股票数量',
      dataIndex: 'stock_count',
      key: 'stock_count',
      width: 100,
      sorter: true,
      sortOrder: sortBy === 'stock_count' ? (order === 'desc' ? 'descend' : 'ascend') : null,
      render: (count: number) => (
        <Tag color="blue">{count}只</Tag>
      ),
    },
  ]

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Space style={{ marginBottom: 16, flexWrap: 'wrap' }}>
          <span style={{ fontWeight: 500 }}>排序：</span>
          <Select
            value={sortBy}
            onChange={setSortBy}
            style={{ width: 120 }}
            options={[
              { value: 'change_percent', label: '涨跌幅' },
              { value: 'change_5d', label: '5 日涨幅' },
              { value: 'change_ytd', label: '今年涨幅' },
              { value: 'turnover', label: '成交额' },
              { value: 'volume', label: '成交量' },
              { value: 'stock_count', label: '股票数量' },
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
            placeholder="搜索行业名称或代码"
            style={{ width: 250 }}
            allowClear
            onSearch={setSearchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <Button icon={<ReloadOutlined />} onClick={loadIndustries}>
            刷新
          </Button>
        </Space>
        <div style={{ color: '#666', fontSize: 14 }}>
          共 {pagination.total} 个行业，第 {pagination.current} 页 / 共 {Math.ceil(pagination.total / pagination.pageSize)} 页
        </div>
      </Card>

      <Card title="行业板块">
        <Table
          columns={columns}
          dataSource={industries.filter(
            (item) =>
              item.name.toLowerCase().includes(searchText.toLowerCase()) ||
              item.code.toLowerCase().includes(searchText.toLowerCase()) ||
              item.lead_stock.toLowerCase().includes(searchText.toLowerCase())
          )}
          rowKey="code"
          loading={loading}
          onChange={handleTableChange}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            pageSizeOptions: ['20', '50', '100', '200'],
            showTotal: (total) => `共 ${total} 条`,
          }}
          scroll={{ x: 1400, y: 600 }}
          size="middle"
          sticky
        />
      </Card>
    </div>
  )
}

export default IndustryPage
