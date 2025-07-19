import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Agent {
  id: string;
  name: string;
  description?: string;
  version: string;
  status: 'draft' | 'testing' | 'deployed' | 'archived';
  createdAt: Date;
  updatedAt: Date;
  
  // OPUS Components
  identity: {
    name: string;
    role: string;
    description?: string;
    roleTemplate?: string;
    constraints: string[];
    scenarios: string[];
  };
  
  architecture: {
    knowledge: string[];
    skills: string[];
    reasoningEngine: string[];
    externalTools: string[];
    ragRetrieval: string[];
  };
  
  memory: {
    architecture: string;
    operations: string[];
    storageStrategy: string;
    paths: Record<string, any>;
    dynamicOperations: string[];
  };
  
  formats: {
    analysisFormat: any;
    resultFormat: any;
    interactionFormat: any;
    customFormats: Record<string, any>;
  };
  
  workflow: {
    functions: Record<string, any>;
    rawContent: string;
  };
  
  constraints: {
    behavioral: string[];
    technical: string[];
    security: string[];
    output: string[];
  };
  
  // Platform-specific fields
  deployment?: {
    target: string;
    url?: string;
    status: string;
    config: any;
  };
  
  analytics?: {
    totalRequests: number;
    successRate: number;
    avgResponseTime: number;
    lastActive: Date;
  };
}

interface AgentStore {
  // State
  agents: Agent[];
  currentAgent: Agent | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  loadAgents: () => Promise<void>;
  loadAgent: (id: string) => Promise<void>;
  createAgent: () => void;
  updateAgent: (agent: Agent) => void;
  saveAgent: (agent: Agent) => Promise<void>;
  deleteAgent: (id: string) => Promise<void>;
  deployAgent: (id: string, config: any) => Promise<void>;
  exportAgent: (id: string) => Promise<string>;
  importAgent: (opusContent: string) => Promise<void>;
  validateAgent: (agent: Agent) => { isValid: boolean; errors: string[] };
  
  // Filters and search
  searchAgents: (query: string) => Agent[];
  filterAgents: (status?: string, tags?: string[]) => Agent[];
}

