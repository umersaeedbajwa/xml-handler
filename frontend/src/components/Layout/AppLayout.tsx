import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  Button,
  Avatar,
  Dropdown,
  Typography,
  Space,
  message,
} from 'antd';
import {
  DashboardOutlined,
  PhoneOutlined,
  LogoutOutlined,
  GlobalOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UserOutlined,
  SettingOutlined,
  MonitorOutlined,
  SoundOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAuthStore } from '../../store/authStore';
import { useTenantStore } from '../../store/tenantStore';
import TenantSelector from '../Common/TenantSelector';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const [tenantSelectorVisible, setTenantSelectorVisible] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuthStore();
  const { selectedTenant, clearSelectedTenant } = useTenantStore();

  const handleLogout = async () => {
    try {
      await logout();
      clearSelectedTenant(); // Clear tenant selection on logout
      message.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      clearSelectedTenant(); // Clear tenant selection even on error
      navigate('/login');
    }
  };


  const getCurrentMenuKey = () => {
    const path = location.pathname;
    
    if (path === '/dashboard') return 'dashboard';
    if (path === '/domains') return 'domains';
    if (path === '/extensions') return 'extensions';
    if (path === '/voicemails') return 'voicemails';
    return 'dashboard';
  };

  const menuItems: MenuProps['items'] = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
      onClick: () => navigate('/dashboard'),
    },
    {
      key: 'freeswitch',
      icon: <PhoneOutlined />,
      label: 'FreeSWITCH',
      children: [
        {
          key: 'domains',
          icon: <GlobalOutlined />,
          label: 'Domains',
          onClick: () => navigate('/domains'),
        },
        {
          key: 'extensions',
          icon: <TeamOutlined />,
          label: 'Extensions',
          onClick: () => navigate('/extensions'),
        },
        {
          key: 'voicemails',
          icon: <SoundOutlined />,
          label: 'Voicemails',
          onClick: () => navigate('/voicemails'),
        },
      ],
    },
  ];

  const getBreadcrumbText = () => {
    const path = location.pathname;
    if (path === '/dashboard') return 'Pages / Dashboard';
    if (path === '/domains') return 'FreeSWITCH / Domains';
    if (path === '/extensions') return 'FreeSWITCH / Extensions';
    if (path === '/voicemails') return 'FreeSWITCH / Voicemails';
    return 'Pages / Dashboard';
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'tenant-selector',
      icon: <GlobalOutlined />,
      label: selectedTenant ? `Current: ${selectedTenant.tenant_name}` : 'Select Tenant',
      onClick: () => setTenantSelectorVisible(true),
    },
    {
      type: 'divider',
    },
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Fixed Sidebar */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        width={250}
        style={{
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          bottom: 0,
          zIndex: 100,
          background: '#001529',
        }}
      >
        {/* Logo/Brand */}
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: '#002140',
            borderBottom: '1px solid #303030',
          }}
        >
          {!collapsed ? (
            <Space>
              <div
                style={{
                  width: 32,
                  height: 32,
                  background: '#1890ff',
                  borderRadius: 8,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Text style={{ color: 'white', fontWeight: 'bold' }}>XH</Text>
              </div>
              <Text style={{ color: 'white', fontWeight: 'bold', fontSize: 16 }}>
                XML Handler
              </Text>
            </Space>
          ) : (
            <div
              style={{
                width: 32,
                height: 32,
                background: '#1890ff',
                borderRadius: 8,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Text style={{ color: 'white', fontWeight: 'bold' }}>CT</Text>
            </div>
          )}
        </div>

        {/* Navigation Menu */}
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[getCurrentMenuKey()]}
          items={menuItems}
          style={{
            height: 'calc(100% - 64px)',
            borderRight: 0,
            background: '#001529',
          }}
        />
      </Sider>

      {/* Main Layout */}
      <Layout style={{ marginLeft: collapsed ? 80 : 250, transition: 'margin-left 0.2s' }}>
        {/* Top Navigation Bar (Not Fixed) */}
        <Header
          style={{
            padding: '0 24px',
            background: '#fff',
            borderBottom: '1px solid #f0f0f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          {/* Left side - Collapse button and breadcrumb */}
          <Space>
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: '16px',
                width: 40,
                height: 40,
              }}
            />
            <div>
              <Text type="secondary" style={{ fontSize: 12 }}>
                {selectedTenant?.tenant_name} / {getBreadcrumbText()}
              </Text>
            </div>
          </Space>

          {/* Right side - Search, notifications, user */}
          <Space size="middle">
            {/* <Input
              placeholder="Type here..."
              prefix={<SearchOutlined />}
              style={{
                width: 200,
                borderRadius: 20,
              }}
            />
            
            <Button
              type="text"
              style={{
                background: '#e6f7ff',
                color: '#1890ff',
                borderRadius: 8,
                fontSize: 12,
                height: 32,
              }}
            >
              Online Builder
            </Button>

            <Badge count={0}>
              <Button
                type="text"
                icon={<StarOutlined />}
                style={{ fontSize: 16 }}
              />
            </Badge>
            
            <Text style={{ fontSize: 14 }}>11,156</Text>

            <Badge dot>
              <Button
                type="text"
                icon={<BellOutlined />}
                style={{ fontSize: 16 }}
              />
            </Badge>

            <Button
              type="text"
              icon={<SettingOutlined />}
              style={{ fontSize: 16 }}
            /> */}

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Avatar
                style={{ backgroundColor: '#1890ff', cursor: 'pointer' }}
                icon={<UserOutlined />}
              />
            </Dropdown>
          </Space>
        </Header>

        {/* Main Content */}
        <Content
          style={{
            margin: 0,
            padding: 24,
            background: '#f5f5f5',
            minHeight: 'calc(100vh - 64px)',
          }}
        >
          {children}
        </Content>
      </Layout>

      {/* Tenant Selector Modal */}
      <TenantSelector
        visible={tenantSelectorVisible}
        onClose={() => setTenantSelectorVisible(false)}
      />
    </Layout>
  );
};

export default AppLayout;
