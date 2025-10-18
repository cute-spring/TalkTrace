import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Card,
  Steps,
  Button,
  Table,
  Space,
  Tag,
  Input,
  Select,
  message,
  Progress,
  Typography,
  Alert,
} from 'antd'
import { ImportOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons'
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

const ImportPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const [currentStep, setCurrentStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [sessionIds, setSessionIds] = useState<string[]>([])
  const [previewData, setPreviewData] = useState<SessionRecord[]>([])
  const [importTasks, setImportTasks] = useState<ImportTask[]>([])
  const [currentTask, setCurrentTask] = useState<ImportTask | null>(null)
  const [importConfig, setImportConfig] = useState({
    defaultOwner: '',
    defaultPriority: 'medium',
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
      const response = await importService.preview({ sessionIds: ids.slice(0, 5) })
      setPreviewData([]) // 简化版，不显示实际预览数据
      message.success('预览数据加载成功')
    } catch (error) {
      message.error('加载预览数据失败')
      console.error('Failed to load preview:', error)
    } finally {
      setLoading(false)
    }
  }

  // 开始导入
  const handleStartImport = async () => {
    if (!importConfig.defaultOwner) {
      message.error('请输入负责人邮箱')
      return
    }

    setLoading(true)
    try {
      const response = await importService.execute({
        sessionIds,
        ...importConfig,
      })

      setCurrentTask({
        taskId: response.data.taskId,
        status: 'running',
        total: sessionIds.length,
        processed: 0,
        failed: 0,
        startTime: new Date().toISOString(),
      })

      setCurrentStep(2)
      message.success('导入任务已开始')

      // 开始轮询进度
      pollProgress(response.data.taskId)
    } catch (error) {
      message.error('开始导入失败')
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
        const task = response.data

        setCurrentTask(task)

        if (task.status === 'completed' || task.status === 'failed') {
          message.success(task.status === 'completed' ? '导入完成' : '导入失败')
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
      setImportTasks(response.data.tasks)
    } catch (error) {
      console.error('Failed to load import tasks:', error)
    }
  }

  useEffect(() => {
    loadImportTasks()
  }, [])

  const getStatusTag = (status: string) => {
    const statusConfig = {
      pending: { color: 'default', icon: <ClockCircleOutlined />, text: '等待中' },
      running: { color: 'processing', icon: <ClockCircleOutlined />, text: '进行中' },
      completed: { color: 'success', icon: <CheckCircleOutlined />, text: '已完成' },
      failed: { color: 'error', icon: <CheckCircleOutlined />, text: '失败' },
    }

    const config = statusConfig[status] || statusConfig.pending
    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    )
  }

  const taskColumns: ColumnsType<ImportTask> = [
    {
      title: '任务ID',
      dataIndex: 'taskId',
      key: 'taskId',
      width: 200,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '总数',
      dataIndex: 'total',
      key: 'total',
      width: 80,
    },
    {
      title: '已处理',
      dataIndex: 'processed',
      key: 'processed',
      width: 80,
    },
    {
      title: '失败',
      dataIndex: 'failed',
      key: 'failed',
      width: 80,
    },
    {
      title: '开始时间',
      dataIndex: 'startTime',
      key: 'startTime',
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
        <Title level={3} className="page-title">数据导入</Title>
        <Text className="page-description">
          将选中的历史对话数据导入为标准化的测试用例
        </Text>
      </Card>

      <Card style={{ marginBottom: 16 }}>
        <Steps current={currentStep} size="small">
          <Step title="选择数据" description="从历史记录中选择要导入的会话" />
          <Step title="配置导入" description="设置导入参数和负责人" />
          <Step title="执行导入" description="处理数据并创建测试用例" />
        </Steps>
      </Card>

      {currentStep === 0 && (
        <Card>
          <Alert
            message="请先从历史记录页面选择要导入的会话数据"
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <Button
            type="primary"
            icon={<ImportOutlined />}
            onClick={() => window.location.href = '/history'}
          >
            前往历史记录页面
          </Button>
        </Card>
      )}

      {currentStep === 1 && (
        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={4}>导入配置</Title>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Text strong>负责人邮箱：</Text>
                <Input
                  placeholder="请输入负责人邮箱"
                  style={{ width: 300, marginLeft: 8 }}
                  value={importConfig.defaultOwner}
                  onChange={(e) => setImportConfig(prev => ({ ...prev, defaultOwner: e.target.value }))}
                />
              </div>
              <div>
                <Text strong>默认优先级：</Text>
                <Select
                  style={{ width: 200, marginLeft: 8 }}
                  value={importConfig.defaultPriority}
                  onChange={(value) => setImportConfig(prev => ({ ...prev, defaultPriority: value }))}
                  options={[
                    { label: '低', value: 'low' },
                    { label: '中', value: 'medium' },
                    { label: '高', value: 'high' },
                  ]}
                />
              </div>
            </Space>
          </div>

          <div style={{ marginBottom: 24 }}>
            <Title level={4}>预览数据</Title>
            <Text>已选择 {sessionIds.length} 条会话记录</Text>
          </div>

          <Space>
            <Button
              type="primary"
              icon={<ImportOutlined />}
              onClick={handleStartImport}
              loading={loading}
            >
              开始导入
            </Button>
            <Button onClick={() => setCurrentStep(0)}>
              返回选择
            </Button>
          </Space>
        </Card>
      )}

      {currentStep === 2 && currentTask && (
        <Card>
          <div style={{ marginBottom: 24 }}>
            <Title level={4}>导入进度</Title>
            <div style={{ marginBottom: 16 }}>
              <Text>任务ID：{currentTask.taskId}</Text>
              <br />
              <Text>状态：{getStatusTag(currentTask.status)}</Text>
            </div>

            <Progress
              percent={progressPercent}
              status={currentTask.status === 'failed' ? 'exception' : 'active'}
              style={{ marginBottom: 16 }}
            />

            <Space>
              <Text>总计：{currentTask.total}</Text>
              <Text>已处理：{currentTask.processed}</Text>
              <Text>失败：{currentTask.failed}</Text>
            </Space>
          </div>

          {(currentTask.status === 'completed' || currentTask.status === 'failed') && (
            <Space>
              <Button onClick={() => window.location.href = '/test-cases'}>
                查看测试用例
              </Button>
              <Button onClick={() => setCurrentStep(0)}>
                导入更多数据
              </Button>
            </Space>
          )}
        </Card>
      )}

      <Card>
        <Title level={4}>导入历史</Title>
        <Table
          columns={taskColumns}
          dataSource={importTasks}
          rowKey="taskId"
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