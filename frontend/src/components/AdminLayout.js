import React, { useState } from 'react';
import { Layout, Menu, Breadcrumb, Avatar } from 'antd';
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  DashboardOutlined,
  TeamOutlined,
  EnvironmentOutlined,
  CalendarOutlined,
  BarChartOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import Logo from './Logo';

const { Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

const AdminLayout = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getBreadcrumbItems = () => {
    const pathSnippets = location.pathname.split('/').filter((i) => i);
    const breadcrumbItems = pathSnippets.map((snippet, index) => {
      const url = `/${pathSnippets.slice(0, index + 1).join('/')}`;
      return (
        <Breadcrumb.Item key={url}>
          <Link to={url}>{snippet.charAt(0).toUpperCase() + snippet.slice(1)}</Link>
        </Breadcrumb.Item>
      );
    });
    return [
      <Breadcrumb.Item key="admin">
        <Link to="/admin">Admin</Link>
      </Breadcrumb.Item>,
      ...breadcrumbItems,
    ];
  };

  if (!user || user.role !== 'admin') {
    return <div>Loading... or Access Denied</div>;
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{
          overflow: 'auto',
          height: '100vh',
          position: 'fixed',
          left: 0,
          top: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Logo collapsed={collapsed} />
        <Menu theme="dark" defaultSelectedKeys={[location.pathname]} mode="inline" style={{ flex: 1, paddingBottom: '48px' }}>
          <Menu.Item key="/admin" icon={<DashboardOutlined />}>
            <Link to="/admin">Dashboard</Link>
          </Menu.Item>
          <Menu.Item key="/admin/venues" icon={<EnvironmentOutlined />}>
            <Link to="/admin/venues">Venue Management</Link>
          </Menu.Item>
          <Menu.Item key="/admin/users" icon={<TeamOutlined />}>
            <Link to="/admin/users">User Management</Link>
          </Menu.Item>
          <Menu.Item key="/admin/reservations" icon={<CalendarOutlined />}>
            <Link to="/admin/reservations">Reservation Management</Link>
          </Menu.Item>
          <Menu.Item key="/admin/statistics" icon={<BarChartOutlined />}>
            <Link to="/admin/statistics">Statistics</Link>
          </Menu.Item>
        </Menu>
        <Menu theme="dark" mode="inline" selectable={false} style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <SubMenu 
            key="user" 
            icon={<Avatar icon={<UserOutlined />} />} 
            title={user.username}
          >
            <Menu.Item key="profile" icon={<UserOutlined />}>
              <Link to="/admin/profile">Profile</Link>
            </Menu.Item>
            <Menu.Item key="settings" icon={<SettingOutlined />}>
              <Link to="/admin/settings">Settings</Link>
            </Menu.Item>
            <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
              Logout
            </Menu.Item>
          </SubMenu>
        </Menu>
      </Sider>
      <Layout className="site-layout" style={{ marginLeft: collapsed ? 80 : 200, transition: 'all 0.2s' }}>
        <Content style={{ margin: '0 16px' }}>
          <Breadcrumb style={{ margin: '16px 0' }}>
            {getBreadcrumbItems()}
          </Breadcrumb>
          <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>Fitness Reservation System ©2024</Footer>
      </Layout>
    </Layout>
  );
};

export default AdminLayout;