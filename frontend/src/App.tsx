import { useState, useEffect } from 'react'
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu, Input, ConfigProvider, theme } from 'antd'
import {
  HomeOutlined,
  SearchOutlined,
  StarOutlined,
  BarChartOutlined,
  StockOutlined,
  FundOutlined,
  FilterOutlined,
  WalletOutlined,
  DashboardOutlined,
  UserOutlined,
  RiseOutlined,
} from '@ant-design/icons'
import Home from './pages/Home'
import StockDetail from './pages/StockDetail'
import Search from './pages/Search'
import Watchlist from './pages/Watchlist'
import Industry from './pages/Industry'
import IndustryDetail from './pages/IndustryDetail'
import MarketSentiment from './pages/MarketSentiment'
import ETF from './pages/ETF'
import AdvancedFilter from './pages/AdvancedFilter'
import Portfolio from './pages/Portfolio'
import Cyb from './pages/Cyb'

const { Header, Content, Sider } = Layout
const { Search: SearchInput } = Input

const MENU_CONFIG = {
  market: {
    label: '市场总览',
    icon: <DashboardOutlined />,
    children: [
      { key: '/', label: '首页', icon: <HomeOutlined /> },
      { key: '/sentiment', label: '市场情绪', icon: <BarChartOutlined /> },
    ],
  },
  filter: {
    label: '筛选中心',
    icon: <FilterOutlined />,
    children: [
      { key: '/search', label: '搜索筛选', icon: <SearchOutlined /> },
      { key: '/filter', label: '高级筛选', icon: <FilterOutlined /> },
      { key: '/etf', label: 'ETF', icon: <FundOutlined /> },
      { key: '/cyb', label: '创业板', icon: <RiseOutlined /> },
    ],
  },
  industry: {
    label: '行业板块',
    icon: <StockOutlined />,
    children: [
      { key: '/industry', label: '行业板块', icon: <StockOutlined /> },
    ],
  },
  personal: {
    label: '个人中心',
    icon: <UserOutlined />,
    children: [
      { key: '/watchlist', label: '自选股', icon: <StarOutlined /> },
      { key: '/portfolio', label: '持仓管理', icon: <WalletOutlined /> },
    ],
  },
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const [activeModule, setActiveModule] = useState<string>('market')

  useEffect(() => {
    const pathToModule: Record<string, string> = {
      '/': 'market',
      '/sentiment': 'market',
      '/search': 'filter',
      '/filter': 'filter',
      '/etf': 'filter',
      '/cyb': 'filter',
      '/industry': 'industry',
      '/watchlist': 'personal',
      '/portfolio': 'personal',
    }
    const currentPath = location.pathname.startsWith('/stock') ? '/' : location.pathname
    const module = pathToModule[currentPath] || 'market'
    setActiveModule(module)
  }, [location.pathname])

  const handleModuleChange = (moduleKey: string) => {
    setActiveModule(moduleKey)
    const firstRoute = MENU_CONFIG[moduleKey as keyof typeof MENU_CONFIG].children[0].key
    navigate(firstRoute)
  }

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?keyword=${encodeURIComponent(value.trim())}`)
    }
  }

  const topMenuItems = Object.entries(MENU_CONFIG).map(([key, config]) => ({
    key,
    icon: config.icon,
    label: config.label,
  }))

  const sideMenuItems = MENU_CONFIG[activeModule as keyof typeof MENU_CONFIG]?.children || []

  return (
    <ConfigProvider
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
          colorBgContainer: '#1f1f1f',
          colorBgElevated: '#262626',
        },
        components: {
          Menu: {
            darkItemBg: '#1f1f1f',
            darkItemSelectedBg: '#1890ff20',
          },
          Card: {
            colorBgContainer: '#1f1f1f',
          },
          Table: {
            headerBg: '#262626',
            rowHoverBg: '#262626',
          },
        },
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        <Header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            background: '#141414',
            borderBottom: '1px solid #303030',
            padding: '0 24px',
            height: 64,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
            <div
              style={{
                fontSize: 20,
                fontWeight: 'bold',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              📈 行情数据
            </div>
            <Menu
              mode="horizontal"
              selectedKeys={[activeModule]}
              items={topMenuItems}
              onClick={({ key }) => handleModuleChange(key)}
              style={{
                background: 'transparent',
                borderBottom: 'none',
                flex: 1,
                minWidth: 400,
              }}
              theme="dark"
            />
          </div>

          <SearchInput
            placeholder="搜索股票代码或名称"
            allowClear
            onSearch={handleSearch}
            style={{ width: 280 }}
          />
        </Header>

        <Layout>
          <Sider
            width={200}
            style={{
              background: '#141414',
              borderRight: '1px solid #303030',
            }}
            theme="dark"
          >
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={sideMenuItems}
              onClick={({ key }) => navigate(key)}
              style={{
                height: '100%',
                borderRight: 0,
                background: 'transparent',
              }}
            />
          </Sider>
          <Layout
            style={{
              background: '#0d1117',
              padding: 0,
            }}
          >
            <Content
              style={{
                padding: 24,
                margin: 0,
                minHeight: 280,
                background: '#0d1117',
              }}
            >
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/sentiment" element={<MarketSentiment />} />
                <Route path="/etf" element={<ETF />} />
                <Route path="/filter" element={<AdvancedFilter />} />
                <Route path="/cyb" element={<Cyb />} />
                <Route path="/industry" element={<Industry />} />
                <Route path="/industry/:code" element={<IndustryDetail />} />
                <Route path="/portfolio" element={<Portfolio />} />
                <Route path="/stock/:code" element={<StockDetail />} />
                <Route path="/search" element={<Search />} />
                <Route path="/watchlist" element={<Watchlist />} />
              </Routes>
            </Content>
          </Layout>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}

export default App