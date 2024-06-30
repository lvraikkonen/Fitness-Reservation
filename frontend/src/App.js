import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import { Layout } from 'antd';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import UserProfilePage from './pages/UserProfilePage';
import GymListPage from './pages/GymListPage';
import BookingPage from './pages/BookingPage';

const { Header, Content, Footer } = Layout;

function App() {
  return (
    <Router>
      <Layout className="layout" style={{ minHeight: '100vh' }}>
        <Header>
          {/* Add navigation menu here */}
        </Header>
        <Content style={{ padding: '0 50px' }}>
          <Switch>
            <Route exact path="/" component={HomePage} />
            <Route path="/login" component={LoginPage} />
            <Route path="/profile" component={UserProfilePage} />
            <Route path="/gyms" component={GymListPage} />
            <Route path="/booking" component={BookingPage} />
          </Switch>
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          Fitness Booking System ©2024 Created by Your Company
        </Footer>
      </Layout>
    </Router>
  );
}

export default App;