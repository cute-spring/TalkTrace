import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Layout, Menu, Typography } from 'antd'
import {
  HistoryOutlined,
  ImportOutlined,
  FileTextOutlined,
  BarChartOutlined,
} from '@ant-design/icons'

const { Header, Sider } = Layout
const { Title } = Typography

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: '历史记录查询',
    },
    {
      key: '/import',
      icon: <ImportOutlined />,
      label: '数据导入',
    },
    {
      key: '/test-cases',
      icon: <FileTextOutlined />,
      label: '测试用例管理',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '统计分析',
    },
  ]

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key)
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={240}
        style={{
          background: '#001529',
        }}
      >
        <div style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: collapsed ? 16 : 18,
          fontWeight: 'bold',
          borderBottom: '1px solid #1f1f1f'
        }}>
          {collapsed ? 'TT' : 'Talk Trace'}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          borderBottom: '1px solid #f0f0f0',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Title level={4} style={{ margin: 0, color: '#262626' }}>
            测试样本管理平台
          </Title>
        </Header>

        {children}
      </Layout>
    </Layout>
  )
}

export default AppLayout