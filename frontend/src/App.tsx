import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout/AppLayout'
import HistoryPage from './pages/HistoryPage'
import ImportPage from './pages/ImportPage'
import TestCasePage from './pages/TestCasePage'

const { Content } = Layout

function App() {
  return (
    <AppLayout>
      <Content style={{ margin: '24px 16px', padding: 24, background: '#fff', borderRadius: 6 }}>
        <Routes>
          <Route path="/" element={<HistoryPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/import" element={<ImportPage />} />
          <Route path="/test-cases" element={<TestCasePage />} />
          <Route path="/file-text" element={<TestCasePage />} />
        </Routes>
      </Content>
    </AppLayout>
  )
}

export default App