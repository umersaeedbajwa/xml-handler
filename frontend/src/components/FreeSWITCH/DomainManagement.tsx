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
  Typography
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { domainApi } from '../../services/freeswitchApi';
import type { Domain, DomainCreate, DomainUpdate } from '../../types/freeswitch';

const { Title } = Typography;
const { Option } = Select;

const DomainManagement: React.FC = () => {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingDomain, setEditingDomain] = useState<Domain | null>(null);
  const [form] = Form.useForm();

  const fetchDomains = async () => {
    setLoading(true);
    try {
      const data = await domainApi.getAll();
      setDomains(data);
    } catch (error) {
      message.error('Failed to fetch domains');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomains();
  }, []);

  const handleCreateOrUpdate = async (values: DomainCreate | DomainUpdate) => {
    try {
      if (editingDomain) {
        await domainApi.update(editingDomain.domain_uuid, values as DomainUpdate);
        message.success('Domain updated successfully');
      } else {
        await domainApi.create(values as DomainCreate);
        message.success('Domain created successfully');
      }
      setModalVisible(false);
      setEditingDomain(null);
      form.resetFields();
      fetchDomains();
    } catch (error) {
      message.error(editingDomain ? 'Failed to update domain' : 'Failed to create domain');
    }
  };

  const handleDelete = async (uuid: string) => {
    try {
      await domainApi.delete(uuid);
      message.success('Domain deleted successfully');
      fetchDomains();
    } catch (error) {
      message.error('Failed to delete domain');
    }
  };

  const openModal = (domain?: Domain) => {
    setEditingDomain(domain || null);
    if (domain) {
      form.setFieldsValue(domain);
    } else {
      form.resetFields();
    }
    setModalVisible(true);
  };

  const columns = [
    {
      title: 'Domain Name',
      dataIndex: 'domain_name',
      key: 'domain_name',
      sorter: (a: Domain, b: Domain) => a.domain_name.localeCompare(b.domain_name),
    },
    {
      title: 'Enabled',
      dataIndex: 'domain_enabled',
      key: 'domain_enabled',
      render: (enabled: string) => (
        <span style={{ color: enabled === 'true' ? '#52c41a' : '#ff4d4f' }}>
          {enabled === 'true' ? 'Enabled' : 'Disabled'}
        </span>
      ),
      filters: [
        { text: 'Enabled', value: 'true' },
        { text: 'Disabled', value: 'false' },
      ],
      onFilter: (value: boolean | React.Key, record: Domain) => record.domain_enabled === value,
    },
    {
      title: 'Created At',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => date ? new Date(date).toLocaleDateString() : '-',
      sorter: (a: Domain, b: Domain) => {
        const dateA = a.created_at ? new Date(a.created_at).getTime() : 0;
        const dateB = b.created_at ? new Date(b.created_at).getTime() : 0;
        return dateA - dateB;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Domain) => (
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
            title="Are you sure you want to delete this domain?"
            onConfirm={() => handleDelete(record.domain_uuid)}
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
        <Title level={3}>Domain Management</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
          Add Domain
        </Button>
      </div>

      <Table
        dataSource={domains}
        columns={columns}
        rowKey="domain_uuid"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
        }}
      />

      <Modal
        title={editingDomain ? 'Edit Domain' : 'Create Domain'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingDomain(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrUpdate}
          initialValues={{ domain_enabled: 'true' }}
        >
          <Form.Item
            name="domain_name"
            label="Domain Name"
            rules={[
              { required: true, message: 'Please enter domain name' },
              { pattern: /^[a-zA-Z0-9.-]+$/, message: 'Invalid domain name format' },
            ]}
          >
            <Input placeholder="e.g., example.com" />
          </Form.Item>

          <Form.Item
            name="domain_enabled"
            label="Status"
            rules={[{ required: true, message: 'Please select status' }]}
          >
            <Select>
              <Option value="true">Enabled</Option>
              <Option value="false">Disabled</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default DomainManagement;