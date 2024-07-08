import React, { useState } from 'react';
import { Layout, Menu, Breadcrumb, Avatar, Dropdown } from 'antd';
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

const { Header, Content, Footer, Sider } = Layout;
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

  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />}>
        <Link to="/profile">Profile</Link>
      </Menu.Item>
      <Menu.Item key="settings" icon={<SettingOutlined />}>
        <Link to="/settings">Settings</Link>
      </Menu.Item>
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={handleLogout}>
        Logout
      </Menu.Item>
    </Menu>
  );

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={setCollapsed}>
        <div className="logo" />
        <Menu theme="dark" defaultSelectedKeys={[location.pathname]} mode="inline">
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
      </Sider>
      <Layout className="site-layout">
        <Header className="site-layout-background" style={{ padding: 0, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Dropdown overlay={userMenu} trigger={['click']}>
            <Avatar style={{ marginRight: 16, cursor: 'pointer' }} icon={<UserOutlined />} />
          </Dropdown>
        </Header>
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