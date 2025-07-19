import React, { useState } from 'react';
import { Layout as AntLayout, Menu, Avatar, Dropdown, Button, Badge, Tooltip } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DashboardOutlined,
  BuildOutlined,
  ShopOutlined,
  BranchesOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  BarChartOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useThemeStore } from '../../stores/themeStore';
import { useUserStore } from '../../stores/userStore';
import './index.css';

const { Header, Sider, Content } = AntLayout;

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useThemeStore();
  const { user, logout } = useUserStore();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/builder',
      icon: <BuildOutlined />,
      label: '智能体构建器',
    },
    {
      key: '/marketplace',
      icon: <ShopOutlined />,
      label: '智能体市场',
    },
    {
      type: 'divider',
    },
    {
      key: 'workflow',
      icon: <BranchesOutlined />,
      label: '工作流管理',
      children: [
        {
          key: '/workflow/new',
          label: '新建工作流',
        },
        {
          key: '/workflow/templates',
          label: '工作流模板',
        },
      ],
    },
    {
      key: 'memory',
      icon: <DatabaseOutlined />,
      label: '记忆管理',
      children: [
        {
          key: '/memory/explorer',
          label: '记忆浏览器',
        },
        {
          key: '/memory/analysis',
          label: '记忆分析',
        },
      ],
    },
    {
      key: '/deployment',
      icon: <CloudServerOutlined />,
      label: '部署中心',
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: '分析报告',
    },
    {
      type: 'divider',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '设置',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      label: '个人资料',
      icon: <UserOutlined />,
    },
    {
      key: 'help',
      label: '帮助文档',
      icon: <QuestionCircleOutlined />,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: logout,
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <AntLayout className="layout-container">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        className="layout-sider"
        theme={isDarkMode ? 'dark' : 'light'}
        width={250}
      >
        <motion.div
          className="logo-container"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="logo">
            {collapsed ? 'OPUS' : 'OPUS Agent Platform'}
          </div>
        </motion.div>

        <Menu
          theme={isDarkMode ? 'dark' : 'light'}
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
          className="layout-menu"
        />
      </Sider>

      <AntLayout className="layout-main">
        <Header className="layout-header">
          <div className="header-left">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className="collapse-button"
            />
            
            <div className="breadcrumb">
              <h2>{getPageTitle(location.pathname)}</h2>
            </div>
          </div>

          <div className="header-right">
            <Tooltip title="通知">
              <Badge count={3} size="small">
                <Button
                  type="text"
                  icon={<BellOutlined />}
                  className="header-action-btn"
                />
              </Badge>
            </Tooltip>

            <Tooltip title={isDarkMode ? '切换到浅色模式' : '切换到深色模式'}>
              <Button
                type="text"
                onClick={toggleTheme}
                className="header-action-btn"
              >
                {isDarkMode ? '🌙' : '☀️'}
              </Button>
            </Tooltip>

            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              arrow
            >
              <div className="user-menu">
                <Avatar
                  size={32}
                  src={user?.avatar}
                  icon={<UserOutlined />}
                />
                {!collapsed && (
                  <span className="user-name">{user?.name || '用户'}</span>
                )}
              </div>
            </Dropdown>
          </div>
        </Header>

        <Content className="layout-content">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="content-wrapper"
          >
            {children}
          </motion.div>
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

function getPageTitle(pathname: string): string {
  const titles: Record<string, string> = {
    '/dashboard': '仪表板',
    '/builder': '智能体构建器',
    '/marketplace': '智能体市场',
    '/deployment': '部署中心',
    '/analytics': '分析报告',
    '/settings': '设置',
  };

  // Handle dynamic routes
  if (pathname.startsWith('/workflow/')) {
    return '工作流设计器';
  }
  if (pathname.startsWith('/memory/')) {
    return '记忆管理';
  }

  return titles[pathname] || '未知页面';
}