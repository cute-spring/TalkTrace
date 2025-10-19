import React, { useState, useEffect } from 'react'
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
      content: string
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
  }
}

const TestCaseDetail: React.FC<TestCaseDetailProps> = ({
  testCaseId,
  visible,
  onClose,
}) => {
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

  const loadTestCaseDetail = async () => {
    setLoading(true)
    try {
      const response = await testCaseService.getById(testCaseId)
      setTestCase(response.data.test_case)
    } catch (error) {
      console.error('Failed to load test case detail:', error)
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
        ? values.optimization_suggestions.split('\n').filter(s => s.trim())
        : []

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
        analyzed_by: "current_user@company.com", // 可以从用户信息获取
        analysis_date: new Date().toISOString()
      }

      await testCaseService.update(testCaseId, { analysis: analysisData })
      setAnalysisEditing(false)
      loadTestCaseDetail()
      message.success('分析数据保存成功')
    } catch (error) {
      console.error('Failed to update analysis:', error)
      message.error('保存分析失败')
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

    const config = statusConfig[status] || statusConfig.draft
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getPriorityTag = (priority: string) => {
    const priorityConfig = {
      low: { color: 'green', text: '低' },
      medium: { color: 'orange', text: '中' },
      high: { color: 'red', text: '高' },
    }

    const config = priorityConfig[priority] || priorityConfig.medium
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getQualityScoreColor = (score: number) => {
    if (score >= 4) return '#52c41a'
    if (score >= 3) return '#faad14'
    return '#ff4d4f'
  }

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
          {role === 'user' ? '用户' : role === 'assistant' ? 'AI' : '系统'}
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
              <Text strong>用户：</Text>
              <Text>{record.query}</Text>
            </div>
          )}
          {record.response && (
            <div>
              <Text strong>AI：</Text>
              <Text>{record.response}</Text>
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
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
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
      render: (content) => (
        <Text ellipsis style={{ maxWidth: 200 }}>
          {content}
        </Text>
      ),
    },
  ]

  if (!testCase) return null

  return (
    <Modal
      title="测试用例详情"
      open={visible}
      onCancel={onClose}
      width={1200}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>,
      ]}
    >
      <Tabs defaultActiveKey="overview">
        <TabPane tab="概览" key="overview">
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
              <Card title="性能指标" size="small">
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
                <Card title="用户反馈" size="small" style={{ marginTop: 16 }}>
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

        <TabPane tab="对话上下文" key="context">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card title="当前查询" size="small">
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Paragraph>{testCase.input.current_query.text}</Paragraph>
                  <Text type="secondary">
                    {new Date(testCase.input.current_query.timestamp).toLocaleString()}
                  </Text>
                </Space>
              </Card>

              <Card title="对话历史" size="small" style={{ marginTop: 16 }}>
                <Table
                  columns={conversationColumns}
                  dataSource={testCase.input.conversation_history}
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>

            <Col span={12}>
              <Card title="检索片段" size="small">
                <Table
                  columns={retrievedChunksColumns}
                  dataSource={testCase.input.current_retrieved_chunks}
                  pagination={false}
                  size="small"
                />
              </Card>
            </Col>
          </Row>
        </TabPane>

        <TabPane tab="配置" key="config">
          <Row gutter={[16, 16]}>
            <Col span={12}>
              <Card title="模型配置" size="small">
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
              <Card title="提示词配置" size="small">
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
                <Card title="检索配置" size="small" style={{ marginTop: 16 }}>
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

        <TabPane tab="执行结果" key="execution">
          <Card title="AI回答" size="small">
            <Paragraph copyable>{testCase.execution.actual.response}</Paragraph>
          </Card>

          {testCase.execution.actual.retrieval_quality && (
            <Card title="检索质量" size="small" style={{ marginTop: 16 }}>
              <Row gutter={16}>
                <Col span={8}>
                  <Statistic
                    title="最大相似度"
                    value={testCase.execution.actual.retrieval_quality.max_similarity}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="平均相似度"
                    value={testCase.execution.actual.retrieval_quality.avg_similarity}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
                <Col span={8}>
                  <Statistic
                    title="多样性分数"
                    value={testCase.execution.actual.retrieval_quality.diversity_score}
                    precision={3}
                    suffix="/ 1.0"
                  />
                </Col>
              </Row>
            </Card>
          )}
        </TabPane>

        <TabPane tab="分析" key="analysis">
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
                        notes: testCase.analysis.notes
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
                        notes: ''
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
                  <Card title="问题分析" size="small">
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
                  <Card title="质量评分" size="small">
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

              <Card title="期望答案" size="small" style={{ marginTop: 16 }}>
                <Form.Item
                  name="expected_answer"
                  rules={[{ required: true, message: '请描述期望答案' }]}
                >
                  <TextArea rows={4} placeholder="描述理想情况下AI应该如何回答这个问题..." />
                </Form.Item>
              </Card>

              <Card title="验收标准" size="small" style={{ marginTop: 16 }}>
                <Form.Item
                  name="acceptance_criteria"
                  rules={[{ required: true, message: '请描述验收标准' }]}
                >
                  <TextArea rows={3} placeholder="描述该测试用例通过的标准..." />
                </Form.Item>
              </Card>

              <Card title="优化建议" size="small" style={{ marginTop: 16 }}>
                <Form.Item name="optimization_suggestions">
                  <TextArea
                    rows={4}
                    placeholder="每行输入一条优化建议..."
                  />
                </Form.Item>
              </Card>

              <Card title="分析笔记" size="small" style={{ marginTop: 16 }}>
                <Form.Item name="notes">
                  <TextArea rows={3} placeholder="记录分析过程中的重要发现和思考..." />
                </Form.Item>
              </Card>
            </Form>
          ) : (
            <Space direction="vertical" style={{ width: '100%' }}>
              {testCase.analysis ? (
                <>
                  <Row gutter={[16, 16]}>
                    <Col span={12}>
                      <Card title="质量评分" size="small">
                        <Space direction="vertical" style={{ width: '100%' }}>
                          {Object.entries(testCase.analysis.quality_scores).map(([key, score]) => (
                            <div key={key}>
                              <Text>
                                {key === 'context_understanding' && '上下文理解'}
                                {key === 'answer_accuracy' && '回答准确性'}
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
                      <Card title="分析信息" size="small">
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
                      </Card>
                    </Col>
                  </Row>

                  <Card title="期望答案" size="small">
                    <Paragraph copyable>{testCase.analysis.expected_answer}</Paragraph>
                  </Card>

                  <Card title="验收标准" size="small">
                    <Paragraph>{testCase.analysis.acceptance_criteria}</Paragraph>
                  </Card>

                  <Card title="优化建议" size="small">
                    <ul>
                      {testCase.analysis.optimization_suggestions.map((suggestion, index) => (
                        <li key={index}>
                          <Text>{suggestion}</Text>
                        </li>
                      ))}
                    </ul>
                  </Card>

                  <Card title="分析笔记" size="small">
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