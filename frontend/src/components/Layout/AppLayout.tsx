import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Layout, Menu, Typography } from 'antd'
import {
  HistoryOutlined,
  ImportOutlined,
  FileTextOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import LanguageToggle from '../LanguageToggle'

const { Header, Sider } = Layout
const { Title } = Typography

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { t } = useTranslation()

  const menuItems = [
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: t('menu.history'),
    },
    {
      key: '/import',
      icon: <ImportOutlined />,
      label: t('menu.import'),
    },
    {
      key: '/test-cases',
      icon: <FileTextOutlined />,
      label: t('menu.testCases'),
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: t('menu.analytics'),
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
          display: 'flex',
          flexDirection: 'column',
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
          {collapsed ? 'TT' : t('app.name')}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{
            borderRight: 0,
            flex: 1,
          }}
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
            {t('app.title')}
          </Title>
        </Header>

        {children}
      </Layout>

      {/* Language toggle positioned at absolute bottom-left of the page */}
      <div style={{
        position: 'fixed',
        bottom: 16,
        left: 16,
        zIndex: 1000,
      }}>
        <LanguageToggle collapsed={false} />
      </div>
    </Layout>
  )
}

export default AppLayout