export const useAgentStore = create<AgentStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      agents: [],
      currentAgent: null,
      loading: false,
      error: null,
      
      // Actions
      loadAgents: async () => {
        set({ loading: true, error: null });
        try {
          // Simulate API call
          const response = await fetch('/api/agents');
          const agents = await response.json();
          set({ agents, loading: false });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
        }
      },
      
      loadAgent: async (id: string) => {
        set({ loading: true, error: null });
        try {
          // Simulate API call
          const response = await fetch(`/api/agents/${id}`);
          const agent = await response.json();
          set({ currentAgent: agent, loading: false });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
        }
      },
      
      createAgent: () => {
        const newAgent: Agent = {
          id: `agent_${Date.now()}`,
          name: '',
          version: '1.0.0',
          status: 'draft',
          createdAt: new Date(),
          updatedAt: new Date(),
          
          identity: {
            name: '',
            role: '',
            constraints: [],
            scenarios: [],
          },
          
          architecture: {
            knowledge: [],
            skills: [],
            reasoningEngine: [],
            externalTools: [],
            ragRetrieval: [],
          },
          
          memory: {
            architecture: '',
            operations: [],
            storageStrategy: '',
            paths: {},
            dynamicOperations: [],
          },
          
          formats: {
            analysisFormat: {},
            resultFormat: {},
            interactionFormat: {},
            customFormats: {},
          },
          
          workflow: {
            functions: {},
            rawContent: '',
          },
          
          constraints: {
            behavioral: [],
            technical: [],
            security: [],
            output: [],
          },
        };
        
        set({ currentAgent: newAgent });
      },
      
      updateAgent: (agent: Agent) => {
        set({ 
          currentAgent: { 
            ...agent, 
            updatedAt: new Date() 
          } 
        });
      },
      
      saveAgent: async (agent: Agent) => {
        set({ loading: true, error: null });
        try {
          // Simulate API call
          const response = await fetch(`/api/agents/${agent.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(agent),
          });
          
          if (!response.ok) throw new Error('Failed to save agent');
          
          const savedAgent = await response.json();
          
          // Update agents list
          const { agents } = get();
          const updatedAgents = agents.map(a => 
            a.id === savedAgent.id ? savedAgent : a
          );
          
          // Add to list if new
          if (!agents.find(a => a.id === savedAgent.id)) {
            updatedAgents.push(savedAgent);
          }
          
          set({ 
            agents: updatedAgents,
            currentAgent: savedAgent,
            loading: false 
          });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
        }
      },
      
      deleteAgent: async (id: string) => {
        set({ loading: true, error: null });
        try {
          // Simulate API call
          await fetch(`/api/agents/${id}`, { method: 'DELETE' });
          
          const { agents } = get();
          const updatedAgents = agents.filter(a => a.id !== id);
          
          set({ 
            agents: updatedAgents,
            currentAgent: null,
            loading: false 
          });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
        }
      },
      
      deployAgent: async (id: string, config: any) => {
        set({ loading: true, error: null });
        try {
          // Simulate API call
          const response = await fetch(`/api/agents/${id}/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config),
          });
          
          if (!response.ok) throw new Error('Deployment failed');
          
          const deployment = await response.json();
          
          // Update agent with deployment info
          const { agents, currentAgent } = get();
          const updatedAgents = agents.map(a => 
            a.id === id ? { ...a, deployment, status: 'deployed' as const } : a
          );
          
          set({ 
            agents: updatedAgents,
            currentAgent: currentAgent?.id === id ? 
              { ...currentAgent, deployment, status: 'deployed' } : 
              currentAgent,
            loading: false 
          });
        } catch (error) {
          set({ error: (error as Error).message, loading: false });
        }
      },
      
      exportAgent: async (id: string): Promise<string> => {
        const agent = get().agents.find(a => a.id === id) || get().currentAgent;
        if (!agent) throw new Error('Agent not found');
        
        // Convert agent to OPUS format
        const opusContent = convertAgentToOPUS(agent);
        return opusContent;
      },
      
      importAgent: async (opusContent: string) => {
        try {
          // Parse OPUS content and create agent
          const agent = parseOPUSContent(opusContent);
          set({ currentAgent: agent });
        } catch (error) {
          throw new Error('Failed to import OPUS content: ' + (error as Error).message);
        }
      },
      
      validateAgent: (agent: Agent) => {
        const errors: string[] = [];
        
        if (!agent.identity?.name?.trim()) {
          errors.push('智能体名称不能为空');
        }
        
        if (!agent.identity?.role?.trim()) {
          errors.push('专业身份不能为空');
        }
        
        if (!agent.architecture?.knowledge?.length) {
          errors.push('至少需要定义一个知识领域');
        }
        
        if (!agent.architecture?.skills?.length) {
          errors.push('至少需要定义一个核心技能');
        }
        
        if (!Object.keys(agent.workflow?.functions || {}).length) {
          errors.push('至少需要定义一个工作流函数');
        }
        
        return {
          isValid: errors.length === 0,
          errors,
        };
      },
      
      searchAgents: (query: string) => {
        const { agents } = get();
        if (!query.trim()) return agents;
        
        const lowercaseQuery = query.toLowerCase();
        return agents.filter(agent => 
          agent.name.toLowerCase().includes(lowercaseQuery) ||
          agent.description?.toLowerCase().includes(lowercaseQuery) ||
          agent.identity?.role?.toLowerCase().includes(lowercaseQuery)
        );
      },
      
      filterAgents: (status?: string, tags?: string[]) => {
        const { agents } = get();
        
        return agents.filter(agent => {
          if (status && agent.status !== status) return false;
          if (tags?.length) {
            // Implement tag filtering logic
            return true;
          }
          return true;
        });
      },
    }),
    {
      name: 'agent-store',
    }
  )
);

