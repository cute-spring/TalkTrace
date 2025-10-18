import { useState, useEffect } from 'react'
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Modal,
  Form,
  message,
  Typography,
  Drawer,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { testCaseService } from '../services/api'

const { Title, Text } = Typography
const { Option } = Select
const { confirm } = Modal

interface TestCase {
  id: string
  name: string
  description?: string
  status: string
  owner: string
  priority: string
  domain?: string
  difficulty?: string
  version: string
  createdDate: string
  updatedDate: string
  tags: Array<{ tag: { name: string; color: string } }>
}

const TestCasePage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [currentTestCase, setCurrentTestCase] = useState<TestCase | null>(null)
  const [form] = Form.useForm()

  const [filters, setFilters] = useState({
    page: 1,
    pageSize: 20,
    status: undefined,
    domain: undefined,
    priority: undefined,
    search: '',
  })

  // 获取测试用例列表
  const fetchTestCases = async () => {
    setLoading(true)
    try {
      const response = await testCaseService.getList(filters)
      setData(response.data)
    } catch (error) {
      message.error('获取测试用例列表失败')
      console.error('Failed to fetch test cases:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchTestCases()
  }, [filters])

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 1 }))
    fetchTestCases()
  }

  const handleEdit = (record: TestCase) => {
    setCurrentTestCase(record)
    form.setFieldsValue({
      name: record.name,
      description: record.description,
      status: record.status,
      priority: record.priority,
      domain: record.domain,
      difficulty: record.difficulty,
    })
    setEditModalVisible(true)
  }

  const handleDelete = (record: TestCase) => {
    confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除测试用例"${record.name}"吗？`,
      onOk: async () => {
        try {
          await testCaseService.delete(record.id)
          message.success('删除成功')
          fetchTestCases()
        } catch (error) {
          message.error('删除失败')
          console.error('Failed to delete test case:', error)
        }
      },
    })
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的测试用例')
      return
    }

    confirm({
      title: '批量删除',
      icon: <ExclamationCircleOutlined />,
      content: `确定要删除选中的 ${selectedRowKeys.length} 个测试用例吗？`,
      onOk: async () => {
        try {
          await testCaseService.batchOperation({
            action: 'delete',
            ids: selectedRowKeys,
          })
          message.success('批量删除成功')
          setSelectedRowKeys([])
          fetchTestCases()
        } catch (error) {
          message.error('批量删除失败')
          console.error('Failed to batch delete:', error)
        }
      },
    })
  }

  const handleViewDetails = (record: TestCase) => {
    setCurrentTestCase(record)
    setDetailDrawerVisible(true)
  }

  const handleSubmit = async (values: any) => {
    if (!currentTestCase) return

    try {
      await testCaseService.update(currentTestCase.id, values)
      message.success('更新成功')
      setEditModalVisible(false)
      fetchTestCases()
    } catch (error) {
      message.error('更新失败')
      console.error('Failed to update test case:', error)
    }
  }

  const getStatusTag = (status: string) => {
    const statusConfig = {
      draft: { color: 'default', text: '草稿' },
      pending_review: { color: 'processing', text: '待审核' },
      approved: { color: 'success', text: '已审核' },
      published: { color: 'success', text: '已发布' },
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

  const columns: ColumnsType<TestCase> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Button type="link" onClick={() => handleViewDetails(record)}>
          {text}
        </Button>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => getStatusTag(status),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority) => getPriorityTag(priority),
    },
    {
      title: '领域',
      dataIndex: 'domain',
      key: 'domain',
      width: 100,
      render: (domain) => domain ? <Tag>{domain}</Tag> : '-',
    },
    {
      title: '难度',
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 80,
      render: (difficulty) => difficulty ? <Tag>{difficulty}</Tag> : '-',
    },
    {
      title: '负责人',
      dataIndex: 'owner',
      key: 'owner',
      width: 200,
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags) => (
        <Space wrap>
          {tags.map((tagItem, index) => (
            <Tag key={index} color={tagItem.tag.color}>
              {tagItem.tag.name}
            </Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'createdDate',
      key: 'createdDate',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            删除
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
        <Title level={3} className="page-title">测试用例管理</Title>
        <Text className="page-description">
          管理和编辑从历史记录导入的测试用例
        </Text>
      </Card>

      <Card className="search-form">
        <Space wrap size="middle">
          <Input
            placeholder="搜索测试用例"
            style={{ width: 250 }}
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
          />

          <Select
            placeholder="状态"
            style={{ width: 120 }}
            value={filters.status}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
            allowClear
          >
            <Option value="draft">草稿</Option>
            <Option value="pending_review">待审核</Option>
            <Option value="approved">已审核</Option>
            <Option value="published">已发布</Option>
          </Select>

          <Select
            placeholder="优先级"
            style={{ width: 100 }}
            value={filters.priority}
            onChange={(value) => setFilters(prev => ({ ...prev, priority: value }))}
            allowClear
          >
            <Option value="low">低</Option>
            <Option value="medium">中</Option>
            <Option value="high">高</Option>
          </Select>

          <Select
            placeholder="领域"
            style={{ width: 120 }}
            value={filters.domain}
            onChange={(value) => setFilters(prev => ({ ...prev, domain: value }))}
            allowClear
          >
            <Option value="finance">金融</Option>
            <Option value="technology">技术</Option>
            <Option value="healthcare">医疗</Option>
            <Option value="general">通用</Option>
          </Select>

          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
          >
            搜索
          </Button>
        </Space>

        {selectedRowKeys.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Space>
              <Text>已选择 {selectedRowKeys.length} 项</Text>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={handleBatchDelete}
              >
                批量删除
              </Button>
            </Space>
          </div>
        )}
      </Card>

      <Card className="content-card">
        <Table
          columns={columns}
          dataSource={data?.items || []}
          rowKey="id"
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

      {/* 编辑模态框 */}
      <Modal
        title="编辑测试用例"
        open={editModalVisible}
        onCancel={() => setEditModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
        >
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: '请输入测试用例名称' }]}
          >
            <Input />
          </Form.Item>

          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item label="状态" name="status">
            <Select>
              <Option value="draft">草稿</Option>
              <Option value="pending_review">待审核</Option>
              <Option value="approved">已审核</Option>
              <Option value="published">已发布</Option>
            </Select>
          </Form.Item>

          <Form.Item label="优先级" name="priority">
            <Select>
              <Option value="low">低</Option>
              <Option value="medium">中</Option>
              <Option value="high">高</Option>
            </Select>
          </Form.Item>

          <Form.Item label="领域" name="domain">
            <Select allowClear>
              <Option value="finance">金融</Option>
              <Option value="technology">技术</Option>
              <Option value="healthcare">医疗</Option>
              <Option value="general">通用</Option>
            </Select>
          </Form.Item>

          <Form.Item label="难度" name="difficulty">
            <Select allowClear>
              <Option value="easy">简单</Option>
              <Option value="medium">中等</Option>
              <Option value="hard">困难</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title="测试用例详情"
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={800}
      >
        {currentTestCase && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>名称：</Text>
              <Text>{currentTestCase.name}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>描述：</Text>
              <Text>{currentTestCase.description || '无'}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>状态：</Text>
              {getStatusTag(currentTestCase.status)}
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>优先级：</Text>
              {getPriorityTag(currentTestCase.priority)}
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>负责人：</Text>
              <Text>{currentTestCase.owner}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>创建时间：</Text>
              <Text>{new Date(currentTestCase.createdDate).toLocaleString()}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>更新时间：</Text>
              <Text>{new Date(currentTestCase.updatedDate).toLocaleString()}</Text>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  )
}

export default TestCasePage