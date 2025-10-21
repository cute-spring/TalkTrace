import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
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
  test_config?: {
    model: {
      name: string
      params?: {
        temperature?: number
        max_tokens?: number
        [key: string]: any
      }
    }
    prompts?: {
      system: string
      user_instruction: string
    }
  }
}

const HistoryPage: React.FC = () => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)

  // Helper function for robust translation with interpolation
  const translateWithValues = (key: string, values: Record<string, number | string> = {}) => {
    try {
      const result = t(key, values)
      // If the result still contains placeholders, do manual replacement
      if (typeof result === 'string' && (result.includes('{{') || result.includes('{'))) {
        let fallback = result
        Object.entries(values).forEach(([placeholder, value]) => {
          // Try both {{}} and {} syntax
          fallback = fallback.replace(new RegExp(`{{${placeholder}}}`, 'g'), String(value))
          fallback = fallback.replace(new RegExp(`{${placeholder}}}`, 'g'), String(value))
        })
        return fallback
      }
      return result
    } catch (error) {
      console.error(`Translation error for key "${key}":`, error)
      return key // Return the key as fallback
    }
  }
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
      message.error(t('common.error'))
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
    // Use search results with complete retrieval chunk information
    Modal.info({
      title: t('history.modal.sessionId'),
      width: 1000,
      okText: t('common.ok'),
      content: (
        <div style={{ marginTop: 16 }}>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.sessionId')}</Text>
            <Text code>{record.session_id}</Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.model')}</Text>
            <Tag color="blue">{record.model_id}</Tag>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.userQuery')}</Text>
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {record.user_query}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.aiResponse')}</Text>
            <div style={{ background: '#f0f7ff', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {record.ai_response}
            </div>
          </div>

          {/* Retrieval chunks section */}
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.retrievalChunks')}</Text>
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
                          <span>{chunk.title || `${t('history.modal.chunk')} ${index + 1}`}</span>
                          <Tag color="green">{t('history.modal.confidence')} {chunk.metadata?.confidence ? (chunk.metadata.confidence * 100).toFixed(1) : 'N/A'}%</Tag>
                        </div>
                      }
                    >
                      <div style={{ marginBottom: 8 }}>
                        <Text type="secondary">{t('history.modal.source')}</Text>
                        <a href={chunk.source} target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>
                          {chunk.source || t('history.modal.unknownSource')}
                        </a>
                      </div>
                      <div style={{ marginBottom: 8 }}>
                        <Text type="secondary">{t('history.modal.content')}</Text>
                        <div style={{ background: '#fafafa', padding: 8, borderRadius: 4, marginTop: 4, maxHeight: 120, overflowY: 'auto' }}>
                          {chunk.content}
                        </div>
                      </div>
                      {chunk.metadata && (
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          <Space wrap>
                            <span>{t('history.modal.published')} {chunk.metadata.publish_date || 'N/A'}</span>
                            <span>{t('history.modal.effective')} {chunk.metadata.effective_date || 'N/A'}</span>
                            <span>{t('history.modal.expired')} {chunk.metadata.expiration_date || 'N/A'}</span>
                            <Tag color="orange">{chunk.metadata.chunk_type || t('history.modal.unclassified')}</Tag>
                            <span>{t('history.modal.rank')} #{chunk.metadata.retrieval_rank || index + 1}</span>
                          </Space>
                        </div>
                      )}
                    </Card>
                  ))}
                </div>
              ) : (
                <Text type="secondary">{t('history.modal.noChunks')}</Text>
              )}
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.userRating')}</Text>
            <Rate disabled value={record.user_rating} style={{ marginLeft: 8 }} />
          </div>
          <div>
            <Text strong>{t('history.modal.createdAt')}</Text>
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

          {/* Test Configuration Section */}
          {record.test_config && (
            <div style={{ marginTop: 24, padding: 16, backgroundColor: '#f8f9fa', borderRadius: 6 }}>
              <Title level={5} style={{ margin: '0 0 16px 0', color: '#1890ff' }}>
                {t('history.modal.testConfig.title')}
              </Title>

              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Card size="small" title={t('history.modal.testConfig.modelConfig')}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{t('history.modal.testConfig.modelName')}：</Text>
                        <Text>{record.test_config.model?.name || record.model_id || 'N/A'}</Text>
                      </div>
                      {record.test_config.model?.params && (
                        <div>
                          <Text strong>{t('history.modal.testConfig.parameters')}：</Text>
                          <pre style={{ fontSize: '12px', marginTop: 4, padding: 8, backgroundColor: '#fff', border: '1px solid #d9d9d9', borderRadius: 4 }}>
                            {JSON.stringify(record.test_config.model.params, null, 2)}
                          </pre>
                        </div>
                      )}
                    </Space>
                  </Card>
                </Col>

                <Col span={12}>
                  <Card size="small" title={t('history.modal.testConfig.promptConfig')}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        <Text strong>{t('history.modal.testConfig.systemPrompt')}：</Text>
                        <div style={{
                          marginTop: 4,
                          padding: 8,
                          backgroundColor: '#fff',
                          border: '1px solid #d9d9d9',
                          borderRadius: 4,
                          maxHeight: 120,
                          overflowY: 'auto',
                          fontSize: '12px'
                        }}>
                          <Text code>{record.test_config.prompts?.system || 'N/A'}</Text>
                        </div>
                      </div>
                      <div>
                        <Text strong>{t('history.modal.testConfig.userInstruction')}：</Text>
                        <div style={{
                          marginTop: 4,
                          padding: 8,
                          backgroundColor: '#fff',
                          border: '1px solid #d9d9d9',
                          borderRadius: 4,
                          maxHeight: 120,
                          overflowY: 'auto',
                          fontSize: '12px'
                        }}>
                          <Text code>{record.test_config.prompts?.user_instruction || 'N/A'}</Text>
                        </div>
                      </div>
                    </Space>
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </div>
      ),
    })
  }

  const columns: ColumnsType<HistoryRecord> = [
    {
      title: t('history.columns.sessionId'),
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
      title: t('history.columns.userQuery'),
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
      title: t('history.columns.aiResponse'),
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
      title: t('history.columns.model'),
      dataIndex: 'model_id',
      key: 'model_id',
      width: 150,
      render: (text, record) => {
        const modelName = record.test_config?.model?.name || text
        return <Tag color="blue">{modelName}</Tag>
      },
    },
    {
      title: t('history.columns.rating'),
      dataIndex: 'user_rating',
      key: 'user_rating',
      width: 120,
      render: (rating) => (
        <Rate disabled value={rating} style={{ fontSize: 14 }} />
      ),
    },
    {
      title: t('history.columns.timestamp'),
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
      title: t('common.actions'),
      key: 'actions',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => handleViewDetails(record)}
        >
          {t('common.view')}
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
        <Title level={3} className="page-title">{t('history.title')}</Title>
        <Text className="page-description">
          Query and filter historical conversation records from BigQuery, select session data to import
        </Text>
      </Card>

      <Card className="search-form">
        <Space wrap size="middle">
          <div>
            <Text strong>{t('history.dateRange')}：</Text>
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
            <Text strong>{t('history.model')}：</Text>
            <Select
              mode="multiple"
              placeholder={modelsLoading ? t('common.loading') : t('history.selectModel')}
              style={{ width: 200, marginLeft: 8 }}
              value={filters.modelIds}
              onChange={(values) => setFilters(prev => ({ ...prev, modelIds: values }))}
              loading={modelsLoading}
              options={Array.isArray(models) ? models.map(model => ({ label: model, value: model })) : []}
            />
          </div>

          <div>
            <Text strong>{t('history.rating')}：</Text>
            <Select
              placeholder={t('history.selectRatingRange')}
              style={{ width: 150, marginLeft: 8 }}
              value={filters.ratingRange || undefined}
              onChange={(value) => setFilters(prev => ({ ...prev, ratingRange: value }))}
              options={[
                { label: t('common.all'), value: undefined },
                { label: t('history.rating1-2'), value: [1, 2] },
                { label: t('history.rating3-4'), value: [3, 4] },
                { label: t('history.rating5'), value: [5, 5] },
              ]}
            />
          </div>

          <div>
            <Input
              placeholder={t('history.searchPlaceholder')}
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
            {t('history.search')}
          </Button>

          <Button
            icon={<ReloadOutlined />}
            onClick={fetchHistory}
          >
            {t('history.reset')}
          </Button>
        </Space>

        {selectedRowKeys.length > 0 && (
          <div style={{ marginTop: 16, padding: 12, background: '#f6ffed', borderRadius: 4 }}>
            <Text strong>{translateWithValues('history.selectedRecords', { count: selectedRowKeys.length })}</Text>
            <Button
              type="primary"
              size="small"
              style={{ marginLeft: 16 }}
              onClick={() => {
                // 这里可以跳转到导入页面，并传递选中的会话ID
                window.location.href = `/import?sessionIds=${selectedRowKeys.join(',')}`
              }}
            >
              {t('history.importSelected')}
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
              translateWithValues('history.pagination', { start: range[0], end: range[1], total: total }),
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