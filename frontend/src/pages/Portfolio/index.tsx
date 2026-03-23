import { useState, useEffect } from 'react'
import {
  Card,
  Row,
  Col,
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Spin,
  message,
  Popconfirm,
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  RiseOutlined,
  FallOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { portfolioApi } from '@/services/api'
import type { PortfolioGroup, Position, ProfitLossSummary } from '@/types'

const { Option } = Select

export default function Portfolio() {
  const [loading, setLoading] = useState(false)
  const [groups, setGroups] = useState<PortfolioGroup[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [profitLoss, setProfitLoss] = useState<ProfitLossSummary | null>(null)
  const [selectedGroup, setSelectedGroup] = useState<number | undefined>(undefined)

  const [groupModalVisible, setGroupModalVisible] = useState(false)
  const [positionModalVisible, setPositionModalVisible] = useState(false)
  const [groupForm] = Form.useForm()
  const [positionForm] = Form.useForm()

  useEffect(() => {
    fetchGroups()
    fetchProfitLoss()
  }, [])

  useEffect(() => {
    fetchPositions(selectedGroup)
    fetchProfitLoss(selectedGroup)
  }, [selectedGroup])

  const fetchGroups = async () => {
    try {
      const data = await portfolioApi.getGroups()
      setGroups(data)
    } catch (error) {
      message.error('获取分组列表失败')
    }
  }

  const fetchPositions = async (groupId?: number) => {
    setLoading(true)
    try {
      const data = await portfolioApi.getPositions(groupId)
      setPositions(data)
    } catch (error) {
      message.error('获取持仓列表失败')
    } finally {
      setLoading(false)
    }
  }

  const fetchProfitLoss = async (groupId?: number) => {
    try {
      const data = await portfolioApi.getProfitLoss(groupId)
      setProfitLoss(data)
    } catch (error) {
      message.error('获取盈亏数据失败')
    }
  }

  const handleCreateGroup = async () => {
    try {
      const values = await groupForm.validateFields()
      await portfolioApi.createGroup(values.name)
      setGroupModalVisible(false)
      groupForm.resetFields()
      fetchGroups()
      message.success('创建成功')
    } catch (error) {
      message.error('创建分组失败')
    }
  }

  const handleDeleteGroup = async (id: number) => {
    try {
      await portfolioApi.deleteGroup(id)
      fetchGroups()
      if (selectedGroup === id) {
        setSelectedGroup(undefined)
      }
      message.success('删除成功')
    } catch (error) {
      message.error('删除分组失败')
    }
  }

  const handleCreatePosition = async () => {
    try {
      const values = await positionForm.validateFields()
      await portfolioApi.createPosition({
        group_id: values.group_id,
        stock_code: values.stock_code,
        stock_name: values.stock_name,
        cost_price: values.cost_price,
        quantity: values.quantity,
      })
      setPositionModalVisible(false)
      positionForm.resetFields()
      fetchPositions(selectedGroup)
      fetchProfitLoss(selectedGroup)
      message.success('添加成功')
    } catch (error) {
      message.error('添加持仓失败')
    }
  }

  const handleDeletePosition = async (id: number) => {
    try {
      await portfolioApi.deletePosition(id)
      fetchPositions(selectedGroup)
      fetchProfitLoss(selectedGroup)
      message.success('删除成功')
    } catch (error) {
      message.error('删除持仓失败')
    }
  }

  const positionColumns: ColumnsType<ProfitLossSummary['positions'][0]> = [
    {
      title: '代码',
      dataIndex: 'stockCode',
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'stockName',
      width: 120,
    },
    {
      title: '持仓量',
      dataIndex: 'quantity',
      width: 100,
      render: (v: number) => `${v}股`,
    },
    {
      title: '成本价',
      dataIndex: 'costPrice',
      width: 100,
      render: (v: number) => v.toFixed(2),
    },
    {
      title: '现价',
      dataIndex: 'currentPrice',
      width: 100,
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '市值',
      dataIndex: 'marketValue',
      width: 120,
      render: (v: number | string) => {
        const num = typeof v === 'string' ? parseFloat(v) : v
        return num ? num.toFixed(2) : '-'
      },
    },
    {
      title: '盈亏',
      dataIndex: 'profitLoss',
      width: 120,
      render: (v: number) => {
        if (v === undefined || v === null) return '-'
        const color = v >= 0 ? '#ef4444' : '#22c55e'
        return <span style={{ color, fontWeight: 500 }}>{v >= 0 ? '+' : ''}{v.toFixed(2)}</span>
      },
    },
    {
      title: '盈亏%',
      dataIndex: 'profitLossPercent',
      width: 100,
      render: (v: number) => {
        if (v === undefined || v === null) return '-'
        const color = v >= 0 ? '#ef4444' : '#22c55e'
        return <span style={{ color, fontWeight: 500 }}>{v >= 0 ? '+' : ''}{v.toFixed(2)}%</span>
      },
    },
    {
      title: '操作',
      width: 80,
      render: (_, record) => (
        <Popconfirm
          title="确定删除该持仓?"
          onConfirm={() => handleDeletePosition(record.positionId)}
        >
          <Button type="link" danger size="small">
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  const isProfit = (profitLoss?.totalProfitLoss || 0) >= 0

  return (
    <div>
      <h1 className="page-title">持仓管理</h1>

      <Card style={{ marginBottom: 16 }} className="hover-card">
        <Row gutter={24}>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">总成本</div>
              <div className="stat-value">¥{(profitLoss?.totalCost || 0).toFixed(2)}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">总市值</div>
              <div className="stat-value">¥{(profitLoss?.totalMarketValue || 0).toFixed(2)}</div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">总盈亏</div>
              <div className="stat-value" style={{ color: isProfit ? '#ef4444' : '#22c55e' }}>
                {isProfit ? <RiseOutlined style={{ marginRight: 8 }} /> : <FallOutlined style={{ marginRight: 8 }} />}
                ¥{(profitLoss?.totalProfitLoss || 0).toFixed(2)}
              </div>
            </div>
          </Col>
          <Col span={6}>
            <div className="stat-card">
              <div className="stat-label">盈亏比例</div>
              <div className="stat-value" style={{ color: isProfit ? '#ef4444' : '#22c55e' }}>
                {(profitLoss?.totalProfitLossPercent || 0).toFixed(2)}%
              </div>
            </div>
          </Col>
        </Row>
      </Card>

      <Row gutter={16}>
        <Col span={6}>
          <Card
            title="分组"
            extra={
              <Button
                type="primary"
                size="small"
                icon={<PlusOutlined />}
                onClick={() => setGroupModalVisible(true)}
              >
                新建
              </Button>
            }
            className="hover-card"
          >
            <div
              style={{
                padding: '12px 16px',
                cursor: 'pointer',
                borderRadius: 8,
                marginBottom: 8,
                background: selectedGroup === undefined ? 'rgba(24, 144, 255, 0.15)' : 'transparent',
                border: selectedGroup === undefined ? '1px solid rgba(24, 144, 255, 0.3)' : '1px solid transparent',
              }}
              onClick={() => setSelectedGroup(undefined)}
            >
              全部持仓
            </div>
            {groups.map((group) => (
              <div
                key={group.id}
                style={{
                  padding: '12px 16px',
                  cursor: 'pointer',
                  borderRadius: 8,
                  marginBottom: 8,
                  background: selectedGroup === group.id ? 'rgba(24, 144, 255, 0.15)' : 'transparent',
                  border: selectedGroup === group.id ? '1px solid rgba(24, 144, 255, 0.3)' : '1px solid transparent',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span onClick={() => setSelectedGroup(group.id)}>
                  {group.name}
                </span>
                <Popconfirm
                  title="确定删除该分组?"
                  onConfirm={() => handleDeleteGroup(group.id)}
                >
                  <DeleteOutlined style={{ color: '#8b949e' }} />
                </Popconfirm>
              </div>
            ))}
          </Card>
        </Col>

        <Col span={18}>
          <Card
            title={`持仓列表 (${profitLoss?.positions?.length || 0})`}
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setPositionModalVisible(true)}
              >
                添加持仓
              </Button>
            }
            className="hover-card"
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '50px 0' }}>
                <Spin size="large" />
              </div>
            ) : (
              <Table
                dataSource={profitLoss?.positions || []}
                columns={positionColumns}
                rowKey="positionId"
                pagination={false}
                size="small"
              />
            )}
          </Card>
        </Col>
      </Row>

      <Modal
        title="创建分组"
        open={groupModalVisible}
        onOk={handleCreateGroup}
        onCancel={() => setGroupModalVisible(false)}
      >
        <Form form={groupForm} layout="vertical">
          <Form.Item
            name="name"
            label="分组名称"
            rules={[{ required: true, message: '请输入分组名称' }]}
          >
            <Input placeholder="请输入分组名称" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="添加持仓"
        open={positionModalVisible}
        onOk={handleCreatePosition}
        onCancel={() => setPositionModalVisible(false)}
      >
        <Form form={positionForm} layout="vertical">
          <Form.Item
            name="group_id"
            label="所属分组"
            rules={[{ required: true, message: '请选择分组' }]}
            initialValue={selectedGroup}
          >
            <Select placeholder="请选择分组">
              {groups.map((group) => (
                <Option key={group.id} value={group.id}>
                  {group.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="stock_code"
            label="股票代码"
            rules={[{ required: true, message: '请输入股票代码' }]}
          >
            <Input placeholder="如: 600519" />
          </Form.Item>
          <Form.Item name="stock_name" label="股票名称">
            <Input placeholder="可选" />
          </Form.Item>
          <Form.Item
            name="cost_price"
            label="成本价"
            rules={[{ required: true, message: '请输入成本价' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={0}
              precision={3}
              placeholder="请输入成本价"
            />
          </Form.Item>
          <Form.Item
            name="quantity"
            label="持仓量（股）"
            rules={[{ required: true, message: '请输入持仓量' }]}
          >
            <InputNumber
              style={{ width: '100%' }}
              min={1}
              precision={0}
              placeholder="请输入持仓量"
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}