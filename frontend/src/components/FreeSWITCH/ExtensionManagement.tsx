import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Space,
  Popconfirm,
  message,
  Card,
  Typography,
  Switch,
  Row,
  Col,
  Divider
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, SettingOutlined } from '@ant-design/icons';
import { extensionApi, domainApi } from '../../services/freeswitchApi';
import type { Extension, ExtensionCreate, Domain } from '../../types/freeswitch';

const { Title } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const ExtensionManagement: React.FC = () => {
  const [extensions, setExtensions] = useState<Extension[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingExtension, setEditingExtension] = useState<Extension | null>(null);
  const [form] = Form.useForm();

  const fetchExtensions = async () => {
    setLoading(true);
    try {
      const data = await extensionApi.getAll();
      setExtensions(data);
    } catch (error) {
      message.error('Failed to fetch extensions');
    } finally {
      setLoading(false);
    }
  };

  const fetchDomains = async () => {
    try {
      const data = await domainApi.getAll();
      setDomains(data);
    } catch (error) {
      message.error('Failed to fetch domains');
    }
  };

  useEffect(() => {
    fetchExtensions();
    fetchDomains();
  }, []);

  const handleCreateOrUpdate = async (values: ExtensionCreate) => {
    try {
      // Clean up empty string values
      const cleanValues = Object.fromEntries(
        Object.entries(values).filter(([_, value]) => value !== '' && value !== undefined)
      );

      if (editingExtension) {
        await extensionApi.update(editingExtension.extension_uuid, cleanValues);
        message.success('Extension updated successfully');
      } else {
        await extensionApi.create(cleanValues as ExtensionCreate);
        message.success('Extension created successfully');
      }
      setModalVisible(false);
      setEditingExtension(null);
      form.resetFields();
      fetchExtensions();
    } catch (error) {
      message.error(editingExtension ? 'Failed to update extension' : 'Failed to create extension');
    }
  };

  const handleDelete = async (uuid: string) => {
    try {
      await extensionApi.delete(uuid);
      message.success('Extension deleted successfully');
      fetchExtensions();
    } catch (error) {
      message.error('Failed to delete extension');
    }
  };

  const openModal = (extension?: Extension) => {
    setEditingExtension(extension || null);
    if (extension) {
      // Convert boolean-like strings to boolean values for Switch components
      const formValues = { ...extension };
      form.setFieldsValue(formValues);
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  const getDomainName = (domainUuid: string) => {
    const domain = domains.find(d => d.domain_uuid === domainUuid);
    return domain?.domain_name || 'Unknown Domain';
  };

  const columns = [
    {
      title: 'Extension',
      dataIndex: 'extension',
      key: 'extension',
      sorter: (a: Extension, b: Extension) => a.extension.localeCompare(b.extension),
    },
    {
      title: 'Domain',
      dataIndex: 'domain_uuid',
      key: 'domain_uuid',
      render: (domainUuid: string) => getDomainName(domainUuid),
    },
    {
      title: 'Type',
      dataIndex: 'extension_type',
      key: 'extension_type',
      render: (type: string) => type || 'N/A',
    },
    {
      title: 'Enabled',
      dataIndex: 'enabled',
      key: 'enabled',
      render: (enabled: string) => (
        <span style={{ color: enabled === 'true' ? '#52c41a' : '#ff4d4f' }}>
          {enabled === 'true' ? 'Enabled' : 'Disabled'}
        </span>
      ),
      filters: [
        { text: 'Enabled', value: 'true' },
        { text: 'Disabled', value: 'false' },
      ],
      onFilter: (value: boolean | React.Key, record: Extension) => record.enabled === value,
    },
    {
      title: 'First Name',
      dataIndex: 'directory_first_name',
      key: 'directory_first_name',
      render: (name: string) => name || '-',
    },
    {
      title: 'Last Name',
      dataIndex: 'directory_last_name',
      key: 'directory_last_name',
      render: (name: string) => name || '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Extension) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<EditOutlined />}
            onClick={() => openModal(record)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Are you sure you want to delete this extension?"
            onConfirm={() => handleDelete(record.extension_uuid)}
            okText="Yes"
            cancelText="No"
          >
            <Button type="primary" danger size="small" icon={<DeleteOutlined />}>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Card>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={3}>Extension Management</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
          Add Extension
        </Button>
      </div>

      <Table
        dataSource={extensions}
        columns={columns}
        rowKey="extension_uuid"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
        }}
        scroll={{ x: 1200 }}
      />

      <Modal
        title={editingExtension ? 'Edit Extension' : 'Create Extension'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingExtension(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        destroyOnClose
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrUpdate}
          initialValues={{ 
            enabled: 'true',
            extension_type: 'fixed',
            directory_visible: 'true',
            directory_exten_visible: 'true'
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="domain_uuid"
                label="Domain"
                rules={[{ required: true, message: 'Please select a domain' }]}
              >
                <Select placeholder="Select domain">
                  {domains.map(domain => (
                    <Option key={domain.domain_uuid} value={domain.domain_uuid}>
                      {domain.domain_name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="extension"
                label="Extension Number"
                rules={[
                  { required: true, message: 'Please enter extension number' },
                  { pattern: /^\d+$/, message: 'Extension must be numeric' },
                ]}
              >
                <Input placeholder="e.g., 1001" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="number_alias" label="Number Alias">
                <Input placeholder="Alternative number" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="extension_type" label="Extension Type">
                <Select>
                  <Option value="fixed">Fixed</Option>
                  <Option value="dynamic">Dynamic</Option>
                  <Option value="gateway">Gateway</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="password" label="Password">
                <Input.Password placeholder="SIP password" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="enabled" label="Enabled">
                <Select>
                  <Option value="true">Enabled</Option>
                  <Option value="false">Disabled</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>Directory Information</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="directory_first_name" label="First Name">
                <Input placeholder="First name" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="directory_last_name" label="Last Name">
                <Input placeholder="Last name" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="directory_visible" label="Directory Visible">
                <Select>
                  <Option value="true">Visible</Option>
                  <Option value="false">Hidden</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="directory_exten_visible" label="Extension Visible">
                <Select>
                  <Option value="true">Visible</Option>
                  <Option value="false">Hidden</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Divider>Caller ID</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="effective_caller_id_name" label="Effective Caller ID Name">
                <Input placeholder="Caller ID name" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="effective_caller_id_number" label="Effective Caller ID Number">
                <Input placeholder="Caller ID number" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="outbound_caller_id_name" label="Outbound Caller ID Name">
                <Input placeholder="Outbound caller ID name" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="outbound_caller_id_number" label="Outbound Caller ID Number">
                <Input placeholder="Outbound caller ID number" />
              </Form.Item>
            </Col>
          </Row>

          <Divider>Advanced Settings</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="call_timeout" label="Call Timeout">
                <Input placeholder="Timeout in seconds" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="max_registrations" label="Max Registrations">
                <Input placeholder="Maximum registrations" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="dial_string" label="Dial String">
            <TextArea placeholder="Custom dial string" rows={2} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default ExtensionManagement;