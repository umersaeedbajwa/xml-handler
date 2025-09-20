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
} from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { voicemailApi, domainApi } from '../../services/freeswitchApi';
import type { Voicemail, VoicemailCreate, VoicemailUpdate, Domain } from '../../types/freeswitch';

const { Title } = Typography;
const { Option } = Select;

const VoicemailManagement: React.FC = () => {
  const [voicemails, setVoicemails] = useState<Voicemail[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingVoicemail, setEditingVoicemail] = useState<Voicemail | null>(null);
  const [form] = Form.useForm();

  const fetchVoicemails = async () => {
    setLoading(true);
    try {
      const data = await voicemailApi.getAll();
      setVoicemails(data);
    } catch (error) {
      message.error('Failed to fetch voicemails');
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
    fetchVoicemails();
    fetchDomains();
  }, []);

  const handleCreateOrUpdate = async (values: VoicemailCreate | VoicemailUpdate) => {
    try {
      if (editingVoicemail) {
        await voicemailApi.update(editingVoicemail.voicemail_uuid, values as VoicemailUpdate);
        message.success('Voicemail updated successfully');
      } else {
        await voicemailApi.create(values as VoicemailCreate);
        message.success('Voicemail created successfully');
      }
      setModalVisible(false);
      setEditingVoicemail(null);
      form.resetFields();
      fetchVoicemails();
    } catch (error) {
      message.error(editingVoicemail ? 'Failed to update voicemail' : 'Failed to create voicemail');
    }
  };

  const handleDelete = async (uuid: string) => {
    try {
      await voicemailApi.delete(uuid);
      message.success('Voicemail deleted successfully');
      fetchVoicemails();
    } catch (error) {
      message.error('Failed to delete voicemail');
    }
  };

  const openModal = (voicemail?: Voicemail) => {
    setEditingVoicemail(voicemail || null);
    if (voicemail) {
      form.setFieldsValue(voicemail);
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
      title: 'Voicemail ID',
      dataIndex: 'voicemail_id',
      key: 'voicemail_id',
      sorter: (a: Voicemail, b: Voicemail) => a.voicemail_id.localeCompare(b.voicemail_id),
    },
    {
      title: 'Domain',
      dataIndex: 'domain_uuid',
      key: 'domain_uuid',
      render: (domainUuid: string) => getDomainName(domainUuid),
    },
    {
      title: 'Enabled',
      dataIndex: 'voicemail_enabled',
      key: 'voicemail_enabled',
      render: (enabled: string) => (
        <span style={{ color: enabled === 'true' ? '#52c41a' : '#ff4d4f' }}>
          {enabled === 'true' ? 'Enabled' : 'Disabled'}
        </span>
      ),
      filters: [
        { text: 'Enabled', value: 'true' },
        { text: 'Disabled', value: 'false' },
      ],
      onFilter: (value: boolean | React.Key, record: Voicemail) => record.voicemail_enabled === value,
    },
    {
      title: 'Email',
      dataIndex: 'voicemail_mail_to',
      key: 'voicemail_mail_to',
      render: (email: string) => email || '-',
    },
    {
      title: 'Attach File',
      dataIndex: 'voicemail_attach_file',
      key: 'voicemail_attach_file',
      render: (attach: string) => attach === 'true' ? 'Yes' : 'No',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: Voicemail) => (
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
            title="Are you sure you want to delete this voicemail?"
            onConfirm={() => handleDelete(record.voicemail_uuid)}
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
        <Title level={3}>Voicemail Management</Title>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openModal()}>
          Add Voicemail
        </Button>
      </div>

      <Table
        dataSource={voicemails}
        columns={columns}
        rowKey="voicemail_uuid"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} items`,
        }}
      />

      <Modal
        title={editingVoicemail ? 'Edit Voicemail' : 'Create Voicemail'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false);
          setEditingVoicemail(null);
          form.resetFields();
        }}
        onOk={() => form.submit()}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreateOrUpdate}
          initialValues={{ 
            voicemail_enabled: 'true',
            voicemail_attach_file: 'true',
            voicemail_local_after_email: 'true'
          }}
        >
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

          <Form.Item
            name="voicemail_id"
            label="Voicemail ID"
            rules={[
              { required: true, message: 'Please enter voicemail ID' },
              { pattern: /^\d+$/, message: 'Voicemail ID must be numeric' },
            ]}
          >
            <Input placeholder="e.g., 1001" />
          </Form.Item>

          <Form.Item
            name="voicemail_password"
            label="Voicemail Password"
            rules={[{ required: true, message: 'Please enter voicemail password' }]}
          >
            <Input.Password placeholder="Voicemail access password" />
          </Form.Item>

          <Form.Item
            name="voicemail_mail_to"
            label="Email Address"
            rules={[
              { type: 'email', message: 'Please enter a valid email address' }
            ]}
          >
            <Input placeholder="user@domain.com" />
          </Form.Item>

          <Form.Item
            name="voicemail_enabled"
            label="Enabled"
            rules={[{ required: true, message: 'Please select status' }]}
          >
            <Select>
              <Option value="true">Enabled</Option>
              <Option value="false">Disabled</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="voicemail_attach_file"
            label="Attach Audio File to Email"
          >
            <Select>
              <Option value="true">Yes</Option>
              <Option value="false">No</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="voicemail_local_after_email"
            label="Keep Local Copy After Email"
          >
            <Select>
              <Option value="true">Yes</Option>
              <Option value="false">No</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default VoicemailManagement;