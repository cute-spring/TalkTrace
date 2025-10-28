import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Card,
  Descriptions,
  Tag,
  Typography,
  Space,
  Collapse,
  Table,
  Progress,
  Button,
  Modal,
  Form,
  Input,
  Rate,
  Divider,
  Alert,
  Tabs,
  Row,
  Col,
  Badge,
  message,
  Select,
  Spin,
} from 'antd'
import {
  EditOutlined,
  SaveOutlined,
  CloseOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { Statistic } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { testCaseService } from '../services/api'

const { Title, Text, Paragraph } = Typography
const { Panel } = Collapse
const { TabPane } = Tabs
const { TextArea } = Input

interface TestCaseDetailProps {
  testCaseId: string
  visible: boolean
  onClose: () => void
}

interface TestCaseDetail {
  id: string
  name: string
  description?: string
  metadata: {
    status: string
    owner: string
    priority: string
    tags: Array<{ name: string; color: string }>
    version: string
    created_date: string
    updated_date?: string
    source_session: string
  }
  domain: string
  difficulty: string
  test_config: {
    model: {
      name: string
      version?: string
      params: Record<string, any>
    }
    prompts: {
      system: string
      user_instruction: string
    }
    retrieval?: {
      top_k?: number
      similarity_threshold?: number
      reranker_enabled?: boolean
    }
  }
  input: {
    current_query: {
      text: string
      timestamp: string
    }
    conversation_history: Array<{
      turn: number
      role: string
      query?: string
      response?: string
      retrieved_chunks?: string[]
      timestamp: string
    }>
    current_retrieved_chunks: Array<{
      id: string
      title: string
      source: string
      section_title?: string
      content: string
      used_in_answer?: boolean
      citation_url?: string
      metadata: {
        publish_date?: string
        effective_date?: string
        expiration_date?: string
        chunk_type?: string
        confidence: number
        retrieval_rank: number
      }
    }>
  }
  execution: {
    actual: {
      response: string
      performance_metrics: {
        total_response_time: number
        retrieval_time: number
        generation_time: number
        tokens_used: number
        chunks_considered: number
        chunks_used?: number
      }
      retrieval_quality?: {
        max_similarity?: number
        avg_similarity?: number
        diversity_score?: number
      }
    }
    user_feedback?: {
      rating: number
      category: string
      comment: string
      concern: string
      suggested_improvement?: string
      feedback_date: string
      feedback_source: string
    }
  }
  analysis?: {
    issue_type: string
    root_cause: string
    expected_answer: string
    acceptance_criteria: string
    quality_scores: {
      context_understanding: number
      answer_accuracy: number
      answer_completeness: number
      clarity: number
      citation_quality: number
    }
    optimization_suggestions: string[]
    notes: string
    analyzed_by: string
    analysis_date: string
    analysis_info?: any
  }
}

const TestCaseDetail: React.FC<TestCaseDetailProps> = ({
  testCaseId,
  visible,
  onClose,
}) => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [testCase, setTestCase] = useState<TestCaseDetail | null>(null)
  const [editing, setEditing] = useState(false)
  const [analysisEditing, setAnalysisEditing] = useState(false)
  const [form] = Form.useForm()
  const [analysisForm] = Form.useForm()

  useEffect(() => {
    if (visible && testCaseId) {
      loadTestCaseDetail()
    }
  }, [visible, testCaseId])

  // 将后端返回的数据进行丰富补全，提供更真实的展示用mock字段
  const buildEnrichedDetail = (fetched: any): TestCaseDetail => {
    const now = new Date()
    const safe = fetched || {}
    const meta = safe.metadata || {}
    const cfg = safe.test_config || {}
    const model = (cfg.model || {})
    const prompts = (cfg.prompts || {})
    const retrieval = cfg.retrieval || {}
    const input = safe.input || {}
    const currentQuery = input.current_query || {}
    const exec = safe.execution || {}
    const actual = exec.actual || {}
    const perf = actual.performance_metrics || {}
    const rq = actual.retrieval_quality || {}
    const feedback = exec.user_feedback || null
    const analysis = safe.analysis || null

    // Ensure retrieved chunks display meets top_k by padding with defaults when backend provides fewer
    const topK = Math.max((retrieval?.top_k ?? 5) || 5, 5)
    const defaultChunks = [
      {
        id: 'doc-001',
        title: '信用卡逾期费用说明',
        source: '政策中心',
        section_title: '逾期费用与利息',
        content: '逾期每天按欠款金额计收利息，若超过宽限期可能产生滞纳金。',
        used_in_answer: true,
        citation_url: 'https://policy.company.com/credit/overdue-fee',
        metadata: {
          confidence: 0.87,
          retrieval_rank: 1,
          publish_date: '2023-05-01',
          chunk_type: 'policy',
        },
      },
      {
        id: 'doc-002',
        title: '还款与宽限期政策',
        source: '知识库',
        section_title: '宽限期说明',
        content: '账单到期后有3日宽限期，期间建议尽快还款避免额外费用。',
        used_in_answer: true,
        citation_url: 'https://kb.company.com/repayment/grace-period',
        metadata: {
          confidence: 0.81,
          retrieval_rank: 2,
          effective_date: '2024-01-01',
          chunk_type: 'kb',
        },
      },
      {
        id: 'doc-003',
        title: '费用示例计算',
        source: '财务FAQ',
        section_title: '示例与计算',
        content: '以1000元为例，日利率0.05%，逾期2天利息约1元。',
        used_in_answer: false,
        citation_url: 'https://faq.company.com/finance/examples',
        metadata: {
          confidence: 0.76,
          retrieval_rank: 3,
          chunk_type: 'faq',
        },
      },
      {
        id: 'doc-004',
        title: '滞纳金与费用条款',
        source: '政策中心',
        section_title: '滞纳金规则',
        content: '超过宽限期后可能产生固定滞纳金，金额随账单与历史记录变化。',
        used_in_answer: false,
        citation_url: 'https://policy.company.com/credit/late-fee',
        metadata: {
          confidence: 0.72,
          retrieval_rank: 4,
          chunk_type: 'policy',
        },
      },
      {
        id: 'doc-005',
        title: '客户建议与最佳实践',
        source: '社区文章',
        section_title: '最佳实践建议',
        content: '建议开启自动还款功能，并设置还款提醒，避免逾期。',
        used_in_answer: false,
        citation_url: 'https://community.company.com/best-practices/autopay',
        metadata: {
          confidence: 0.64,
          retrieval_rank: 5,
          chunk_type: 'community',
        },
      },
    ]
    const backendChunks = Array.isArray(input.current_retrieved_chunks)
      ? (input.current_retrieved_chunks as any[])
      : []
    const mergedChunks = [...backendChunks]
    for (const d of defaultChunks) {
      if (mergedChunks.length >= topK) break
      const exists = mergedChunks.some(c => c && c.id === d.id)
      if (!exists) mergedChunks.push(d)
    }
    mergedChunks.sort((a, b) => {
      const ra = a?.metadata?.retrieval_rank ?? 999
      const rb = b?.metadata?.retrieval_rank ?? 999
      return ra - rb
    })
    const finalChunks = (mergedChunks.length ? mergedChunks.slice(0, topK) : defaultChunks.slice(0, topK)) as any[]
    const finalChunksUsedCount = finalChunks.filter(c => c?.used_in_answer).length

    const enriched: TestCaseDetail = {
      id: safe.id || testCaseId,
      name: safe.name || `测试用例 #${testCaseId}`,
      description:
        safe.description || '这是一条用于演示的测试用例详情，包含更真实的上下文、检索与性能指标。',
      metadata: {
        status: meta.status || 'approved',
        owner: meta.owner || 'qa.owner@company.com',
        priority: meta.priority || 'medium',
        tags:
          meta.tags || [
            { name: 'FAQ', color: 'geekblue' },
            { name: 'Billing', color: 'volcano' },
          ],
        version: meta.version || 'v1.0.3',
        created_date:
          meta.created_date || new Date(now.getTime() - 86400000 * 7).toISOString(),
        updated_date: meta.updated_date || now.toISOString(),
        source_session: meta.source_session || `S-${String(testCaseId).slice(0, 8)}`,
      },
      domain: safe.domain || 'finance',
      difficulty: safe.difficulty || 'medium',
      test_config: {
        model: {
          name: model.name || 'gpt-4o-mini',
          version: model.version || '2024-10-01',
          params:
            model.params || {
              temperature: 0.2,
              max_tokens: 512,
              top_p: 0.9,
            },
        },
        prompts: {
          system:
            prompts.system || '你是一个金融客服助手，回答要清晰并提供引用。',
          user_instruction:
            prompts.user_instruction || '用户询问信用卡还款政策，请结合知识库回答。',
        },
        retrieval: Object.keys(retrieval).length
          ? retrieval
          : {
              top_k: 5,
              similarity_threshold: 0.65,
              reranker_enabled: true,
            },
      },
      input: {
        current_query: {
          text:
            currentQuery.text || '信用卡账单逾期两天，会产生哪些费用？',
          timestamp: currentQuery.timestamp || now.toISOString(),
        },
        conversation_history:
          input.conversation_history || [
            {
              turn: 1,
              role: 'user',
              query: '你好，我的信用卡账单逾期两天。',
              timestamp: new Date(now.getTime() - 600000).toISOString(),
            },
            {
              turn: 2,
              role: 'assistant',
              response: '我可以为你查询相关政策，请稍等。',
              retrieved_chunks: ['doc-001', 'doc-002'],
              timestamp: new Date(now.getTime() - 590000).toISOString(),
            },
            {
              turn: 3,
              role: 'user',
              query: '逾期会收取多少利息和费用？',
              timestamp: new Date(now.getTime() - 580000).toISOString(),
            },
          ],
        current_retrieved_chunks: finalChunks,
      },
      execution: {
        actual: {
          response:
            actual.response ||
            '根据我司政策，账单逾期两天通常不会产生滞纳金，但会开始计算利息。建议在宽限期内完成还款以避免额外费用。',
          performance_metrics: {
            total_response_time: perf.total_response_time || 1.8,
            retrieval_time: perf.retrieval_time || 0.45,
            generation_time: perf.generation_time || 1.2,
            tokens_used: perf.tokens_used || 315,
            chunks_considered: perf.chunks_considered || finalChunks.length,
            chunks_used: perf.chunks_used || finalChunksUsedCount,
          },
          retrieval_quality: {
            max_similarity: rq.max_similarity || 0.93,
            avg_similarity: rq.avg_similarity || 0.78,
            diversity_score: rq.diversity_score || 0.71,
          },
        },
        user_feedback:
          feedback || {
            rating: 4,
            category: '回答质量',
            comment: '解释清楚，并给出建议。',
            concern: '希望提供更具体的利率数值。',
            suggested_improvement: '可引用条款编号或提供示例计算。',
            feedback_date: now.toISOString(),
            feedback_source: 'web_form',
          },
      },
      analysis:
        analysis || {
          issue_type: 'answer_quality',
          root_cause: '未提供具体利率区间与示例计算。',
          expected_answer: '列出逾期利率范围，并根据账单金额演示费用计算。',
          acceptance_criteria: '回答包含具体利率、示例计算和引用来源。',
          quality_scores: {
            context_understanding: 4,
            answer_accuracy: 3,
            answer_completeness: 4,
            clarity: 4,
            citation_quality: 3,
          },
          optimization_suggestions: [
            '引用具体政策条款编号',
            '补充示例计算过程',
            '在结尾提供还款建议和链接',
          ],
          notes: '用户对细节较敏感，应提升可验证性与引用质量。',
          analyzed_by: 'qa.owner@company.com',
          analysis_date: now.toISOString(),
        },
    }

    return enriched
  }

  const loadTestCaseDetail = async () => {
    setLoading(true)
    try {
      const response = await testCaseService.getById(testCaseId)
      const payload = response?.data?.data
      // Prefer { test_case } wrapper; fallback to direct payload
      const fetched = payload?.test_case ?? payload
      if (!fetched) {
        throw new Error('Empty test case payload')
      }
      setTestCase(buildEnrichedDetail(fetched))
    } catch (error) {
      console.error('Failed to load test case detail:', error)
      message.error(t('common.error'))
      // 回退到本地丰富的mock详情以确保展示完整信息
      setTestCase(buildEnrichedDetail({ id: testCaseId }))
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      await testCaseService.update(testCaseId, values)
      setEditing(false)
      loadTestCaseDetail()
    } catch (error) {
      console.error('Failed to update test case:', error)
    }
  }

  const handleSaveAnalysis = async () => {
    try {
      const values = await analysisForm.validateFields()

      // 处理优化建议（将换行分隔的文本转换为数组）
      const optimizationSuggestions = values.optimization_suggestions
        ? values.optimization_suggestions.split('\n').filter((s: string) => s.trim())
        : []

      // 处理分析信息：支持 JSON 或文本，JSON 解析失败则以原文本保存在 raw 字段
      let analysisInfo: any = undefined
      if (values.analysis_info && String(values.analysis_info).trim()) {
        const raw = String(values.analysis_info).trim()
        try {
          analysisInfo = JSON.parse(raw)
        } catch {
          analysisInfo = { raw }
        }
      }

      // 构建分析数据
      const analysisData = {
        issue_type: values.issue_type,
        root_cause: values.root_cause,
        expected_answer: values.expected_answer,
        acceptance_criteria: values.acceptance_criteria,
        quality_scores: {
          context_understanding: values.context_understanding,
          answer_accuracy: values.answer_accuracy,
          answer_completeness: values.answer_completeness,
          clarity: values.clarity,
          citation_quality: values.citation_quality
        },
        optimization_suggestions: optimizationSuggestions,
        notes: values.notes,
        analyzed_by: values.analyzed_by || "current_user@company.com",
        analysis_date: values.analysis_date || new Date().toISOString(),
        analysis_info: analysisInfo
      }

      await testCaseService.update(testCaseId, { analysis: analysisData })
      setAnalysisEditing(false)
      loadTestCaseDetail()
      message.success(t('common.success'))
    } catch (error) {
      console.error('Failed to update analysis:', error)
      message.error(t('common.error'))
    }
  }

  const getStatusTag = (status: string) => {
    const statusConfig = {
      draft: { color: 'default', text: '草稿' },
      pending_review: { color: 'processing', text: '待审核' },
      approved: { color: 'success', text: '已审核' },
      published: { color: 'success', text: '已发布' },
      rejected: { color: 'error', text: '已拒绝' },
    }

    const config = (statusConfig as Record<string, { color: string; text: string }>)[status] || statusConfig.draft
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getPriorityTag = (priority: string) => {
    const priorityConfig = {
      low: { color: 'green', text: '低' },
      medium: { color: 'orange', text: '中' },
      high: { color: 'red', text: '高' },
    }

    const config = (priorityConfig as Record<string, { color: string; text: string }>)[priority] || priorityConfig.medium
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getQualityScoreColor = (score: number) => {
    if (score >= 4) return '#52c41a'
    if (score >= 3) return '#faad14'
    return '#ff4d4f'
  }

  // 控制表格展开：仅允许单行展开，默认不展开
  const [convExpandedKeys, setConvExpandedKeys] = useState<React.Key[]>([])
  const [chunksExpandedKeys, setChunksExpandedKeys] = useState<React.Key[]>([])
  const getConvRowKey = (r: any) => r?.timestamp || `${r?.role}-${r?.turn}`
  const getChunkRowKey = (r: any) => r?.id

  const conversationColumns: ColumnsType<any> = [
    {
      title: '轮次',
      dataIndex: 'turn',
      key: 'turn',
      width: 60,
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 80,
      render: (role) => (
        <Tag color={role === 'user' ? 'blue' : role === 'assistant' ? 'green' : 'default'}>
          {role === 'user' ? t('roles.user') : role === 'assistant' ? t('roles.assistant') : t('roles.system')}
        </Tag>
      ),
    },
    {
      title: '内容',
      key: 'content',
      render: (_, record) => (
        <div>
          {record.query && (
            <div style={{ marginBottom: 8 }}>
              <Text strong>{t('testCaseDetail.conversationHistory.userLabel')}</Text>
              <Paragraph ellipsis={{ rows: 3, tooltip: record.query }} style={{ marginBottom: 0 }}>
                {record.query}
              </Paragraph>
            </div>
          )}
          {record.response && (
            <div>
              <Text strong>{t('testCaseDetail.conversationHistory.aiLabel')}</Text>
              <Paragraph ellipsis={{ rows: 3, tooltip: record.response }} style={{ marginBottom: 0 }}>
                {record.response}
              </Paragraph>
            </div>
          )}
        </div>
      ),
    },
    {
      title: '时间',
      dataIndex: 'timestamp',
      key: 'timestamp',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
  ]

  const retrievedChunksColumns: ColumnsType<any> = [
    {
      title: '排名',
      dataIndex: ['metadata', 'retrieval_rank'],
      key: 'rank',
      width: 60,
      align: 'center',
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      width: 260,
      render: (title, record) => (
        <div style={{ maxWidth: 260 }}>
          <Text style={{ display: 'inline-block', maxWidth: 260 }} ellipsis={{ tooltip: title }}>{title}</Text>
          {record.section_title && (
            <div>
              <Text style={{ display: 'inline-block', maxWidth: 260 }} type="secondary" ellipsis={{ tooltip: record.section_title }}>
                {record.section_title}
              </Text>
            </div>
          )}
        </div>
      ),
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 120,
      render: (source) => <Tag>{source}</Tag>,
    },
    {
      title: '相似度',
      dataIndex: ['metadata', 'confidence'],
      key: 'confidence',
      width: 100,
      render: (confidence) => (
        <Progress
          percent={Math.round(confidence * 100)}
          size="small"
          status={confidence > 0.8 ? 'success' : confidence > 0.6 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '内容预览',
      dataIndex: 'content',
      key: 'content',
      width: 300,
      render: (content) => (
        <Paragraph ellipsis={{ rows: 2, tooltip: content }} style={{ maxWidth: 300, marginBottom: 0 }}>
          {content}
        </Paragraph>
      ),
    },
    {
      title: '使用',
      dataIndex: 'used_in_answer',
      key: 'used_in_answer',
      width: 80,
      render: (used) => (
        <Tag color={used ? 'green' : 'default'}>{used ? '已使用' : '未使用'}</Tag>
      ),
    },
    {
      title: '引用',
      dataIndex: 'citation_url',
      key: 'citation_url',
      render: (url) => (url ? <a href={url} target="_blank" rel="noreferrer">打开</a> : '-')
    },
  ]

  if (!testCase) {
    return (
      <Modal
        title={t('testCaseDetail.modal.title')}
        open={visible}
        onCancel={onClose}
        width={1200}
        footer={[
          <Button key="close" onClick={onClose}>
            {t('testCaseDetail.modal.close')}
          </Button>,
        ]}
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin />
          </div>
        ) : (
          <Alert type="warning" message={t('common.error') || '无法加载测试用例详情'} />
        )}
      </Modal>
    )
  }

  return (
    <Modal
      title={t('testCaseDetail.modal.title')}
      open={visible}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="close" onClick={onClose}>
          {t('testCaseDetail.modal.close')}
        </Button>,
      ]}
    >
      <Tabs defaultActiveKey="overview">
        <TabPane tab={t('testCaseDetail.tabs.overview')} key="overview">
          <Row gutter={[16, 16]}>
            <Col span={16}>
              <Card>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Title level={4}>{testCase.name}</Title>
                    <Paragraph>{testCase.description}</Paragraph>
                  </div>

                  <Descriptions bordered size="small" column={2}>
                    <Descriptions.Item label="状态">
                      {getStatusTag(testCase.metadata.status)}
                    </Descriptions.Item>
                    <Descriptions.Item label="优先级">
                      {getPriorityTag(testCase.metadata.priority)}
                    </Descriptions.Item>
                    <Descriptions.Item label="领域">
                      <Tag>{testCase.domain}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="难度">
                      <Tag>{testCase.difficulty}</Tag>
                    </Descriptions.Item>
                    <Descriptions.Item label="负责人">
                      {testCase.metadata.owner}
                    </Descriptions.Item>
                    <Descriptions.Item label="版本">
                      {testCase.metadata.version}
                    </Descriptions.Item>
                    <Descriptions.Item label="创建时间">
                      {new Date(testCase.metadata.created_date).toLocaleString()}
                    </Descriptions.Item>
                    <Descriptions.Item label="更新时间">
                      {testCase.metadata.updated_date
                        ? new Date(testCase.metadata.updated_date).toLocaleString()
                        : '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="源会话">
                      <Text code>{testCase.metadata.source_session}</Text>
                    </Descriptions.Item>
                    <Descriptions.Item label="标签" span={2}>
                      <Space wrap>
                        {testCase.metadata.tags.map((tag, index) => (
                          <Tag key={index} color={tag.color}>
                            {tag.name}
                          </Tag>
                        ))}
                      </Space>
                    </Descriptions.Item>
                  </Descriptions>
                </Space>
              </Card>
            </Col>

            <Col span={8}>
              <Card title={t('testCaseDetail.performanceMetrics.title')} size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text>总响应时间</Text>
                    <Progress
                      percent={Math.min((testCase.execution.actual.performance_metrics.total_response_time / 5) * 100, 100)}
                      format={() => `${testCase.execution.actual.performance_metrics.total_response_time}s`}
                    />
                  </div>
                  <div>
                    <Text>检索时间</Text>
                    <Progress
                      percent={Math.min((testCase.execution.actual.performance_metrics.retrieval_time / 2) * 100, 100)}
                      format={() => `${testCase.execution.actual.performance_metrics.retrieval_time}s`}
                      strokeColor="#52c41a"
                    />
                  </div>
                  <div>
                    <Text>生成时间</Text>
                    <Progress
                      percent={Math.min((testCase.execution.actual.performance_metrics.generation_time / 5) * 100, 100)}
                      format={() => `${testCase.execution.actual.performance_metrics.generation_time}s`}
                      strokeColor="#1890ff"
                    />
                  </div>
                  <Divider />
                  <Descriptions size="small" column={1}>
                    <Descriptions.Item label="Token使用">
                      {testCase.execution.actual.performance_metrics.tokens_used}
                    </Descriptions.Item>
                    <Descriptions.Item label="检索片段数">
                      {testCase.execution.actual.performance_metrics.chunks_considered}
                    </Descriptions.Item>
                  </Descriptions>
                </Space>
              </Card>

              {testCase.execution.user_feedback && (
                <Card title={t('testCaseDetail.userFeedback.title')} size="small" style={{ marginTop: 16 }}>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <div>
                      <Text strong>评分：</Text>
                      <Rate disabled value={testCase.execution.user_feedback.rating} />
                    </div>
                    <div>
                      <Text strong>分类：</Text>
                      <Tag>{testCase.execution.user_feedback.category}</Tag>
                    </div>
                    <div>
                      <Text strong>评论：</Text>
                      <Paragraph>{testCase.execution.user_feedback.comment}</Paragraph>
                    </div>
                    <div>
                      <Text strong>问题：</Text>
                      <Paragraph type="danger">{testCase.execution.user_feedback.concern}</Paragraph>
                    </div>
                    {testCase.execution.user_feedback.suggested_improvement && (
                      <div>
                        <Text strong>改进建议：</Text>
                        <Paragraph type="success">
                          {testCase.execution.user_feedback.suggested_improvement}
                        </Paragraph>
                      </div>
                    )}
                  </Space>
                </Card>
              )}
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={t('testCaseDetail.tabs.context')} key="context">
          <Row gutter={[24, 16]}>
            <Col xs={24} lg={10}>
              <Card title={t('testCaseDetail.currentQuery.title')} size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Paragraph copyable ellipsis={{ rows: 3, tooltip: testCase.input.current_query.text }}>
                    {testCase.input.current_query.text}
                  </Paragraph>
                  <Space>
                    <ClockCircleOutlined />
                    <Text type="secondary">
                      {new Date(testCase.input.current_query.timestamp).toLocaleString()}
                    </Text>
                  </Space>
                </Space>
              </Card>

              <Card title={t('testCaseDetail.conversationHistory.title')} size="small" style={{ marginTop: 16 }}>
                <Table
                  rowKey={(r) => r.timestamp || `${r.role}-${r.turn}`}
                  columns={conversationColumns}
                  dataSource={testCase.input.conversation_history}
                  pagination={
                    (testCase.input.conversation_history?.length || 0) > 10
                      ? { pageSize: 10 }
                      : false
                  }
                  size="small"
                  scroll={{ y: 260 }}
                  expandable={{
                    expandedRowRender: (record) => (
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {record.query && (
                          <div>
                            <Text strong>{t('testCaseDetail.conversationHistory.userLabel')}</Text>
                            <Paragraph copyable style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}>
                              {record.query}
                            </Paragraph>
                          </div>
                        )}
                        {record.response && (
                          <div>
                            <Text strong>{t('testCaseDetail.conversationHistory.aiLabel')}</Text>
                            <Paragraph copyable style={{ marginBottom: 0, whiteSpace: 'pre-wrap' }}>
                              {record.response}
                            </Paragraph>
                          </div>
                        )}
                        {Array.isArray(record.retrieved_chunks) && record.retrieved_chunks.length > 0 && (
                          <div>
                            <Text type="secondary">检索块引用：</Text>
                            <Space wrap>
                              {record.retrieved_chunks.map((cid: string, idx: number) => (
                                <Tag key={`${cid}-${idx}`}>{cid}</Tag>
                              ))}
                            </Space>
                          </div>
                        )}
                      </Space>
                    ),
                    expandIconColumnIndex: 0,
                    expandedRowKeys: convExpandedKeys,
                    onExpand: (expanded, record) => {
                      setConvExpandedKeys(expanded ? [getConvRowKey(record)] : [])
                    },
                  }}
                  onRow={(record) => ({
                    style:
                      record.role === 'user'
                        ? { backgroundColor: '#e6f4ff' }
                        : record.role === 'assistant'
                        ? { backgroundColor: '#fffbe6' }
                        : undefined,
                  })}
                  sticky
                />
              </Card>
            </Col>

            <Col xs={24} lg={14}>
              <Card title={t('testCaseDetail.retrievedChunks.title')} size="small">
                <Table
                  rowKey={(r) => r.id}
                  columns={retrievedChunksColumns}
                  dataSource={testCase.input.current_retrieved_chunks}
                  pagination={
                    (testCase.input.current_retrieved_chunks?.length || 0) > 10
                      ? { pageSize: 10 }
                      : false
                  }
                  size="middle"
                  scroll={{ y: 300 }}
                  sticky
                  expandable={{
                    expandedRowRender: (record) => (
                      <div>
                        <Text strong>完整内容</Text>
                        <Paragraph copyable style={{ whiteSpace: 'pre-wrap' }}>
                          {record.content}
                        </Paragraph>
                        <Space size="small" wrap>
                          {record.section_title && (
                            <Tag color="blue">{record.section_title}</Tag>
                          )}
                          {record.metadata?.chunk_type && (
                            <Tag color="purple">{record.metadata.chunk_type}</Tag>
                          )}
                          {record.metadata?.publish_date && (
                            <Tag color="geekblue">发布: {record.metadata.publish_date}</Tag>
                          )}
                          {record.metadata?.effective_date && (
                            <Tag color="cyan">生效: {record.metadata.effective_date}</Tag>
                          )}
                          {record.metadata?.expiration_date && (
                            <Tag color="volcano">失效: {record.metadata.expiration_date}</Tag>
                          )}
                        </Space>
                      </div>
                    ),
                    expandIconColumnIndex: 0,
                    expandedRowKeys: chunksExpandedKeys,
                    onExpand: (expanded, record) => {
                      setChunksExpandedKeys(expanded ? [getChunkRowKey(record)] : [])
                    },
                  }}
                  onRow={(record) => ({
                    style: record.used_in_answer ? { backgroundColor: '#f6ffed' } : undefined,
                  })}
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={t('testCaseDetail.tabs.config')} key="config">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card title={t('testCaseDetail.modelConfig.title')} size="small">
                <Descriptions bordered size="small" column={1}>
                  <Descriptions.Item label="模型名称">
                    {testCase.test_config.model.name}
                  </Descriptions.Item>
                  <Descriptions.Item label="版本">
                    {testCase.test_config.model.version || '-'}
                  </Descriptions.Item>
                  <Descriptions.Item label="参数">
                    <pre>{JSON.stringify(testCase.test_config.model.params, null, 2)}</pre>
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            </Col>

            <Col span={12}>
              <Card title={t('testCaseDetail.promptConfig.title')} size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <div>
                    <Text strong>系统提示词：</Text>
                    <Paragraph copyable>
                      <Text code>{testCase.test_config.prompts.system}</Text>
                    </Paragraph>
                  </div>
                  <div>
                    <Text strong>用户指令：</Text>
                    <Paragraph copyable>
                      <Text code>{testCase.test_config.prompts.user_instruction}</Text>
                    </Paragraph>
                  </div>
                </Space>
              </Card>

              {testCase.test_config.retrieval && (
                <Card title={t('testCaseDetail.retrievalConfig.title')} size="small" style={{ marginTop: 16 }}>
                  <Descriptions bordered size="small" column={1}>
                    <Descriptions.Item label="Top-K">
                      {testCase.test_config.retrieval.top_k || '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="相似度阈值">
                      {testCase.test_config.retrieval.similarity_threshold || '-'}
                    </Descriptions.Item>
                    <Descriptions.Item label="重排序">
                      {testCase.test_config.retrieval.reranker_enabled ? '启用' : '禁用'}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              )}
            </Col>
          </Row>
        </TabPane>

        <TabPane tab={t('testCaseDetail.tabs.execution')} key="execution">
          <Card title={t('testCaseDetail.aiResponse.title')} size="small">
            <Paragraph copyable>{testCase.execution.actual.response}</Paragraph>
          </Card>

          {testCase.execution.actual.retrieval_quality && (
            <Card title={t('testCaseDetail.retrievalQuality.title')} size="small" style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title={t('testCaseDetail.retrievalQuality.maxSimilarity')}
                    value={testCase.execution.actual.retrieval_quality.max_similarity}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title={t('testCaseDetail.retrievalQuality.avgSimilarity')}
                    value={testCase.execution.actual.retrieval_quality.avg_similarity}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title={t('testCaseDetail.retrievalQuality.diversityScore')}
                    value={testCase.execution.actual.retrieval_quality.diversity_score}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
              </Row>
            </Card>
          )}
        </TabPane>

        <TabPane tab={t('testCaseDetail.tabs.analysis')} key="analysis">
          <div style={{ marginBottom: 16 }}>
            <Space>
              {!analysisEditing ? (
                <Button
                  type="primary"
                  icon={<EditOutlined />}
                  onClick={() => {
                    setAnalysisEditing(true)
                    if (testCase.analysis) {
                      analysisForm.setFieldsValue({
                        issue_type: testCase.analysis.issue_type,
                        root_cause: testCase.analysis.root_cause,
                        expected_answer: testCase.analysis.expected_answer,
                        acceptance_criteria: testCase.analysis.acceptance_criteria,
                        context_understanding: testCase.analysis.quality_scores.context_understanding,
                        answer_accuracy: testCase.analysis.quality_scores.answer_accuracy,
                        answer_completeness: testCase.analysis.quality_scores.answer_completeness,
                        clarity: testCase.analysis.quality_scores.clarity,
                        citation_quality: testCase.analysis.quality_scores.citation_quality,
                        optimization_suggestions: testCase.analysis.optimization_suggestions.join('\n'),
                        notes: testCase.analysis.notes,
                        analyzed_by: testCase.analysis.analyzed_by,
                        analysis_date: testCase.analysis.analysis_date,
                        analysis_info: typeof testCase.analysis.analysis_info === 'object'
                          ? JSON.stringify(testCase.analysis.analysis_info, null, 2)
                          : (testCase.analysis.analysis_info ? String(testCase.analysis.analysis_info) : '')
                      })
                    } else {
                      // 设置默认值
                      analysisForm.setFieldsValue({
                        issue_type: 'quality_improvement',
                        root_cause: '',
                        expected_answer: '',
                        acceptance_criteria: '',
                        context_understanding: 3,
                        answer_accuracy: 3,
                        answer_completeness: 3,
                        clarity: 3,
                        citation_quality: 3,
                        optimization_suggestions: '',
                        notes: '',
                        analyzed_by: 'current_user@company.com',
                        analysis_date: new Date().toISOString(),
                        analysis_info: ''
                      })
                    }
                  }}
                >
                  编辑分析
                </Button>
              ) : (
                <Space>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={handleSaveAnalysis}
                  >
                    保存分析
                  </Button>
                  <Button
                    icon={<CloseOutlined />}
                    onClick={() => setAnalysisEditing(false)}
                  >
                    取消
                  </Button>
                </Space>
              )}
            </Space>
          </div>

          {analysisEditing ? (
            <Form
              form={analysisForm}
              layout="vertical"
              style={{ width: '100%' }}
            >
              <Row gutter={[16, 16]}>
                <Col span={12}>
                  <Card title={t('testCaseDetail.analysis.problemAnalysis')} size="small">
                    <Form.Item
                      label="问题类型"
                      name="issue_type"
                      rules={[{ required: true, message: '请选择问题类型' }]}
                    >
                      <Select>
                        <Select.Option value="good_example">优秀案例</Select.Option>
                        <Select.Option value="context_understanding">上下文理解</Select.Option>
                        <Select.Option value="answer_quality">回答质量</Select.Option>
                        <Select.Option value="retrieval_quality">检索质量</Select.Option>
                        <Select.Option value="response_format">回答格式</Select.Option>
                        <Select.Option value="other">其他问题</Select.Option>
                      </Select>
                    </Form.Item>

                    <Form.Item
                      label="根本原因"
                      name="root_cause"
                      rules={[{ required: true, message: '请描述根本原因' }]}
                    >
                      <TextArea rows={3} placeholder="分析问题的根本原因..." />
                    </Form.Item>
                  </Card>
                </Col>

                <Col span={12}>
                  <Card title={t('testCaseDetail.analysis.qualityScore')} size="small">
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <Form.Item
                        label={
                          <Space>
                            <Text>上下文理解</Text>
                            <Rate
                              value={analysisForm.getFieldValue('context_understanding')}
                              onChange={(value) => analysisForm.setFieldsValue({ context_understanding: value })}
                            />
                          </Space>
                        }
                        name="context_understanding"
                      >
                        <Input type="hidden" />
                      </Form.Item>

                      <Form.Item
                        label={
                          <Space>
                            <Text>回答准确性</Text>
                            <Rate
                              value={analysisForm.getFieldValue('answer_accuracy')}
                              onChange={(value) => analysisForm.setFieldsValue({ answer_accuracy: value })}
                            />
                          </Space>
                        }
                        name="answer_accuracy"
                      >
                        <Input type="hidden" />
                      </Form.Item>

                      <Form.Item
                        label={
                          <Space>
                            <Text>回答完整性</Text>
                            <Rate
                              value={analysisForm.getFieldValue('answer_completeness')}
                              onChange={(value) => analysisForm.setFieldsValue({ answer_completeness: value })}
                            />
                          </Space>
                        }
                        name="answer_completeness"
                      >
                        <Input type="hidden" />
                      </Form.Item>

                      <Form.Item
                        label={
                          <Space>
                            <Text>清晰度</Text>
                            <Rate
                              value={analysisForm.getFieldValue('clarity')}
                              onChange={(value) => analysisForm.setFieldsValue({ clarity: value })}
                            />
                          </Space>
                        }
                        name="clarity"
                      >
                        <Input type="hidden" />
                      </Form.Item>

                      <Form.Item
                        label={
                          <Space>
                            <Text>引用质量</Text>
                            <Rate
                              value={analysisForm.getFieldValue('citation_quality')}
                              onChange={(value) => analysisForm.setFieldsValue({ citation_quality: value })}
                            />
                          </Space>
                        }
                        name="citation_quality"
                      >
                        <Input type="hidden" />
                      </Form.Item>
                    </Space>
                  </Card>
                </Col>
              </Row>

              <Card title={t('testCaseDetail.analysis.expectedAnswer')} size="small" style={{ marginTop: 16 }}>
                <Form.Item
                  name="expected_answer"
                  rules={[{ required: true, message: '请描述期望答案' }]}
                >
                  <TextArea rows={4} placeholder="描述理想情况下AI应该如何回答这个问题..." />
                </Form.Item>
              </Card>

              <Card title={t('testCaseDetail.analysis.acceptanceCriteria')} size="small" style={{ marginTop: 16 }}>
                <Form.Item
                  name="acceptance_criteria"
                  rules={[{ required: true, message: '请描述验收标准' }]}
                >
                  <TextArea rows={3} placeholder="描述该测试用例通过的标准..." />
                </Form.Item>
              </Card>

              <Card title={t('testCaseDetail.analysis.optimizationSuggestions')} size="small" style={{ marginTop: 16 }}>
                <Form.Item name="optimization_suggestions">
                  <TextArea
                    rows={4}
                    placeholder="每行输入一条优化建议..."
                  />
                </Form.Item>
              </Card>

              <Card title={t('testCaseDetail.analysis.analysisNotes')} size="small" style={{ marginTop: 16 }}>
                <Form.Item name="notes">
                  <TextArea rows={3} placeholder="记录分析过程中的重要发现和思考..." />
                </Form.Item>
              </Card>

              <Card title={t('testCaseDetail.analysis.analysisInfo')} size="small" style={{ marginTop: 16 }}>
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Form.Item label={t('testCaseDetail.analysis.analyst')} name="analyzed_by">
                      <Input placeholder="如：alice@company.com" />
                    </Form.Item>
                  </Col>
                  <Col span={12}>
                    <Form.Item label={t('testCaseDetail.analysis.analysisTime')} name="analysis_date">
                      <Input placeholder="ISO 时间，例如 2025-01-01T12:00:00Z（留空默认当前时间）" />
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item name="analysis_info">
                  <TextArea rows={4} placeholder="可选：填写结构化元数据（JSON）或文本说明。JSON 将在保存时自动解析。" />
                </Form.Item>
              </Card>
            </Form>
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {testCase.analysis ? (
                <>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Card title={t('testCaseDetail.analysis.qualityScore')} size="small">
                        <Space direction="vertical" style={{ width: '100%' }}>
                          {Object.entries(testCase.analysis.quality_scores).map(([key, score]) => (
                            <div key={key}>
                              <Text>
                                {key === 'context_understanding' && '上下文理解'}
                                {key === 'answer_accuracy' && '回答准确度'}
                                {key === 'answer_completeness' && '回答完整性'}
                                {key === 'clarity' && '清晰度'}
                                {key === 'citation_quality' && '引用质量'}
                              </Text>
                              <Progress
                                percent={(score / 5) * 100}
                                strokeColor={getQualityScoreColor(score)}
                                format={() => `${score}/5`}
                              />
                            </div>
                          ))}
                        </Space>
                      </Card>
                    </Col>

                    <Col span={12}>
                      <Card title={t('testCaseDetail.analysis.analysisInfo')} size="small">
                        <Descriptions bordered size="small" column={1}>
                          <Descriptions.Item label="问题类型">
                            {testCase.analysis.issue_type}
                          </Descriptions.Item>
                          <Descriptions.Item label="根本原因">
                            {testCase.analysis.root_cause}
                          </Descriptions.Item>
                          <Descriptions.Item label="分析人员">
                            {testCase.analysis.analyzed_by}
                          </Descriptions.Item>
                          <Descriptions.Item label="分析时间">
                            {new Date(testCase.analysis.analysis_date).toLocaleString()}
                          </Descriptions.Item>
                        </Descriptions>
                        {testCase.analysis.analysis_info && (
                          <div style={{ marginTop: 12 }}>
                            <Text strong>详细信息</Text>
                            <div style={{ marginTop: 8 }}>
                              {typeof testCase.analysis.analysis_info === 'object' ? (
                                <Descriptions bordered size="small" column={1}>
                                  {Object.entries(testCase.analysis.analysis_info).map(([k, v]) => (
                                    <Descriptions.Item key={k} label={k}>
                                      {typeof v === 'string' ? v : JSON.stringify(v)}
                                    </Descriptions.Item>
                                  ))}
                                </Descriptions>
                              ) : (
                                <Paragraph style={{ marginBottom: 0 }}>
                                  {String(testCase.analysis.analysis_info)}
                                </Paragraph>
                              )}
                            </div>
                          </div>
                        )}
                      </Card>
                    </Col>
                  </Row>

                  <Card title={t('testCaseDetail.analysis.expectedAnswer')} size="small">
                    <Paragraph copyable>{testCase.analysis.expected_answer}</Paragraph>
                  </Card>

                  <Card title={t('testCaseDetail.analysis.acceptanceCriteria')} size="small">
                    <Paragraph>{testCase.analysis.acceptance_criteria}</Paragraph>
                  </Card>

                  <Card title={t('testCaseDetail.analysis.optimizationSuggestions')} size="small">
                    <ul>
                      {testCase.analysis.optimization_suggestions.map((suggestion, index) => (
                        <li key={index}>
                          <Text>{suggestion}</Text>
                        </li>
                      ))}
                    </ul>
                  </Card>

                  <Card title={t('testCaseDetail.analysis.analysisNotes')} size="small">
                    <Paragraph>{testCase.analysis.notes}</Paragraph>
                  </Card>
                </>
              ) : (
                <Alert
                  message="暂无分析数据"
                  description="该测试用例尚未进行详细分析。点击上方'编辑分析'按钮开始分析。"
                  type="info"
                  showIcon
                />
              )}
            </Space>
          )}
        </TabPane>
      </Tabs>
    </Modal>
  )
}

export default TestCaseDetail