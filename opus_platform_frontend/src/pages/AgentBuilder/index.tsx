import React, { useState, useCallback } from 'react';
import { Card, Tabs, Button, Steps, Space, message, Modal, Upload } from 'antd';
import {
  SaveOutlined,
  PlayCircleOutlined,
  ExportOutlined,
  ImportOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { motion } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import { IdentityEditor } from './components/IdentityEditor';
import { ArchitectureEditor } from './components/ArchitectureEditor';
import { MemoryEditor } from './components/MemoryEditor';
import { FormatEditor } from './components/FormatEditor';
import { WorkflowEditor } from './components/WorkflowEditor';
import { ConstraintsEditor } from './components/ConstraintsEditor';
import { PreviewPanel } from './components/PreviewPanel';
import { TestConsole } from './components/TestConsole';
import { useAgentStore } from '../../stores/agentStore';
import './index.css';

const { Step } = Steps;

interface BuilderStep {
  key: string;
  title: string;
  description: string;
  component: React.ReactNode;
  status: 'wait' | 'process' | 'finish' | 'error';
}

export const AgentBuilder: React.FC = () => {
  const navigate = useNavigate();
  const { agentId } = useParams();
  const [activeTab, setActiveTab] = useState('identity');
  const [currentStep, setCurrentStep] = useState(0);
  const [previewVisible, setPreviewVisible] = useState(false);
  const [testVisible, setTestVisible] = useState(false);
  const [importModalVisible, setImportModalVisible] = useState(false);
  
  const {
    currentAgent,
    loadAgent,
    saveAgent,
    createAgent,
    exportAgent,
    importAgent,
    validateAgent
  } = useAgentStore();

  React.useEffect(() => {
    if (agentId) {
      loadAgent(agentId);
    } else {
      createAgent();
    }
  }, [agentId, loadAgent, createAgent]);

  const builderSteps: BuilderStep[] = [
    {
      key: 'identity',
      title: '身份定义',
      description: '定义智能体的角色和基本信息',
      component: <IdentityEditor />,
      status: currentAgent?.identity ? 'finish' : 'wait',
    },
    {
      key: 'architecture',
      title: '架构设计',
      description: '配置知识、技能和工具',
      component: <ArchitectureEditor />,
      status: currentAgent?.architecture ? 'finish' : 'wait',
    },
    {
      key: 'memory',
      title: '记忆系统',
      description: '设计记忆架构和存储策略',
      component: <MemoryEditor />,
      status: currentAgent?.memory ? 'finish' : 'wait',
    },
    {
      key: 'formats',
      title: '格式管理',
      description: '定义输入输出格式模板',
      component: <FormatEditor />,
      status: currentAgent?.formats ? 'finish' : 'wait',
    },
    {
      key: 'workflow',
      title: '工作流设计',
      description: '设计智能体的处理流程',
      component: <WorkflowEditor />,
      status: currentAgent?.workflow ? 'finish' : 'wait',
    },
    {
      key: 'constraints',
      title: '约束规则',
      description: '设置行为约束和安全规则',
      component: <ConstraintsEditor />,
      status: currentAgent?.constraints ? 'finish' : 'wait',
    },
  ];

  const handleSave = useCallback(async () => {
    try {
      const validation = validateAgent(currentAgent);
      if (!validation.isValid) {
        message.error(`验证失败: ${validation.errors.join(', ')}`);
        return;
      }
      
      await saveAgent(currentAgent);
      message.success('智能体保存成功');
    } catch (error) {
      message.error('保存失败: ' + (error as Error).message);
    }
  }, [currentAgent, saveAgent, validateAgent]);

  const handleExport = useCallback(async () => {
    try {
      const opusContent = await exportAgent(currentAgent.id);
      const blob = new Blob([opusContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentAgent.name || 'agent'}.opus`;
      a.click();
      URL.revokeObjectURL(url);
      message.success('OPUS文件导出成功');
    } catch (error) {
      message.error('导出失败: ' + (error as Error).message);
    }
  }, [currentAgent, exportAgent]);

  const handleImport = useCallback(async (file: File) => {
    try {
      const content = await file.text();
      await importAgent(content);
      message.success('OPUS文件导入成功');
      setImportModalVisible(false);
    } catch (error) {
      message.error('导入失败: ' + (error as Error).message);
    }
    return false; // Prevent default upload
  }, [importAgent]);

  const handleTest = useCallback(() => {
    setTestVisible(true);
  }, []);

  const handleDeploy = useCallback(() => {
    navigate(`/deployment?agentId=${currentAgent.id}`);
  }, [navigate, currentAgent]);

  const tabItems = builderSteps.map((step, index) => ({
    key: step.key,
    label: (
      <div className="tab-label">
        <span className={`step-number ${step.status}`}>{index + 1}</span>
        <div>
          <div className="tab-title">{step.title}</div>
          <div className="tab-description">{step.description}</div>
        </div>
      </div>
    ),
    children: (
      <motion.div
        key={step.key}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: -20 }}
        transition={{ duration: 0.3 }}
        className="tab-content"
      >
        {step.component}
      </motion.div>
    ),
  }));

  return (
    <div className="agent-builder">
      <div className="builder-header">
        <div className="header-info">
          <h1>{currentAgent?.name || '新建智能体'}</h1>
          <div className="agent-status">
            状态: <span className="status-badge">编辑中</span>
          </div>
        </div>
        
        <Space className="header-actions">
          <Button
            icon={<ImportOutlined />}
            onClick={() => setImportModalVisible(true)}
          >
            导入OPUS
          </Button>
          
          <Button
            icon={<FileTextOutlined />}
            onClick={() => setPreviewVisible(true)}
          >
            预览
          </Button>
          
          <Button
            icon={<PlayCircleOutlined />}
            type="primary"
            ghost
            onClick={handleTest}
          >
            测试
          </Button>
          
          <Button
            icon={<SaveOutlined />}
            type="primary"
            onClick={handleSave}
          >
            保存
          </Button>
          
          <Button
            icon={<ExportOutlined />}
            onClick={handleExport}
          >
            导出
          </Button>
        </Space>
      </div>

      <div className="builder-content">
        <div className="progress-section">
          <Steps
            current={currentStep}
            size="small"
            className="builder-steps"
          >
            {builderSteps.map((step, index) => (
              <Step
                key={step.key}
                title={step.title}
                description={step.description}
                status={step.status}
                onClick={() => {
                  setCurrentStep(index);
                  setActiveTab(step.key);
                }}
              />
            ))}
          </Steps>
        </div>

        <Card className="builder-card">
          <Tabs
            activeKey={activeTab}
            onChange={(key) => {
              setActiveTab(key);
              const stepIndex = builderSteps.findIndex(step => step.key === key);
              setCurrentStep(stepIndex);
            }}
            type="card"
            items={tabItems}
            className="builder-tabs"
          />
        </Card>
      </div>

      {/* Action Bar */}
      <div className="action-bar">
        <div className="action-bar-left">
          <Button
            disabled={currentStep === 0}
            onClick={() => {
              const newStep = Math.max(0, currentStep - 1);
              setCurrentStep(newStep);
              setActiveTab(builderSteps[newStep].key);
            }}
          >
            上一步
          </Button>
          
          <Button
            type="primary"
            disabled={currentStep === builderSteps.length - 1}
            onClick={() => {
              const newStep = Math.min(builderSteps.length - 1, currentStep + 1);
              setCurrentStep(newStep);
              setActiveTab(builderSteps[newStep].key);
            }}
          >
            下一步
          </Button>
        </div>
        
        <div className="action-bar-right">
          <Button
            type="primary"
            size="large"
            onClick={handleDeploy}
            disabled={!currentAgent?.id}
          >
            部署智能体
          </Button>
        </div>
      </div>

      {/* Preview Modal */}
      <Modal
        title="智能体预览"
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={800}
        className="preview-modal"
      >
        <PreviewPanel agent={currentAgent} />
      </Modal>

      {/* Test Console Modal */}
      <Modal
        title="智能体测试"
        open={testVisible}
        onCancel={() => setTestVisible(false)}
        footer={null}
        width={1000}
        className="test-modal"
      >
        <TestConsole agent={currentAgent} />
      </Modal>

      {/* Import Modal */}
      <Modal
        title="导入OPUS文件"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={null}
      >
        <Upload.Dragger
          accept=".opus,.txt,.md"
          beforeUpload={handleImport}
          showUploadList={false}
          className="import-uploader"
        >
          <p className="ant-upload-drag-icon">
            <FileTextOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 .opus、.txt、.md 格式的OPUS智能体定义文件
          </p>
        </Upload.Dragger>
      </Modal>
    </div>
  );
};