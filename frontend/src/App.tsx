import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import { Layout, Menu } from 'antd'
import {
  HomeOutlined,
  SearchOutlined,
  StarOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import Home from './pages/Home'
import StockDetail from './pages/StockDetail'
import Search from './pages/Search'
import Watchlist from './pages/Watchlist'
import Industry from './pages/Industry'

const { Header, Content, Sider } = Layout

function App() {
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/industry',
      icon: <BarChartOutlined />,
      label: '行业板块',
    },
    {
      key: '/search',
      icon: <SearchOutlined />,
      label: '搜索筛选',
    },
    {
      key: '/watchlist',
      icon: <StarOutlined />,
      label: '自选股',
    },
  ]

  return (
    <Layout>
      <Header className="header" style={{ display: 'flex', alignItems: 'center' }}>
        <div className="logo">📈 行情数据</div>
      </Header>
      <Layout>
        <Sider width={200} className="site-layout-background">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => {
              navigate(key)
            }}
          />
        </Sider>
        <Layout style={{ padding: '0' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
            }}
          >
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/industry" element={<Industry />} />
              <Route path="/stock/:code" element={<StockDetail />} />
              <Route path="/search" element={<Search />} />
              <Route path="/watchlist" element={<Watchlist />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  )
}

export default App
