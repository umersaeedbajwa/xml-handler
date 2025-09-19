import React, { useEffect, useState } from 'react';
import { Modal, Select, Button, Space, Typography, Spin, Alert } from 'antd';
import { GlobalOutlined } from '@ant-design/icons';
import { useTenantStore, type Tenant } from '../../store/tenantStore';

const { Text } = Typography;
const { Option } = Select;

interface TenantSelectorProps {
  visible: boolean;
  onClose: () => void;
}

const TenantSelector: React.FC<TenantSelectorProps> = ({ visible, onClose }) => {
  const { 
    tenants, 
    selectedTenant, 
    loading, 
    error, 
    fetchTenants, 
    setSelectedTenant 
  } = useTenantStore();
  
  const [tempSelectedTenant, setTempSelectedTenant] = useState<Tenant | null>(null);

  useEffect(() => {
    if (visible) {
      fetchTenants();
      setTempSelectedTenant(selectedTenant);
    }
  }, [visible, fetchTenants, selectedTenant]);

  const handleSave = () => {
    if (tempSelectedTenant) {
      setSelectedTenant(tempSelectedTenant);
      onClose();
      // Reload the page to apply tenant context
      window.location.reload();
    }
  };

  const handleCancel = () => {
    setTempSelectedTenant(selectedTenant);
    onClose();
  };

  return (
    <Modal
      title={
        <Space>
          <GlobalOutlined />
          <span>Select Tenant</span>
        </Space>
      }
      open={visible}
      onCancel={handleCancel}
      footer={[
        <Button key="cancel" onClick={handleCancel}>
          Cancel
        </Button>,
        <Button 
          key="save" 
          type="primary" 
          onClick={handleSave}
          disabled={!tempSelectedTenant}
        >
          Save & Reload
        </Button>
      ]}
      width={500}
    >
      <div style={{ padding: '16px 0' }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <Spin size="large" />
            <div style={{ marginTop: 16 }}>
              <Text>Loading tenants...</Text>
            </div>
          </div>
        ) : error ? (
          <Alert
            message="Error"
            description={error}
            type="error"
            showIcon
            style={{ marginBottom: 16 }}
          />
        ) : (
          <>
            <div style={{ marginBottom: 16 }}>
              <Text type="secondary">
                Select a tenant to switch context. This will reload the application.
              </Text>
            </div>
            
            <div style={{ marginBottom: 16 }}>
              <Text strong>Current Tenant:</Text>
              <div style={{ marginTop: 8 }}>
                {selectedTenant ? (
                  <Text>
                    {selectedTenant.tenant_name} (ID: {selectedTenant.tenant_id})
                  </Text>
                ) : (
                  <Text type="secondary">No tenant selected</Text>
                )}
              </div>
            </div>

            <div>
              <Text strong>Select New Tenant:</Text>
              <Select
                style={{ width: '100%', marginTop: 8 }}
                placeholder="Choose a tenant"
                value={tempSelectedTenant?.tenant_id}
                onChange={(value) => {
                  const tenant = tenants.find(t => t.tenant_id === value);
                  setTempSelectedTenant(tenant || null);
                }}
                optionFilterProp="children"
                showSearch
                filterOption={(input, option) =>
                  (option?.children as unknown as string)
                    ?.toLowerCase()
                    ?.includes(input.toLowerCase())
                }
              >
                {tenants.map((tenant) => (
                  <Option key={tenant.tenant_id} value={tenant.tenant_id}>
                    <div>
                      <div>{tenant.tenant_name} - {tenant.description && (
                        <span style={{ fontSize: 12 }}>
                          {tenant.description}
                        </span>
                      )} 
                      </div>
                      
                    </div>
                  </Option>
                ))}
              </Select>
            </div>
          </>
        )}
      </div>
    </Modal>
  );
};

export default TenantSelector;