// Helper functions
function convertAgentToOPUS(agent: Agent): string {
  return `<identity>
${agent.identity.role}

约束规则：
${agent.identity.constraints.map(c => `- ${c}`).join('\n')}

应用场景：
${agent.identity.scenarios.map(s => `- ${s}`).join('\n')}
</identity>

<architecture>
专业知识：[${agent.architecture.knowledge.map(k => `"${k}"`).join(', ')}]
核心技能：[${agent.architecture.skills.map(s => `"${s}"`).join(', ')}]
推理引擎：[${agent.architecture.reasoningEngine.map(r => `"${r}"`).join(', ')}]
外部工具：[${agent.architecture.externalTools.map(t => `"${t}"`).join(', ')}]
RAG检索：[${agent.architecture.ragRetrieval.map(r => `"${r}"`).join(', ')}]
</architecture>

<Memory>
${agent.memory.architecture}

${Object.entries(agent.memory.paths).map(([path, data]) => 
  `store("${path}", ${JSON.stringify(data)})`
).join('\n')}

${agent.memory.dynamicOperations.map(op => `locate("${op}")`).join('\n')}
</Memory>

<formats>
${Object.entries(agent.formats.customFormats).map(([name, format]) => 
  `[Format.${name}] = ${JSON.stringify(format)}`
).join('\n')}
</formats>

<workflow>
${agent.workflow.rawContent || Object.entries(agent.workflow.functions).map(([name, func]) => 
  `FN ${name}():\nBEGIN\n  // Workflow implementation\nEND`
).join('\n\n')}
</workflow>

<constraints>
行为约束：
${agent.constraints.behavioral.map(c => `- ${c}`).join('\n')}

技术约束：
${agent.constraints.technical.map(c => `- ${c}`).join('\n')}

安全约束：
${agent.constraints.security.map(c => `- ${c}`).join('\n')}

输出约束：
${agent.constraints.output.map(c => `- ${c}`).join('\n')}
</constraints>`;
}

function parseOPUSContent(opusContent: string): Agent {
  // Simple OPUS parser - can be enhanced
  const agent: Agent = {
    id: `imported_${Date.now()}`,
    name: 'Imported Agent',
    version: '1.0.0',
    status: 'draft',
    createdAt: new Date(),
    updatedAt: new Date(),
    
    identity: {
      name: 'Imported Agent',
      role: '',
      constraints: [],
      scenarios: [],
    },
    
    architecture: {
      knowledge: [],
      skills: [],
      reasoningEngine: [],
      externalTools: [],
      ragRetrieval: [],
    },
    
    memory: {
      architecture: '',
      operations: [],
      storageStrategy: '',
      paths: {},
      dynamicOperations: [],
    },
    
    formats: {
      analysisFormat: {},
      resultFormat: {},
      interactionFormat: {},
      customFormats: {},
    },
    
    workflow: {
      functions: {},
      rawContent: '',
    },
    
    constraints: {
      behavioral: [],
      technical: [],
      security: [],
      output: [],
    },
  };
  
  // Parse identity section
  const identityMatch = opusContent.match(/<identity>(.*?)<\/identity>/s);
  if (identityMatch) {
    const identityContent = identityMatch[1].trim();
    const lines = identityContent.split('\n').filter(line => line.trim());
    if (lines.length > 0) {
      agent.identity.role = lines[0];
      agent.identity.name = lines[0].substring(0, 50) + '...';
    }
  }
  
  // Parse architecture section
  const architectureMatch = opusContent.match(/<architecture>(.*?)<\/architecture>/s);
  if (architectureMatch) {
    const architectureContent = architectureMatch[1];
    
    const knowledgeMatch = architectureContent.match(/专业知识[：:]\s*\[(.*?)\]/);
    if (knowledgeMatch) {
      agent.architecture.knowledge = knowledgeMatch[1]
        .split(',')
        .map(k => k.trim().replace(/['"]/g, ''))
        .filter(k => k);
    }
    
    const skillsMatch = architectureContent.match(/核心技能[：:]\s*\[(.*?)\]/);
    if (skillsMatch) {
      agent.architecture.skills = skillsMatch[1]
        .split(',')
        .map(s => s.trim().replace(/['"]/g, ''))
        .filter(s => s);
    }
  }
  
  return agent;
}