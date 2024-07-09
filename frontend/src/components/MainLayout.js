import React, { useState } from 'react';
import { Layout, Menu, Breadcrumb, Avatar } from 'antd';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  HomeOutlined,
  CalendarOutlined,
  BarChartOutlined,
  MessageOutlined,
  LogoutOutlined,
  UserOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { logout, getCurrentUser } from '../services/auth';
import Logo from './Logo';

const { Content, Footer, Sider } = Layout;
const { SubMenu } = Menu;

const MainLayout = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const currentUser = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate('/');
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
      <Breadcrumb.Item key="home">
        <Link to="/dashboard">Home</Link>
      </Breadcrumb.Item>,
      ...breadcrumbItems,
    ];
  };

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
          <Menu.Item key="/dashboard" icon={<HomeOutlined />}>
            <Link to="/dashboard">Dashboard</Link>
          </Menu.Item>
          <Menu.Item key="/venues" icon={<CalendarOutlined />}>
            <Link to="/venues">Venues</Link>
          </Menu.Item>
          <Menu.Item key="/reservations" icon={<CalendarOutlined />}>
            <Link to="/reservations">Reservations</Link>
          </Menu.Item>
          {currentUser.role === 'admin' && (
            <Menu.Item key="/statistics" icon={<BarChartOutlined />}>
              <Link to="/statistics">Statistics</Link>
            </Menu.Item>
          )}
          <Menu.Item key="/feedback" icon={<MessageOutlined />}>
            <Link to="/feedback">Feedback</Link>
          </Menu.Item>
        </Menu>
        <Menu theme="dark" mode="inline" selectable={false} style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <SubMenu 
            key="user" 
            icon={<Avatar icon={<UserOutlined />} />} 
            title={currentUser.username}
          >
            <Menu.Item key="profile" icon={<UserOutlined />}>
              <Link to="/profile">Profile</Link>
            </Menu.Item>
            <Menu.Item key="settings" icon={<SettingOutlined />}>
              <Link to="/settings">Settings</Link>
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
            {children}
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>Fitness Reservation System ©2024</Footer>
      </Layout>
    </Layout>
  );
};

export default MainLayout;