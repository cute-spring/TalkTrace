import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Card,
  Steps,
  Button,
  Table,
  Space,
  Tag,
  Input,
  Select,
  Checkbox,
  message,
  Progress,
  Typography,
  Alert,
  Row,
  Col,
} from 'antd'
import { ImportOutlined, CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { importService, historyService } from '../services/api'

const { Step } = Steps
const { Title, Text } = Typography

interface ImportTask {
  taskId: string
  status: string
  total: number
  processed: number
  failed: number
  skipped: number
  startTime: string
  endTime?: string
}

interface SessionRecord {
  session_id: string
  user_query: string
  ai_response: string
  user_rating: number
  model_id: string
  created_at: string
}

interface PreviewSession {
  session_id: string
  message_count: number
  first_message: string
  last_message: string
  has_user_rating: boolean
}

interface DuplicateSessionInfo {
  session_id: string
  existing_test_case_id: string
  existing_test_case_name: string
  import_date: string
  owner: string
}

interface ValidationResult {
  valid_sessions: string[]
  duplicate_sessions: DuplicateSessionInfo[]
  can_import_all: boolean
  total_count: number
  duplicate_count: number
  message: string
}

const ImportPage: React.FC = () => {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const [currentStep, setCurrentStep] = useState(0)

  // Helper function for robust translation with interpolation
  const translateWithValues = (key: string, values: Record<string, number | string> = {}) => {
    try {
      const result = t(key, values)
      // If the result still contains placeholders, use template literals as fallback
      if (typeof result === 'string' && (result.includes('{{') || result.includes('{'))) {
        // For debugging in development
        if (process.env.NODE_ENV === 'development') {
          console.warn(`Translation interpolation failed for key "${key}", using fallback`)
        }

        // Simple template literal replacement
        let fallback = result
        Object.entries(values).forEach(([placeholder, value]) => {
          fallback = fallback.replace(new RegExp(`{{${placeholder}}}`, 'g'), String(value))
          fallback = fallback.replace(new RegExp(`{${placeholder}}`, 'g'), String(value))
        })
        return fallback
      }
      return result
    } catch (error) {
      console.error(`Translation error for key "${key}":`, error)
      return key // Return the key as fallback
    }
  }
  const [loading, setLoading] = useState(false)
  const [sessionIds, setSessionIds] = useState<string[]>([])
  const [previewData, setPreviewData] = useState<PreviewSession[]>([])
  const [importTasks, setImportTasks] = useState<ImportTask[]>([])
  const [currentTask, setCurrentTask] = useState<ImportTask | null>(null)
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null)
  const [duplicateSessions, setDuplicateSessions] = useState<DuplicateSessionInfo[]>([])
  const [importConfig, setImportConfig] = useState({
    defaultOwner: '',
    defaultPriority: 'medium',
    defaultDifficulty: 'medium',
    includeAnalysis: false,
    skipDuplicates: false,
  })

  // 从URL参数获取会话ID
  useEffect(() => {
    const idsFromUrl = searchParams.get('sessionIds')
    if (idsFromUrl) {
      const ids = idsFromUrl.split(',').filter(id => id.trim())
      setSessionIds(ids)
      setCurrentStep(1)
      loadPreviewData(ids)
    }
  }, [searchParams])

  // 加载预览数据
  const loadPreviewData = async (ids: string[]) => {
    setLoading(true)
    try {
      const response = await importService.preview({ session_ids: ids })
      const data = response.data.data || response.data
      setPreviewData(data.preview_data || [])

      // 设置重复会话信息
      if (data.duplicate_sessions) {
        setDuplicateSessions(data.duplicate_sessions)
      }

      // 设置验证结果
      if (data.validation_result) {
        setValidationResult(data.validation_result)
      }

      // 显示重复信息提示
      if (data.validation_result && data.validation_result.duplicate_count > 0) {
        const validation = data.validation_result
        message.warning(translateWithValues('import.duplicateWarning', {
          duplicateCount: validation.duplicate_count,
          validCount: validation.valid_sessions.length
        }))
      } else {
        message.success(t('import.previewLoadSuccess'))
      }
    } catch (error) {
      message.error(t('import.previewLoadFailed'))
      console.error('Failed to load preview:', error)
    } finally {
      setLoading(false)
    }
  }

  // 开始导入
  const handleStartImport = async () => {
    if (!importConfig.defaultOwner) {
      message.error(t('import.ownerRequired'))
      return
    }

    setLoading(true)
    try {
      const response = await importService.execute({
        session_ids: sessionIds,
        defaultOwner: importConfig.defaultOwner,
        defaultPriority: importConfig.defaultPriority,
        defaultDifficulty: importConfig.defaultDifficulty,
        includeAnalysis: importConfig.includeAnalysis,
        skipDuplicates: importConfig.skipDuplicates,
      })

      // Debug: Log the response structure
      console.log('Import execute response:', response.data)
      console.log('Task ID from response:', response.data.data.task_id)
      console.log('Task keys:', Object.keys(response.data.data))
      console.log('Has task_id:', 'task_id' in response.data.data)

      // Try alternative access methods
      console.log('Task ID via dot notation:', response.data.data.task_id)
      console.log('Task ID via bracket notation:', response.data.data['task_id'])

      setCurrentTask({
        taskId: response.data.data.task_id,
        status: 'running',
        total: sessionIds.length,
        processed: 0,
        failed: 0,
        startTime: new Date().toISOString(),
      })

      setCurrentStep(2)
      message.success(t('import.importStarted'))

      // 开始轮询进度
      pollProgress(response.data.data.task_id)
    } catch (error) {
      message.error(t('import.importStartFailed'))
      console.error('Failed to start import:', error)
    } finally {
      setLoading(false)
    }
  }

  // 轮询导入进度
  const pollProgress = async (taskId: string) => {
    const poll = async () => {
      try {
        const response = await importService.getProgress(taskId)
        const task = response.data.data

        console.log('Progress response:', response.data)
        console.log('Task data:', task)

        setCurrentTask({
          taskId: task.task_id,
          status: task.status,
          total: task.total,
          processed: task.processed,
          failed: task.failed,
          skipped: task.skipped,
          startTime: task.start_time,
          endTime: task.end_time,
        })

        if (task.status === 'completed' || task.status === 'failed') {
          message.success(task.status === 'completed' ? t('import.importCompleted') : t('import.importFailed'))
          loadImportTasks()
        } else {
          setTimeout(poll, 2000) // 2秒后继续轮询
        }
      } catch (error) {
        console.error('Failed to get progress:', error)
      }
    }

    poll()
  }

  // 加载导入任务列表
  const loadImportTasks = async () => {
    try {
      const response = await importService.getTasks()
      setImportTasks(response.data.data?.items || [])
      console.log('Import tasks response:', response.data)
    } catch (error) {
      console.error('Failed to load import tasks:', error)
    }
  }

  useEffect(() => {
    loadImportTasks()
  }, [])

  const getStatusTag = (status: string) => {
    const statusConfig = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: t('import.statusTags.pending') },
      running: { color: 'processing', icon: <ClockCircleOutlined />, text: t('import.statusTags.running') },
      completed: { color: 'success', icon: <CheckCircleOutlined />, text: t('import.statusTags.completed') },
      failed: { color: 'error', icon: <CheckCircleOutlined />, text: t('import.statusTags.failed') },
    }

    const config = statusConfig[status] || statusConfig.pending
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const previewColumns: ColumnsType<PreviewSession> = [
    {
      title: t('import.tableLabels.sessionId'),
      dataIndex: 'session_id',
      key: 'session_id',
      width: 200,
      render: (text) => <Text code style={{ fontSize: 12 }}>{text}</Text>,
    },
    {
      title: t('import.tableLabels.messageCount'),
      dataIndex: 'message_count',
      key: 'message_count',
      width: 100,
      render: (count) => <Tag color="blue">{count} {t('import.tableTags.messageUnit')}</Tag>,
    },
    {
      title: t('import.tableLabels.firstMessage'),
      dataIndex: 'first_message',
      key: 'first_message',
      ellipsis: true,
      render: (text) => (
        <Text title={text} style={{ maxWidth: 200 }}>
          {text}
        </Text>
      ),
    },
    {
      title: t('import.tableLabels.lastMessage'),
      dataIndex: 'last_message',
      key: 'last_message',
      ellipsis: true,
      render: (text) => (
        <Text title={text} style={{ maxWidth: 200 }}>
          {text}
        </Text>
      ),
    },
    {
      title: t('import.tableLabels.userRating'),
      dataIndex: 'has_user_rating',
      key: 'has_user_rating',
      width: 100,
      render: (hasRating) => (
        <Tag color={hasRating ? 'green' : 'default'}>
          {hasRating ? t('import.tableTags.rated') : t('import.tableTags.notRated')}
        </Tag>
      ),
    },
  ]

  const duplicateColumns: ColumnsType<DuplicateSessionInfo> = [
    {
      title: t('import.tableLabels.sessionId'),
      dataIndex: 'session_id',
      key: 'session_id',
      width: 200,
      render: (text) => <Text code style={{ fontSize: 12 }}>{text}</Text>,
    },
    {
      title: t('import.tableLabels.existingTestCase'),
      dataIndex: 'existing_test_case_name',
      key: 'existing_test_case_name',
      ellipsis: true,
      render: (text, record) => (
        <Space>
          <Text>{text}</Text>
          <Text type="secondary">({record.existing_test_case_id})</Text>
        </Space>
      ),
    },
    {
      title: t('import.tableColumns.owner'),
      dataIndex: 'owner',
      key: 'owner',
      width: 120,
    },
    {
      title: t('import.tableLabels.importDate'),
      dataIndex: 'import_date',
      key: 'import_date',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
  ]

  const taskColumns: ColumnsType<ImportTask> = [
    {
      title: t('import.tableColumns.taskId'),
      dataIndex: 'task_id',
      key: 'task_id',
      width: 200,
    },
    {
      title: t('import.tableColumns.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: t('import.tableColumns.total'),
      dataIndex: 'total',
      key: 'total',
      width: 80,
    },
    {
      title: t('import.tableColumns.processed'),
      dataIndex: 'processed',
      key: 'processed',
      width: 80,
    },
    {
      title: t('import.tableColumns.failed'),
      dataIndex: 'failed',
      key: 'failed',
      width: 80,
    },
    {
      title: t('import.tableColumns.skipped'),
      dataIndex: 'skipped',
      key: 'skipped',
      width: 80,
      render: (skipped) => skipped > 0 ? <Tag color="orange">{skipped}</Tag> : <Text type="secondary">0</Text>,
    },
    {
      title: t('import.tableColumns.startTime'),
      dataIndex: 'start_time',
      key: 'start_time',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
  ]

  const progressPercent = currentTask
    ? Math.round((currentTask.processed / currentTask.total) * 100)
    : 0

  return (
    <div>
      <Card className="page-header">
        <Title level={3} className="page-title">{t('import.title')}</Title>
        <Text className="page-description">
          {t('import.pageDescription')}
        </Text>
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <Steps current={currentStep} size="small">
          <Step title={t('import.steps.selectData')} description={t('import.steps.selectDataDesc')} />
          <Step title={t('import.steps.configImport')} description={t('import.steps.configImportDesc')} />
          <Step title={t('import.steps.executeImport')} description={t('import.steps.executeImportDesc')} />
        </Steps>
      </Card>

      {currentStep === 0 && (
        <Card>
          <Alert
            message={t('import.alert')}
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Button
            type="primary"
            icon={<ImportOutlined />}
            onClick={() => window.location.href = '/history'}
          >
            {t('import.goToHistory')}
          </Button>
        </Card>
      )}

      {currentStep === 1 && (
        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={4}>{t('import.config.title')}</Title>
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <div>
                    <Text strong>{t('import.config.ownerEmail')}</Text>
                    <Input
                      placeholder={t('import.config.ownerPlaceholder')}
                      style={{ width: '100%', marginTop: 8 }}
                      value={importConfig.defaultOwner}
                      onChange={(e) => setImportConfig(prev => ({ ...prev, defaultOwner: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Text strong>{t('import.config.defaultPriority')}</Text>
                    <Select
                      style={{ width: '100%', marginTop: 8 }}
                      value={importConfig.defaultPriority}
                      onChange={(value) => setImportConfig(prev => ({ ...prev, defaultPriority: value }))}
                      options={[
                        { label: t('priority.low'), value: 'low' },
                        { label: t('priority.medium'), value: 'medium' },
                        { label: t('priority.high'), value: 'high' },
                      ]}
                    />
                  </div>
                </Space>
              </Col>
              <Col span={12}>
                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                  <div>
                    <Text strong>{t('import.config.defaultDifficulty')}</Text>
                    <Select
                      style={{ width: '100%', marginTop: 8 }}
                      value={importConfig.defaultDifficulty}
                      onChange={(value) => setImportConfig(prev => ({ ...prev, defaultDifficulty: value }))}
                      options={[
                        { label: t('difficulty.easy'), value: 'easy' },
                        { label: t('difficulty.medium'), value: 'medium' },
                        { label: t('difficulty.hard'), value: 'hard' },
                      ]}
                    />
                  </div>
                  <div>
                    <Space direction="vertical">
                      <Text strong>{t('import.config.advancedOptions')}</Text>
                      <Checkbox
                        checked={importConfig.includeAnalysis}
                        onChange={(e) => setImportConfig(prev => ({ ...prev, includeAnalysis: e.target.checked }))}
                      >
                        {t('import.config.autoGenerateAnalysis')}
                      </Checkbox>
                    </Space>
                  </div>
                </Space>
              </Col>
            </Row>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Title level={4}>{t('import.preview.title')}</Title>
            <Text>{t('import.preview.selected', { count: sessionIds.length, max: Math.min(5, sessionIds.length) })}</Text>

            {previewData.length > 0 && (
              <Table
                columns={previewColumns}
                dataSource={previewData}
                rowKey="session_id"
                pagination={false}
                size="small"
                style={{ marginTop: 16 }}
              />
            )}
          </div>

          {/* 重复会话检测和处理选项 */}
          {validationResult && validationResult.duplicate_count > 0 && (
            <div style={{ marginBottom: 24 }}>
              <Title level={4}>
                <span style={{ color: '#faad14' }}>
                  <ExclamationCircleOutlined style={{ marginRight: 8 }} />
                  {t('import.duplicateDetection.title')}
                </span>
              </Title>

              {/* 概要信息 */}
              <Alert
                message={
                  <div>
                    <Text strong>
                      {translateWithValues('import.duplicateDetection.summary', {
                        total: validationResult.total_count,
                        duplicates: validationResult.duplicate_count,
                        new: validationResult.valid_sessions.length
                      })}
                    </Text>
                    <div style={{ marginTop: 8 }}>
                      <Text>
                        {translateWithValues('import.duplicateDetection.description', {
                          count: validationResult.duplicate_count
                        })}
                      </Text>
                    </div>
                  </div>
                }
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />

              {/* 导入选项 */}
              <div style={{
                backgroundColor: '#fffbe6',
                border: '1px solid #ffe58f',
                borderRadius: '6px',
                padding: '16px',
                marginBottom: 16
              }}>
                <Title level={5} style={{ margin: '0 0 12px 0', color: '#d48806' }}>
                  {t('import.importOptions.title')}
                </Title>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Checkbox
                    checked={importConfig.skipDuplicates}
                    onChange={(e) => setImportConfig(prev => ({ ...prev, skipDuplicates: e.target.checked }))}
                    style={{ fontSize: '14px' }}
                  >
                    <Text strong style={{ color: importConfig.skipDuplicates ? '#52c41a' : '#d48806' }}>
                      {importConfig.skipDuplicates
                        ? translateWithValues('import.importOptions.skipDuplicates', {
                            count: validationResult.valid_sessions.length
                          })
                        : translateWithValues('import.importOptions.importAllDuplicates', {
                            count: validationResult.total_count
                          })
                      }
                    </Text>
                  </Checkbox>
                  <Text type="secondary" style={{ fontSize: '12px', marginLeft: '24px' }}>
                    {importConfig.skipDuplicates
                      ? t('import.importOptions.skipDescription')
                      : t('import.importOptions.importAllDescription')
                    }
                  </Text>
                </Space>
              </div>

              {/* 重复会话详情 */}
              <div style={{ marginBottom: 16 }}>
                <Button
                  type="link"
                  size="small"
                  onClick={() => {
                    // Toggle detail visibility logic could be added here
                  }}
                >
                  {t('import.duplicateDetection.toggleDetails')} ({duplicateSessions.length})
                </Button>
              </div>

              <Table
                columns={duplicateColumns}
                dataSource={duplicateSessions}
                rowKey="session_id"
                pagination={false}
                size="small"
                style={{
                  backgroundColor: '#fafafa',
                  border: '1px solid #f0f0f0',
                  borderRadius: '6px'
                }}
              />
            </div>
          )}

          <Space>
            <Button
              type="primary"
              icon={<ImportOutlined />}
              onClick={handleStartImport}
              loading={loading}
              disabled={!importConfig.defaultOwner}
            >
              {validationResult && validationResult.duplicate_count > 0
                ? importConfig.skipDuplicates
                  ? translateWithValues('import.importOnlyNewButton', { count: validationResult.valid_sessions.length })
                  : translateWithValues('import.importAllButton', { count: validationResult.total_count })
                : translateWithValues('import.importAllButton', { count: sessionIds.length })
              }
            </Button>
            <Button onClick={() => setCurrentStep(0)}>
              {t('import.returnButton')}
            </Button>
          </Space>
        </Card>
      )}

      {currentStep === 2 && currentTask && (
        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={4}>{t('import.progress.title')}</Title>
            <div style={{ marginBottom: 16 }}>
              <Text>{t('import.progress.taskId')}{currentTask.taskId}</Text>
              <br />
              <Text>{t('import.progress.status')}{getStatusTag(currentTask.status)}</Text>
            </div>

            <Progress
              percent={progressPercent}
              status={currentTask.status === 'failed' ? 'exception' : 'active'}
              style={{ marginBottom: 16 }}
            />

            <Space>
              <Text>{t('import.progress.total')}{currentTask.total}</Text>
              <Text>{t('import.progress.processed')}{currentTask.processed}</Text>
              <Text>{t('import.progress.failed')}{currentTask.failed}</Text>
              {currentTask.skipped > 0 && (
                <Text type="warning">{t('import.progress.skipped')}{currentTask.skipped}</Text>
              )}
            </Space>
          </div>

          {(currentTask.status === 'completed' || currentTask.status === 'failed') && (
            <Space>
              <Button onClick={() => window.location.href = '/test-cases'}>
                {t('import.progress.viewTestCases')}
              </Button>
              <Button onClick={() => setCurrentStep(0)}>
                {t('import.progress.importMore')}
              </Button>
            </Space>
          )}
        </Card>
      )}

      <Card>
        <Title level={4}>{t('import.history.title')}</Title>
        <Table
          columns={taskColumns}
          dataSource={importTasks}
          rowKey="task_id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
        />
      </Card>
    </div>
  )
}

export default ImportPage