import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  DatePicker,
  Select,
  Rate,
  message,
  Modal,
  Typography,
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import type { ColumnsType } from 'antd/es/table'
import { historyService } from '../services/api'

const { RangePicker } = DatePicker
const { Title, Text } = Typography

interface HistoryRecord {
  session_id: string
  user_query: string
  ai_response: string
  user_rating: number
  model_id: string
  created_at: string
  retrieval_chunks: any[]
}

const HistoryPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [filters, setFilters] = useState({
    startTime: dayjs().subtract(7, 'days').toISOString(),
    endTime: dayjs().toISOString(),
    modelIds: [] as string[],
    ratingRange: null as [number, number] | null,
    keywords: '',
    page: 1,
    pageSize: 20,
  })

  const [models, setModels] = useState<string[]>([])
  const [modelsLoading, setModelsLoading] = useState(true)

  // 获取可用模型列表
  useEffect(() => {
    const fetchModels = async () => {
      setModelsLoading(true)
      try {
        const response = await historyService.getModels()
        // 确保返回的数据是数组
        if (Array.isArray(response.data)) {
          setModels(response.data)
        } else {
          console.warn('Models API returned non-array data:', response.data)
          setModels(['gpt-4o-mini', 'gpt-4o', 'claude-3-sonnet'])
        }
      } catch (error) {
        console.error('Failed to fetch models:', error)
        // 设置默认模型列表以确保UI正常工作
        setModels(['gpt-4o-mini', 'gpt-4o', 'claude-3-sonnet'])
      } finally {
        setModelsLoading(false)
      }
    }
    fetchModels()
  }, [])

  // 获取历史记录
  const fetchHistory = async () => {
    setLoading(true)
    try {
      const response = await historyService.search(filters)
      setData(response.data)
    } catch (error) {
      message.error('获取历史记录失败')
      console.error('Failed to fetch history:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [filters.page, filters.pageSize])

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 1 }))
    fetchHistory()
  }

  const handleDateRangeChange = (dates: any) => {
    if (dates && dates.length === 2) {
      setFilters(prev => ({
        ...prev,
        startTime: dates[0].toISOString(),
        endTime: dates[1].toISOString(),
      }))
    }
  }

  const handleViewDetails = (record: HistoryRecord) => {
    Modal.info({
      title: '会话详情',
      width: 800,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <Text strong>会话ID：</Text>
            <Text>{record.session_id}</Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>模型：</Text>
            <Tag>{record.model_id}</Tag>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>用户问题：</Text>
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {record.user_query}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>AI回答：</Text>
            <div style={{ background: '#f0f7ff', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {record.ai_response}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>用户评分：</Text>
            <Rate disabled value={record.user_rating} style={{ marginLeft: 8 }} />
          </div>
          <div>
            <Text strong>创建时间：</Text>
            <Text>{dayjs(record.created_at).format('YYYY-MM-DD HH:mm:ss')}</Text>
          </div>
        </div>
      ),
    })
  }

  const columns: ColumnsType<HistoryRecord> = [
    {
      title: '会话ID',
      dataIndex: 'session_id',
      key: 'session_id',
      width: 200,
      render: (text) => (
        <Text code style={{ fontSize: 12 }}>
          {text}
        </Text>
      ),
    },
    {
      title: '用户问题',
      dataIndex: 'user_query',
      key: 'user_query',
      ellipsis: true,
      render: (text) => (
        <div className="text-truncate-2" title={text}>
          {text}
        </div>
      ),
    },
    {
      title: 'AI回答',
      dataIndex: 'ai_response',
      key: 'ai_response',
      ellipsis: true,
      render: (text) => (
        <div className="text-truncate-2" title={text}>
          {text}
        </div>
      ),
    },
    {
      title: '模型',
      dataIndex: 'model_id',
      key: 'model_id',
      width: 150,
      render: (text) => <Tag>{text}</Tag>,
    },
    {
      title: '评分',
      dataIndex: 'user_rating',
      key: 'user_rating',
      width: 120,
      render: (rating) => (
        <Rate disabled value={rating} style={{ fontSize: 14 }} />
      ),
    },
    {
      title: '时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm:ss'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleViewDetails(record)}
        >
          查看详情
        </Button>
      ),
    },
  ]

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys as string[])
    },
  }

  return (
    <div>
      <Card className="page-header">
        <Title level={3} className="page-title">历史记录查询</Title>
        <Text className="page-description">
          从BigQuery中查询和筛选历史对话记录，选择需要导入的会话数据
        </Text>
      </Card>

      <Card className="search-form">
        <Space wrap size="middle">
          <div>
            <Text strong>时间范围：</Text>
            <RangePicker
              showTime
              defaultValue={[
                dayjs().subtract(7, 'days'),
                dayjs(),
              ]}
              onChange={handleDateRangeChange}
              style={{ width: 350, marginLeft: 8 }}
            />
          </div>

          <div>
            <Text strong>模型：</Text>
            <Select
              mode="multiple"
              placeholder={modelsLoading ? "加载模型..." : "选择模型"}
              style={{ width: 200, marginLeft: 8 }}
              value={filters.modelIds}
              onChange={(values) => setFilters(prev => ({ ...prev, modelIds: values }))}
              loading={modelsLoading}
              options={Array.isArray(models) ? models.map(model => ({ label: model, value: model })) : []}
            />
          </div>

          <div>
            <Text strong>评分范围：</Text>
            <Select
              placeholder="选择评分范围"
              style={{ width: 150, marginLeft: 8 }}
              value={filters.ratingRange}
              onChange={(value) => setFilters(prev => ({ ...prev, ratingRange: value }))}
              options={[
                { label: '全部', value: null },
                { label: '1-2星', value: [1, 2] },
                { label: '3-4星', value: [3, 4] },
                { label: '5星', value: [5, 5] },
              ]}
            />
          </div>

          <div>
            <Input
              placeholder="关键词搜索"
              style={{ width: 200 }}
              value={filters.keywords}
              onChange={(e) => setFilters(prev => ({ ...prev, keywords: e.target.value }))}
            />
          </div>

          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
          >
            搜索
          </Button>

          <Button
            icon={<ReloadOutlined />}
            onClick={fetchHistory}
          >
            刷新
          </Button>
        </Space>

        {selectedRowKeys.length > 0 && (
          <div style={{ marginTop: 16, padding: 12, background: '#f6ffed', borderRadius: 4 }}>
            <Text strong>已选择 {selectedRowKeys.length} 条记录</Text>
            <Button
              type="primary"
              size="small"
              style={{ marginLeft: 16 }}
              onClick={() => {
                // 这里可以跳转到导入页面，并传递选中的会话ID
                window.location.href = `/import?sessionIds=${selectedRowKeys.join(',')}`
              }}
            >
              导入选中记录
            </Button>
          </div>
        )}
      </Card>

      <Card className="content-card">
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="session_id"
          loading={loading}
          rowSelection={rowSelection}
          pagination={{
            current: data?.page,
            pageSize: data?.pageSize,
            total: data?.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: (page, pageSize) => {
              setFilters(prev => ({ ...prev, page, pageSize: pageSize || 20 }))
            },
          }}
        />
      </Card>
    </div>
  )
}

export default HistoryPage