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
  const [pagination, setPagination] = useState<any>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [filters, setFilters] = useState({
    startTime: dayjs('2024-01-01').startOf('day').toISOString(), // Use a date that includes demo data
    endTime: dayjs().endOf('day').toISOString(),
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
        const modelsData = response.data
        if (Array.isArray(modelsData)) {
          setModels(modelsData)
        } else if (modelsData && typeof modelsData === 'object' && Array.isArray(modelsData.data)) {
          // 处理嵌套的数据结构
          setModels(modelsData.data)
        } else {
          console.warn('Models API returned unexpected data structure:', response.data)
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

      // The actual data is in response.data.data.items (API has extra data wrapper)
      const actualData = response.data.data?.items || response.data.items || []
      const paginationData = response.data.data || response.data
      setData(actualData)
      setPagination(paginationData)
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
    // 直接使用搜索结果中的完整数据，因为搜索API已经返回了完整的检索片段信息
    Modal.info({
      title: '会话详情',
      width: 1000,
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <Text strong>会话ID：</Text>
            <Text code>{record.session_id}</Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>模型：</Text>
            <Tag color="blue">{record.model_id}</Tag>
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

          {/* 检索片段部分 */}
          <div style={{ marginBottom: 16 }}>
            <Text strong>检索片段：</Text>
            <div style={{ marginTop: 8 }}>
              {record.retrieval_chunks && record.retrieval_chunks.length > 0 ? (
                <div>
                  {record.retrieval_chunks.map((chunk: any, index: number) => (
                    <Card
                      key={chunk.id || index}
                      size="small"
                      style={{ marginBottom: 8 }}
                      title={
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span>{chunk.title || `片段 ${index + 1}`}</span>
                          <Tag color="green">置信度: {chunk.metadata?.confidence ? (chunk.metadata.confidence * 100).toFixed(1) : 'N/A'}%</Tag>
                        </div>
                      }
                    >
                      <div style={{ marginBottom: 8 }}>
                        <Text type="secondary">来源：</Text>
                        <a href={chunk.source} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>
                          {chunk.source || '未知来源'}
                        </a>
                      </div>
                      <div style={{ marginBottom: 8 }}>
                        <Text type="secondary">内容：</Text>
                        <div style={{ background: '#fafafa', padding: 8, borderRadius: 4, marginTop: 4, maxHeight: 120, overflowY: 'auto' }}>
                          {chunk.content}
                        </div>
                      </div>
                      {chunk.metadata && (
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          <Space wrap>
                            <span>发布: {chunk.metadata.publish_date || 'N/A'}</span>
                            <span>生效: {chunk.metadata.effective_date || 'N/A'}</span>
                            <span>过期: {chunk.metadata.expiration_date || 'N/A'}</span>
                            <Tag color="orange">{chunk.metadata.chunk_type || '未分类'}</Tag>
                            <span>排序: #{chunk.metadata.retrieval_rank || index + 1}</span>
                          </Space>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              ) : (
                <Text type="secondary">暂无检索片段信息</Text>
              )}
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <Text strong>用户评分：</Text>
            <Rate disabled value={record.user_rating} style={{ marginLeft: 8 }} />
          </div>
          <div>
            <Text strong>创建时间：</Text>
            <Text>
              {(() => {
                try {
                  // Handle various date formats
                  if (!record.created_at) return 'N/A'
                  // Normalize date format
                  const normalizedDate = record.created_at.replace('+00:00Z', 'Z')
                  const parsed = dayjs(normalizedDate)
                  return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm:ss') : record.created_at
                } catch (error) {
                  return record.created_at || 'Invalid Date'
                }
              })()}
            </Text>
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
      render: (text) => {
        try {
          // Handle date format with both +00:00 and Z by normalizing it
          const normalizedDate = text ? text.replace('+00:00Z', 'Z') : text
          const parsed = dayjs(normalizedDate)
          if (parsed.isValid()) {
            return parsed.format('YYYY-MM-DD HH:mm:ss')
          } else {
            return text || 'Invalid Date'
          }
        } catch (error) {
          return text || 'Invalid Date'
        }
      },
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
              value={filters.ratingRange || undefined}
              onChange={(value) => setFilters(prev => ({ ...prev, ratingRange: value }))}
              options={[
                { label: '全部', value: undefined },
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
          dataSource={data || []}
          rowKey="session_id"
          loading={loading}
          rowSelection={rowSelection}
          pagination={{
            current: pagination?.page,
            pageSize: pagination?.page_size || 20,
            total: pagination?.total,
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