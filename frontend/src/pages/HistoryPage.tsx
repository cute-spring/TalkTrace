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
  Row,
  Col,
} from 'antd'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons'
import dayjs from 'dayjs'
import type { ColumnsType } from 'antd/es/table'
import { historyService, testCaseService } from '../services/api'

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
      system: {
        version: string
        content: string
      }
      user_instruction: {
        role: string
        version: string
        content: string
      }
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
  const [expandedRowKeys, setExpandedRowKeys] = useState<string[]>([])

  // Helper to safely render prompt values that may be strings or objects
  const resolvePromptContent = (prompt: any): string => {
    if (!prompt) return 'N/A'
    if (typeof prompt === 'string') return prompt
    if (typeof prompt?.content === 'string') return prompt.content
    try {
      return JSON.stringify(prompt, null, 2)
    } catch {
      return String(prompt)
    }
  }

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
      // Map frontend filters to backend expected query params (camelCase)
      const apiParams = {
        page: filters.page,
        pageSize: filters.pageSize,
        startTime: filters.startTime,
        endTime: filters.endTime,
        keywords: filters.keywords || undefined,
        modelIds: Array.isArray(filters.modelIds) && filters.modelIds.length > 0 ? filters.modelIds : undefined,
        ratingRange: filters.ratingRange
          ? `${filters.ratingRange[0]},${filters.ratingRange[1]}`
          : undefined,
      }

      const response = await historyService.search(apiParams)

      // Normalize API payload shape to avoid type errors
      const raw: any = response?.data
      const payload: any = raw?.data ?? raw
      const items: any[] = Array.isArray(payload?.items)
        ? payload.items
        : Array.isArray(payload?.data?.items)
        ? payload.data.items
        : Array.isArray(payload)
        ? payload
        : []
      const paginationData: any = payload?.page !== undefined || payload?.total !== undefined
        ? payload
        : payload?.data ?? {}
      setData(items)
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

  const handleViewDetails = async (record: HistoryRecord) => {
    // Fetch session details and linked test case by source_session
    let sessionDetail: any = null
    let sessionDetailsList: any[] = []
    let linkedCase: any = null
    try {
      const [detailsResp, mappingResp] = await Promise.all([
        historyService.getSessionDetails(record.session_id),
        testCaseService.getBySourceSession(record.session_id),
      ])

      const detailsRaw: any = detailsResp?.data
      const detailsPayload: any = detailsRaw?.data ?? detailsRaw
      sessionDetail = Array.isArray(detailsPayload) ? (detailsPayload[0] || null) : detailsPayload || null
      sessionDetailsList = Array.isArray(detailsPayload)
        ? detailsPayload.filter(Boolean)
        : (detailsPayload ? [detailsPayload] : [])

      const mappingRaw: any = mappingResp?.data
      linkedCase = mappingRaw?.data ?? null
    } catch (e) {
      console.warn('Failed to load additional session/test case details:', e)
    }

    // Use resolved details if available, otherwise fallback to row record
    const conversation_history = (sessionDetailsList || []).flatMap((d: any, idx: number) => {
      const entries: any[] = []
      if (d?.user_query) entries.push({ role: 'user', content: d.user_query, timestamp: d.created_at, turn: idx + 1 })
      if (d?.ai_response) entries.push({ role: 'assistant', content: d.ai_response, timestamp: d.created_at, turn: idx + 1 })
      return entries
    })
    const display = {
      session_id: sessionDetail?.session_id || record.session_id,
      model_id: sessionDetail?.model_id || record.model_id,
      user_query: sessionDetail?.user_query || record.user_query,
      ai_response: sessionDetail?.ai_response || record.ai_response,
      retrieval_chunks: sessionDetail?.retrieval_chunks || record.retrieval_chunks,
      user_rating: record.user_rating,
      created_at: sessionDetail?.created_at || record.created_at,
      test_config: sessionDetail?.test_config || record.test_config,
      conversation_history,
    }

    // Show details modal
    Modal.info({
      title: t('history.modal.sessionId'),
      width: 1000,
      okText: t('common.ok'),
      content: (
        <div style={{ marginTop: 16 }}>
          {/* Linked Test Case Section */}
          <div style={{ marginBottom: 16 }}>
            <Title level={5} style={{ margin: 0 }}>{t('history.modal.linkedTestCase') || 'Linked Test Case'}</Title>
            <div style={{ marginTop: 8 }}>
              {linkedCase && linkedCase.id ? (
                <Space wrap>
                  <Text strong>ID：</Text>
                  <Text code>{linkedCase.id}</Text>
                  <Text strong style={{ marginLeft: 12 }}>Name：</Text>
                  <Text>{linkedCase.name}</Text>
                  <Text strong style={{ marginLeft: 12 }}>Owner：</Text>
                  <Text>{linkedCase.owner || 'unknown'}</Text>
                  <Text strong style={{ marginLeft: 12 }}>Created：</Text>
                  <Text>
                    {(() => {
                      try {
                        const normalized = (linkedCase.created_date || '').replace('+00:00Z', 'Z')
                        const parsed = dayjs(normalized)
                        return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm:ss') : (linkedCase.created_date || 'N/A')
                      } catch {
                        return linkedCase.created_date || 'N/A'
                      }
                    })()}
                  </Text>
                </Space>
              ) : (
                <Text type="secondary">{t('history.modal.noLinkedTestCase') || 'No linked test case found'}</Text>
              )}
            </div>
          </div>

          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.sessionId')}</Text>
            <Text code>{display.session_id}</Text>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.model')}</Text>
            <Tag color="blue">{display.model_id}</Tag>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.userQuery')}</Text>
            <div style={{ background: '#f5f5f5', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {display.user_query}
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.aiResponse')}</Text>
            <div style={{ background: '#f0f7ff', padding: 12, borderRadius: 4, marginTop: 8 }}>
              {display.ai_response}
            </div>
          </div>

          {/* Conversation History section */}
          <div style={{ marginBottom: 16 }}>
            <Title level={5} style={{ margin: 0 }}>{t('conversationHistory.title')}</Title>
            <div style={{ marginTop: 8 }}>
              {Array.isArray(display.conversation_history) && display.conversation_history.length > 0 ? (
                <div>
                  {display.conversation_history.map((msg: any, i: number) => (
                    <Card key={`conv-${i}`} size="small" style={{ marginBottom: 8 }}>
                      <Space style={{ marginBottom: 4 }}>
                        <Tag color={msg.role === 'user' ? 'geekblue' : (msg.role === 'assistant' ? 'green' : 'default')}>
                          {msg.role === 'user' ? t('conversationHistory.user') : (msg.role === 'assistant' ? t('conversationHistory.assistant') : (msg.role || 'system'))}
                        </Tag>
                        <Text type="secondary">
                          {(() => {
                            try {
                              const normalized = (msg.timestamp || '').replace('+00:00Z', 'Z')
                              const parsed = dayjs(normalized)
                              return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm:ss') : (msg.timestamp || '')
                            } catch {
                              return msg.timestamp || ''
                            }
                          })()}
                        </Text>
                      </Space>
                      <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                    </Card>
                  ))}
                </div>
              ) : (
                <Text type="secondary">{t('history.noData')}</Text>
              )}
            </div>
          </div>

          {/* Retrieval chunks section */}
          <div style={{ marginBottom: 16 }}>
            <Text strong>{t('history.modal.retrievalChunks')}</Text>
            <div style={{ marginTop: 8 }}>
              {display.retrieval_chunks && display.retrieval_chunks.length > 0 ? (
                <div>
                  {display.retrieval_chunks.map((chunk: any, index: number) => (
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
            <Rate disabled value={display.user_rating} style={{ marginLeft: 8 }} />
          </div>
          <div>
            <Text strong>{t('history.modal.createdAt')}</Text>
            <Text>
              {(() => {
                try {
                  // Handle various date formats
                  if (!display.created_at) return 'N/A'
                  // Normalize date format
                  const normalizedDate = display.created_at.replace('+00:00Z', 'Z')
                  const parsed = dayjs(normalizedDate)
                  return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm:ss') : display.created_at
                } catch (error) {
                  return display.created_at || 'Invalid Date'
                }
              })()}
            </Text>
          </div>

          {/* Test Configuration Section */}
          {display.test_config && (
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
                        <Text>{display.test_config?.model?.name || display.model_id || 'N/A'}</Text>
                      </div>
                      {display.test_config?.model?.params && (
                        <div>
                          <Text strong>{t('history.modal.testConfig.parameters')}：</Text>
                          <pre style={{ fontSize: '12px', marginTop: 4, padding: 8, backgroundColor: '#fff', border: '1px solid #d9d9d9', borderRadius: 4 }}>
                            {JSON.stringify(display.test_config?.model?.params, null, 2)}
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
                        {display.test_config?.prompts?.system?.version && (
                          <Tag color="green" style={{ marginLeft: 8, fontSize: '11px' }}>
                            {display.test_config?.prompts?.system?.version}
                          </Tag>
                        )}
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
                          <Text code>
                            {resolvePromptContent(display.test_config?.prompts?.system)}
                          </Text>
                        </div>
                      </div>
                      <div>
                        <Text strong>{t('history.modal.testConfig.userInstruction')}：</Text>
                        {display.test_config?.prompts?.user_instruction?.role && (
                          <Tag color="orange" style={{ marginLeft: 8, fontSize: '11px' }}>
                            {display.test_config?.prompts?.user_instruction?.role}
                          </Tag>
                        )}
                        {display.test_config?.prompts?.user_instruction?.version && (
                          <Tag color="blue" style={{ marginLeft: 4, fontSize: '11px' }}>
                            {display.test_config?.prompts?.user_instruction?.version}
                          </Tag>
                        )}
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
                          <Text code>
                            {resolvePromptContent(display.test_config?.prompts?.user_instruction)}
                          </Text>
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

  // Create Test Case from a history record, including all non-analysis fields
  const handleCreateTestCase = async (record: HistoryRecord) => {
    try {
      // Enrich with session details to capture conversation_history and full test_config
      const detailsResp = await historyService.getSessionDetails(record.session_id)
      const detailsRaw: any = detailsResp?.data
      const detailsPayload: any = detailsRaw?.data ?? detailsRaw
      const sessionDetail: any = Array.isArray(detailsPayload) ? (detailsPayload[0] || null) : detailsPayload || {}

      // Merge record and details with preference to detailed fields
      const merged: any = {
        session_id: sessionDetail?.session_id || record.session_id,
        model_id: sessionDetail?.model_id || record.model_id,
        user_query: sessionDetail?.user_query || record.user_query,
        ai_response: sessionDetail?.ai_response || record.ai_response,
        retrieval_chunks: sessionDetail?.retrieval_chunks || record.retrieval_chunks || [],
        user_rating: record.user_rating,
        created_at: sessionDetail?.created_at || record.created_at,
        conversation_history: sessionDetail?.conversation_history || [],
        test_config: sessionDetail?.test_config || record.test_config,
      }

      // Build payload excluding any analysis fields
      const payload: any = {
        // Basic identity
        name: typeof merged.user_query === 'string' && merged.user_query.trim()
          ? merged.user_query.trim().slice(0, 80)
          : `Session ${merged.session_id}`,
        description: typeof merged.ai_response === 'string' ? merged.ai_response : '',
        status: 'active',

        // Metadata
        metadata: {
          source_session: merged.session_id,
          created_date: merged.created_at,
        },

        // Test configuration
        test_config: merged.test_config ? {
          model: merged.test_config?.model ? {
            name: merged.test_config.model?.name,
            params: merged.test_config.model?.params,
          } : undefined,
          prompts: merged.test_config?.prompts ? {
            system: merged.test_config.prompts?.system ? {
              version: merged.test_config.prompts.system?.version,
              content: merged.test_config.prompts.system?.content,
            } : undefined,
            user_instruction: merged.test_config.prompts?.user_instruction ? {
              role: merged.test_config.prompts.user_instruction?.role,
              version: merged.test_config.prompts.user_instruction?.version,
              content: merged.test_config.prompts.user_instruction?.content,
            } : undefined,
          } : undefined,
        } : undefined,

        // Input
        input: {
          current_query: merged.user_query,
          conversation_history: Array.isArray(merged.conversation_history) ? merged.conversation_history : [],
          current_retrieved_chunks: Array.isArray(merged.retrieval_chunks) ? merged.retrieval_chunks : [],
        },

        // Execution
        execution: {
          actual: merged.ai_response,
          user_feedback: typeof merged.user_rating === 'number' ? { rating: merged.user_rating } : undefined,
        },
      }

      const resp = await testCaseService.create(payload)
      if (resp?.data?.success) {
        message.success(t('testCases.createSuccess') || 'Test case created')
      } else {
        message.warning(t('testCases.createMaybeFailed') || 'Creation response did not indicate success')
      }
    } catch (error) {
      console.error('Failed to create test case from history:', error)
      message.error(t('common.error'))
    }
  }

  // Inline expanded row renderer to show session details
  const renderExpandedRow = (record: HistoryRecord) => (
    <div style={{ background: '#fafafa', padding: 16 }}>
      <div style={{ marginBottom: 12 }}>
        <Text strong>{t('history.modal.sessionId')}</Text>
        <Text code style={{ marginLeft: 8 }}>{record.session_id}</Text>
      </div>
      <div style={{ marginBottom: 12 }}>
        <Text strong>{t('history.modal.model')}</Text>
        <Tag color="blue" style={{ marginLeft: 8 }}>{record.model_id}</Tag>
      </div>

      <Row gutter={[16, 16]}>
        <Col span={12}>
          <Card size="small" title={t('history.modal.userQuery')}>
            <div style={{ background: '#f5f5f5', padding: 8, borderRadius: 4 }}>
              {record.user_query}
            </div>
          </Card>
        </Col>
        <Col span={12}>
          <Card size="small" title={t('history.modal.aiResponse')}>
            <div style={{ background: '#f0f7ff', padding: 8, borderRadius: 4 }}>
              {record.ai_response}
            </div>
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 16 }}>
        <Text strong>{t('history.modal.userRating')}</Text>
        <Rate disabled value={record.user_rating} style={{ marginLeft: 8 }} />
      </div>
      <div style={{ marginTop: 8 }}>
        <Text strong>{t('history.modal.createdAt')}</Text>{' '}
        <Text>
          {(() => {
            try {
              if (!record.created_at) return 'N/A'
              const normalizedDate = record.created_at.replace('+00:00Z', 'Z')
              const parsed = dayjs(normalizedDate)
              return parsed.isValid() ? parsed.format('YYYY-MM-DD HH:mm:ss') : record.created_at
            } catch (error) {
              return record.created_at || 'Invalid Date'
            }
          })()}
        </Text>
      </div>

      {/* Retrieval chunks section */}
      <div style={{ marginTop: 16 }}>
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
                    <div style={{ background: '#fff', padding: 8, borderRadius: 4, marginTop: 4, maxHeight: 120, overflowY: 'auto' }}>
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

      {/* Test Configuration Section */}
      {record.test_config && (
        <div style={{ marginTop: 16, padding: 12, backgroundColor: '#f8f9fa', borderRadius: 6 }}>
          <Title level={5} style={{ margin: '0 0 12px 0', color: '#1890ff' }}>
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
                      <Text strong>{t('history.modal.testConfig.parameters')}</Text>
                      <div style={{ marginTop: 4, padding: 8, backgroundColor: '#fff', border: '1px solid #d9d9d9', borderRadius: 4, maxHeight: 120, overflowY: 'auto', fontSize: '12px' }}>
                        <Text code>
                          {JSON.stringify(record.test_config.model.params)}
                        </Text>
                      </div>
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
                    <div style={{ marginTop: 4, padding: 8, backgroundColor: '#fff', border: '1px solid #d9d9d9', borderRadius: 4, maxHeight: 120, overflowY: 'auto', fontSize: '12px' }}>
                      <Text code>
                        {resolvePromptContent(record.test_config?.prompts?.system)}
                      </Text>
                    </div>
                  </div>
                  <div>
                    <Text strong>{t('history.modal.testConfig.userInstruction')}：</Text>
                    {record.test_config?.prompts?.user_instruction?.role && (
                      <Tag color="orange" style={{ marginLeft: 8, fontSize: '11px' }}>
                        {record.test_config.prompts.user_instruction.role}
                      </Tag>
                    )}
                    {record.test_config?.prompts?.user_instruction?.version && (
                      <Tag color="blue" style={{ marginLeft: 4, fontSize: '11px' }}>
                        {record.test_config.prompts.user_instruction.version}
                      </Tag>
                    )}
                    <div style={{ marginTop: 4, padding: 8, backgroundColor: '#fff', border: '1px solid #d9d9d9', borderRadius: 4, maxHeight: 120, overflowY: 'auto', fontSize: '12px' }}>
                      <Text code>
                        {resolvePromptContent(record.test_config?.prompts?.user_instruction)}
                      </Text>
                    </div>
                  </div>
                </Space>
              </Card>
            </Col>
          </Row>
        </div>
      )}
    </div>
  )

  const handleExpand = (expanded: boolean, record: HistoryRecord) => {
    setExpandedRowKeys(expanded ? [record.session_id] : [])
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
      width: 220,
      render: (text, record) => {
        const modelName = record.test_config?.model?.name || text
        const sysVersion = record.test_config?.prompts?.system?.version
        const userRole = record.test_config?.prompts?.user_instruction?.role
        const userVersion = record.test_config?.prompts?.user_instruction?.version

        if (sysVersion && userRole && userVersion) {
          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
              <Tag color="blue">{modelName}</Tag>
              <div style={{ fontSize: '11px', color: '#666', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                Sys: {sysVersion}, {userRole}: {userVersion}
              </div>
            </div>
          )
        }
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
        <Space>
          <Button
            type="link"
            size="small"
            onClick={() => handleViewDetails(record)}
          >
            {t('common.view')}
          </Button>
          <Button
            type="link"
            size="small"
            onClick={() => handleCreateTestCase(record)}
          >
            {t('testCases.create')}
          </Button>
        </Space>
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
          expandable={{ expandedRowRender: renderExpandedRow, expandedRowKeys, onExpand: handleExpand }}
          sticky
          scroll={{ x: 'max-content', y: 520 }}
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
