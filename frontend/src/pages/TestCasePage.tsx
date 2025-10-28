import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
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
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { testCaseService } from '../services/api'
import TestCaseDetail from '../components/TestCaseDetail'

const { Title, Text } = Typography
const { Option } = Select
const { confirm } = Modal

  type TestStatus = 'draft' | 'pending_review' | 'approved' | 'published' | 'rejected'
  type PriorityLevel = 'low' | 'medium' | 'high'

  interface TestCase {
    id: string
    name: string
    description?: string
    status: TestStatus
    owner: string
    priority: PriorityLevel
    domain?: string
    difficulty?: string
    version: string
    created_date: string
    updated_date?: string
    tags: Array<{ name: string; color: string }>
  }

const TestCasePage: React.FC = () => {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()
  // removed unused navigate
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<any>(null)
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [currentTestCase, setCurrentTestCase] = useState<TestCase | null>(null)
  const [currentTestCaseId, setCurrentTestCaseId] = useState<string>('')
  const [form] = Form.useForm()

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

  // Initialize filters from URL parameters
  const [filters, setFilters] = useState({
    page: parseInt(searchParams.get('page') || '1'),
    pageSize: parseInt(searchParams.get('pageSize') || '10'),
    status: searchParams.get('status') || undefined,
    domain: searchParams.get('domain') || undefined,
    priority: searchParams.get('priority') || undefined,
    search: searchParams.get('search') || '',
  })

  // 获取测试用例列表
  const fetchTestCases = async () => {
    setLoading(true)
    try {
      // Debug: Log the current filters state
      console.log('Current filters state:', filters)

      // Convert frontend parameter names to backend parameter names without delete
      const { pageSize, ...restFilters } = filters
      const apiParams = {
        ...restFilters,
        page_size: pageSize, // Convert pageSize to page_size for backend
      }

      // Debug: Log the API parameters being sent
      console.log('API parameters being sent:', apiParams)

      const response = await testCaseService.getList(apiParams)
      console.log('API Response:', response)
      console.log('Response data:', response.data)
      console.log('Items:', response.data?.data?.items)
      console.log('Items length:', response.data?.data?.items?.length)
      // Fix: Access the nested data structure correctly
      setData(response.data.data)
    } catch (error) {
      message.error(t('testCases.fetchFailed'))
      console.error('Failed to fetch test cases:', error)
    } finally {
      setLoading(false)
    }
  }

  // Sync URL parameters with state
  useEffect(() => {
    const currentPage = parseInt(searchParams.get('page') || '1')
    const currentPageSize = parseInt(searchParams.get('pageSize') || '10')
    const currentStatus = searchParams.get('status') || undefined
    const currentDomain = searchParams.get('domain') || undefined
    const currentPriority = searchParams.get('priority') || undefined
    const currentSearch = searchParams.get('search') || ''

    setFilters({
      page: currentPage,
      pageSize: currentPageSize,
      status: currentStatus,
      domain: currentDomain,
      priority: currentPriority,
      search: currentSearch,
    })
  }, [searchParams])

  useEffect(() => {
    fetchTestCases()
  }, [filters])

  const handleSearch = () => {
    setFilters(prev => ({ ...prev, page: 1 }))

    // Update URL parameters
    const params = new URLSearchParams(searchParams)
    params.set('page', '1')
    if (filters.search) params.set('search', filters.search)
    if (filters.status) params.set('status', filters.status)
    if (filters.domain) params.set('domain', filters.domain)
    if (filters.priority) params.set('priority', filters.priority)
    if (filters.pageSize !== 20) params.set('pageSize', filters.pageSize.toString())
    setSearchParams(params)
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
      title: t('testCases.confirmDeleteTitle'),
      icon: <ExclamationCircleOutlined />,
      content: translateWithValues('testCases.confirmDeleteContent', { name: record.name }),
      onOk: async () => {
        try {
          await testCaseService.delete(record.id)
          message.success(t('testCases.deleteSuccess'))
          fetchTestCases()
        } catch (error) {
          message.error(t('testCases.deleteFailed'))
          console.error('Failed to delete test case:', error)
        }
      },
    })
  }

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning(t('validation.testCaseNameRequired'))
      return
    }

    confirm({
      title: t('testCases.batchDelete.title'),
      icon: <ExclamationCircleOutlined />,
      content: translateWithValues('testCases.batchDelete.confirm', { count: selectedRowKeys.length }),
      onOk: async () => {
        try {
          await testCaseService.batchOperation({
            action: 'delete',
            ids: selectedRowKeys,
          })
          message.success(t('testCases.batchDeleteSuccess'))
          setSelectedRowKeys([])
          fetchTestCases()
        } catch (error) {
          message.error(t('testCases.batchDeleteFailed'))
          console.error('Failed to batch delete:', error)
        }
      },
    })
  }

  const handleViewDetails = (record: TestCase) => {
    setCurrentTestCase(record)
    setCurrentTestCaseId(record.id)
    setDetailModalVisible(true)
  }

  const handleSubmit = async (values: any) => {
    if (!currentTestCase) return

    try {
      await testCaseService.update(currentTestCase.id, values)
      message.success(t('testCases.updateSuccess'))
      setEditModalVisible(false)
      fetchTestCases()
    } catch (error) {
      message.error(t('testCases.updateFailed'))
      console.error('Failed to update test case:', error)
    }
  }

  const getStatusTag = (status: TestStatus) => {
    const statusConfig: Record<TestStatus, { color: string; text: string }> = {
      draft: { color: 'default', text: t('status.draft') },
      pending_review: { color: 'processing', text: t('status.pending_review') },
      approved: { color: 'success', text: t('status.approved') },
      published: { color: 'success', text: t('status.published') },
      rejected: { color: 'error', text: t('status.rejected') },
    }

    const config = statusConfig[status] || statusConfig.draft
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const getPriorityTag = (priority: PriorityLevel) => {
    const priorityConfig: Record<PriorityLevel, { color: string; text: string }> = {
      low: { color: 'green', text: t('priority.low') },
      medium: { color: 'orange', text: t('priority.medium') },
      high: { color: 'red', text: t('priority.high') },
    }

    const config = priorityConfig[priority] || priorityConfig.medium
    return <Tag color={config.color}>{config.text}</Tag>
  }

  const columns: ColumnsType<TestCase> = [
    {
      title: t('testCases.columns.name'),
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Button type="link" onClick={() => handleViewDetails(record)}>
            {text}
          </Button>
        </Space>
      ),
    },
    {
      title: t('testCases.columns.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: TestStatus) => getStatusTag(status),
    },
    {
      title: t('testCases.columns.priority'),
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: PriorityLevel) => getPriorityTag(priority),
    },
    {
      title: t('testCases.columns.domain'),
      dataIndex: 'domain',
      key: 'domain',
      width: 100,
      render: (domain) => domain ? <Tag>{domain}</Tag> : '-',
    },
    {
      title: t('testCases.columns.difficulty'),
      dataIndex: 'difficulty',
      key: 'difficulty',
      width: 80,
      render: (difficulty) => difficulty ? <Tag>{difficulty}</Tag> : '-',
    },
    {
      title: t('testCases.columns.owner'),
      dataIndex: 'owner',
      key: 'owner',
      width: 200,
    },
    {
      title: t('testCases.columns.tags'),
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: TestCase['tags']) => (
        <Space wrap>
          {tags.map((tagItem: { name: string; color: string }, index: number) => (
            <Tag key={index} color={tagItem.color}>{tagItem.name}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: t('testCases.columns.createdTime'),
      dataIndex: 'created_date',
      key: 'created_date',
      width: 180,
      render: (time) => new Date(time).toLocaleString(),
    },
    {
      title: t('testCases.columns.actions'),
      key: 'actions',
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetails(record)}
          >
            {t('testCases.details')}
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            {t('testCases.edit')}
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record)}
          >
            {t('testCases.delete')}
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
        <Title level={3} className="page-title">{t('testCases.title')}</Title>
        <Text className="page-description">
          {t('testCases.pageDescription')}
        </Text>
      </Card>

      <Card className="search-form">
        <Space wrap size="middle">
          <Input
            placeholder={t('testCases.searchPlaceholder')}
            style={{ width: 250 }}
            value={filters.search}
            onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
          />

          <Select
            placeholder={t('testCases.columns.status')}
            style={{ width: 120 }}
            value={filters.status}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
            allowClear
          >
            <Option value="draft">{t('status.draft')}</Option>
            <Option value="pending_review">{t('status.pending_review')}</Option>
            <Option value="approved">{t('status.approved')}</Option>
            <Option value="published">{t('status.published')}</Option>
          </Select>

          <Select
            placeholder={t('testCases.columns.priority')}
            style={{ width: 100 }}
            value={filters.priority}
            onChange={(value) => setFilters(prev => ({ ...prev, priority: value }))}
            allowClear
          >
            <Option value="low">{t('priority.low')}</Option>
            <Option value="medium">{t('priority.medium')}</Option>
            <Option value="high">{t('priority.high')}</Option>
          </Select>

          <Select
            placeholder={t('testCases.columns.domain')}
            style={{ width: 120 }}
            value={filters.domain}
            onChange={(value) => setFilters(prev => ({ ...prev, domain: value }))}
            allowClear
          >
            <Option value="finance">{t('domain.finance')}</Option>
            <Option value="technology">{t('domain.technology')}</Option>
            <Option value="healthcare">{t('domain.healthcare')}</Option>
            <Option value="general">{t('domain.general')}</Option>
          </Select>

          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
          >
            {t('common.search')}
          </Button>
        </Space>

        {selectedRowKeys.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <Space>
              <Text style={{ fontWeight: 'bold' }}>
                {(() => {
                  const count = selectedRowKeys.length;
                  // Use the translateWithValues helper function
                  const translation = translateWithValues('testCases.selectedItems', { count });
                  // Double-check that interpolation worked
                  if (translation.includes('{count}')) {
                    // Fallback to manual interpolation
                    return `Selected ${count} item${count === 1 ? '' : 's'}`;
                  }
                  return translation;
                })()}
              </Text>
              <Button
                danger
                icon={<DeleteOutlined />}
                onClick={handleBatchDelete}
              >
                {t('testCases.batchDelete.title')}
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
              translateWithValues('common.page', { start: range[0], end: range[1], total: total }),
            onChange: (page, pageSize) => {
              const newPageSize = pageSize || 20
              setFilters(prev => ({ ...prev, page, pageSize: newPageSize }))

              // Update URL parameters
              const params = new URLSearchParams(searchParams)
              params.set('page', page.toString())
              params.set('pageSize', newPageSize.toString())
              setSearchParams(params)
            },
          }}
        />
      </Card>

      {/* 编辑模态框 */}
      <Modal
        title={t('testCases.editModal.title')}
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
            label={t('testCases.name')}
            name="name"
            rules={[{ required: true, message: t('testCases.editModal.nameRequired') }]}
          >
            <Input />
          </Form.Item>

          <Form.Item label={t('testCases.description')} name="description">
            <Input.TextArea rows={3} />
          </Form.Item>

          <Form.Item label={t('testCases.columns.status')} name="status">
            <Select>
              <Option value="draft">{t('status.draft')}</Option>
              <Option value="pending_review">{t('status.pending_review')}</Option>
              <Option value="approved">{t('status.approved')}</Option>
              <Option value="published">{t('status.published')}</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('testCases.columns.priority')} name="priority">
            <Select>
              <Option value="low">{t('priority.low')}</Option>
              <Option value="medium">{t('priority.medium')}</Option>
              <Option value="high">{t('priority.high')}</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('testCases.columns.domain')} name="domain">
            <Select allowClear>
              <Option value="finance">{t('domain.finance')}</Option>
              <Option value="technology">{t('domain.technology')}</Option>
              <Option value="healthcare">{t('domain.healthcare')}</Option>
              <Option value="general">{t('domain.general')}</Option>
            </Select>
          </Form.Item>

          <Form.Item label={t('testCases.columns.difficulty')} name="difficulty">
            <Select allowClear>
              <Option value="easy">{t('difficulty.easy')}</Option>
              <Option value="medium">{t('difficulty.medium')}</Option>
              <Option value="hard">{t('difficulty.hard')}</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title={t('testCases.detailDrawer.title')}
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={800}
      >
        {currentTestCase && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.name')}</Text>
              <Text>{currentTestCase.name}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.description')}</Text>
              <Text>{currentTestCase.description || t('testCaseDetail.noDescription')}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.status')}</Text>
              {getStatusTag(currentTestCase.status)}
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.priority')}</Text>
              {getPriorityTag(currentTestCase.priority)}
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.owner')}</Text>
              <Text>{currentTestCase.owner}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.createdTime')}</Text>
              <Text>{new Date(currentTestCase.created_date).toLocaleString()}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>{t('testCaseDetail.basicInfo.updatedTime')}</Text>
              <Text>{currentTestCase.updated_date ? new Date(currentTestCase.updated_date).toLocaleString() : '-'}</Text>
            </div>
          </div>
        )}
      </Drawer>

      {/* 详细信息模态框 */}
      <TestCaseDetail
        testCaseId={currentTestCaseId}
        visible={detailModalVisible}
        onClose={() => {
          setDetailModalVisible(false)
          setCurrentTestCaseId('')
        }}
      />
    </div>
  )
}

export default TestCasePage