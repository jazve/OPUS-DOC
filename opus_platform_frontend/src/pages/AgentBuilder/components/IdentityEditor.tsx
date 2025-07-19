import React from 'react';
import { Card, Form, Input, Select, Tag, Space, Button, Tooltip } from 'antd';
import { PlusOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { useAgentStore } from '../../../stores/agentStore';

const { TextArea } = Input;
const { Option } = Select;

export const IdentityEditor: React.FC = () => {
  const { currentAgent, updateAgent } = useAgentStore();
  const [form] = Form.useForm();

  const handleFormChange = (changedFields: any, allFields: any) => {
    const identity = form.getFieldsValue();
    updateAgent({
      ...currentAgent,
      identity: {
        ...currentAgent.identity,
        ...identity,
      },
    });
  };

  const addConstraint = (newConstraint: string) => {
    if (!newConstraint.trim()) return;
    
    const constraints = currentAgent.identity?.constraints || [];
    const updatedConstraints = [...constraints, newConstraint.trim()];
    
    updateAgent({
      ...currentAgent,
      identity: {
        ...currentAgent.identity,
        constraints: updatedConstraints,
      },
    });
  };

  const removeConstraint = (constraintToRemove: string) => {
    const constraints = currentAgent.identity?.constraints || [];
    const updatedConstraints = constraints.filter(c => c !== constraintToRemove);
    
    updateAgent({
      ...currentAgent,
      identity: {
        ...currentAgent.identity,
        constraints: updatedConstraints,
      },
    });
  };

  const addScenario = (newScenario: string) => {
    if (!newScenario.trim()) return;
    
    const scenarios = currentAgent.identity?.scenarios || [];
    const updatedScenarios = [...scenarios, newScenario.trim()];
    
    updateAgent({
      ...currentAgent,
      identity: {
        ...currentAgent.identity,
        scenarios: updatedScenarios,
      },
    });
  };

  const removeScenario = (scenarioToRemove: string) => {
    const scenarios = currentAgent.identity?.scenarios || [];
    const updatedScenarios = scenarios.filter(s => s !== scenarioToRemove);
    
    updateAgent({
      ...currentAgent,
      identity: {
        ...currentAgent.identity,
        scenarios: updatedScenarios,
      },
    });
  };

  const roleTemplates = [
    { value: 'assistant', label: '通用助手', description: '提供全方位的问答和协助服务' },
    { value: 'analyst', label: '数据分析师', description: '专注于数据分析和洞察发现' },
    { value: 'consultant', label: '业务顾问', description: '提供专业的业务咨询建议' },
    { value: 'teacher', label: '教学助手', description: '辅助教学和学习指导' },
    { value: 'researcher', label: '研究员', description: '协助学术研究和文献分析' },
    { value: 'writer', label: '内容创作者', description: '协助内容创作和编辑' },
    { value: 'developer', label: '开发助手', description: '提供编程和技术支持' },
    { value: 'custom', label: '自定义角色', description: '根据具体需求定制角色' },
  ];

  return (
    <div className="identity-editor">
      <Form
        form={form}
        layout="vertical"
        initialValues={currentAgent?.identity}
        onFieldsChange={handleFormChange}
        className="identity-form"
      >
        <Card title="基本信息" className="editor-card">
          <Form.Item
            label={
              <Space>
                智能体名称
                <Tooltip title="给你的智能体起一个容易识别的名称">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            name="name"
            rules={[{ required: true, message: '请输入智能体名称' }]}
          >
            <Input
              placeholder="例如：客服助手、数据分析专家..."
              size="large"
            />
          </Form.Item>

          <Form.Item
            label={
              <Space>
                角色模板
                <Tooltip title="选择一个预设的角色模板作为起点">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            name="roleTemplate"
          >
            <Select
              placeholder="选择角色模板"
              size="large"
              showSearch
              optionFilterProp="children"
            >
              {roleTemplates.map(template => (
                <Option key={template.value} value={template.value}>
                  <div>
                    <div>{template.label}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {template.description}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label={
              <Space>
                专业身份
                <Tooltip title="详细描述智能体的专业角色和定位">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            name="role"
            rules={[{ required: true, message: '请输入专业身份描述' }]}
          >
            <TextArea
              rows={4}
              placeholder="例如：我是一名专业的客户服务助手，专注于为用户提供高效、准确的问题解答和服务支持..."
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            label={
              <Space>
                角色描述
                <Tooltip title="更详细的角色背景和特点描述">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
            name="description"
          >
            <TextArea
              rows={3}
              placeholder="描述智能体的特点、风格、专长等..."
              showCount
              maxLength={300}
            />
          </Form.Item>
        </Card>

        <Card title="行为约束" className="editor-card">
          <Form.Item
            label={
              <Space>
                约束规则
                <Tooltip title="定义智能体的行为边界和限制">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <div className="tag-list">
              {(currentAgent.identity?.constraints || []).map((constraint, index) => (
                <Tag
                  key={index}
                  closable
                  onClose={() => removeConstraint(constraint)}
                  className="constraint-tag"
                >
                  {constraint}
                </Tag>
              ))}
              
              <ConstraintInput onAdd={addConstraint} />
            </div>
            
            <div className="preset-constraints">
              <div className="preset-label">常用约束规则：</div>
              {[
                '保持礼貌和专业',
                '确保信息准确性',
                '保护用户隐私',
                '避免提供有害内容',
                '遵守法律法规',
                '客观公正',
              ].map(constraint => (
                <Button
                  key={constraint}
                  size="small"
                  type="dashed"
                  onClick={() => addConstraint(constraint)}
                  className="preset-button"
                >
                  + {constraint}
                </Button>
              ))}
            </div>
          </Form.Item>
        </Card>

        <Card title="应用场景" className="editor-card">
          <Form.Item
            label={
              <Space>
                适用场景
                <Tooltip title="定义智能体适用的具体场景和用途">
                  <QuestionCircleOutlined />
                </Tooltip>
              </Space>
            }
          >
            <div className="tag-list">
              {(currentAgent.identity?.scenarios || []).map((scenario, index) => (
                <Tag
                  key={index}
                  closable
                  onClose={() => removeScenario(scenario)}
                  className="scenario-tag"
                >
                  {scenario}
                </Tag>
              ))}
              
              <ScenarioInput onAdd={addScenario} />
            </div>
            
            <div className="preset-scenarios">
              <div className="preset-label">常见应用场景：</div>
              {[
                '客户咨询',
                '技术支持',
                '产品推荐',
                '问题诊断',
                '知识问答',
                '任务协助',
                '学习辅导',
                '内容创作',
              ].map(scenario => (
                <Button
                  key={scenario}
                  size="small"
                  type="dashed"
                  onClick={() => addScenario(scenario)}
                  className="preset-button"
                >
                  + {scenario}
                </Button>
              ))}
            </div>
          </Form.Item>
        </Card>
      </Form>
    </div>
  );
};

// 约束输入组件
const ConstraintInput: React.FC<{ onAdd: (constraint: string) => void }> = ({ onAdd }) => {
  const [inputVisible, setInputVisible] = React.useState(false);
  const [inputValue, setInputValue] = React.useState('');
  const inputRef = React.useRef<any>(null);

  React.useEffect(() => {
    if (inputVisible) {
      inputRef.current?.focus();
    }
  }, [inputVisible]);

  const handleInputConfirm = () => {
    if (inputValue) {
      onAdd(inputValue);
    }
    setInputVisible(false);
    setInputValue('');
  };

  if (inputVisible) {
    return (
      <Input
        ref={inputRef}
        type="text"
        size="small"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onBlur={handleInputConfirm}
        onPressEnter={handleInputConfirm}
        placeholder="输入约束规则"
        style={{ width: 200 }}
      />
    );
  }

  return (
    <Tag onClick={() => setInputVisible(true)} className="add-tag">
      <PlusOutlined /> 添加约束
    </Tag>
  );
};

// 场景输入组件
const ScenarioInput: React.FC<{ onAdd: (scenario: string) => void }> = ({ onAdd }) => {
  const [inputVisible, setInputVisible] = React.useState(false);
  const [inputValue, setInputValue] = React.useState('');
  const inputRef = React.useRef<any>(null);

  React.useEffect(() => {
    if (inputVisible) {
      inputRef.current?.focus();
    }
  }, [inputVisible]);

  const handleInputConfirm = () => {
    if (inputValue) {
      onAdd(inputValue);
    }
    setInputVisible(false);
    setInputValue('');
  };

  if (inputVisible) {
    return (
      <Input
        ref={inputRef}
        type="text"
        size="small"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onBlur={handleInputConfirm}
        onPressEnter={handleInputConfirm}
        placeholder="输入应用场景"
        style={{ width: 200 }}
      />
    );
  }

  return (
    <Tag onClick={() => setInputVisible(true)} className="add-tag">
      <PlusOutlined /> 添加场景
    </Tag>
  );
};