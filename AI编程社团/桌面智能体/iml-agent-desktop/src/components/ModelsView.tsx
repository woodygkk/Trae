import { useState } from 'react';
import { Plus, Server, Trash2, Edit2, Key, CheckCircle2, X } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ModelConfig {
  id: string;
  name: string;
  provider: 'openai' | 'anthropic' | 'gemini' | 'local' | 'other';
  apiKey: string;
  baseUrl?: string;
  isActive: boolean;
}

interface ModelsViewProps {
  models: ModelConfig[];
  onAddModel: (model: ModelConfig) => void;
  onDeleteModel: (id: string) => void;
  onUpdateModel: (id: string, model: Partial<ModelConfig>) => void;
}

export default function ModelsView({ models, onAddModel, onDeleteModel, onUpdateModel }: ModelsViewProps) {
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingModel, setEditingModel] = useState<ModelConfig | null>(null);

  const [formData, setFormData] = useState<Partial<ModelConfig>>({
    provider: 'openai',
    name: '',
    apiKey: '',
    baseUrl: ''
  });

  const handleSave = () => {
    if (!formData.name || !formData.apiKey) return;

    if (editingModel) {
      onUpdateModel(editingModel.id, formData);
    } else {
      onAddModel({
        id: Math.random().toString(36).substr(2, 9),
        name: formData.name || '',
        provider: formData.provider as any || 'openai',
        apiKey: formData.apiKey || '',
        baseUrl: formData.baseUrl,
        isActive: false
      });
    }
    
    setShowAddModal(false);
    setEditingModel(null);
    setFormData({ provider: 'openai', name: '', apiKey: '', baseUrl: '' });
  };

  const openEdit = (model: ModelConfig) => {
    setEditingModel(model);
    setFormData(model);
    setShowAddModal(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('确定要删除这个模型配置吗？')) {
      onDeleteModel(id);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white min-w-0 h-full">
      {/* Header */}
      <header className="h-14 border-b border-gray-100 flex items-center px-6 justify-between bg-white shrink-0 pr-36">
        <div className="text-sm text-gray-500">
          <span className="font-semibold text-gray-800">iML Agent Desktop</span>
          <span className="mx-2">/</span>
          <span>模型管理</span>
        </div>
        <button 
          onClick={() => {
            setEditingModel(null);
            setFormData({ provider: 'openai', name: '', apiKey: '', baseUrl: '' });
            setShowAddModal(true);
          }}
          className="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 flex items-center gap-2 shadow-sm"
        >
          <Plus size={16} />
          添加模型
        </button>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-6">
            <h2 className="text-xl font-bold text-gray-800 mb-2">配置模型 API</h2>
            <p className="text-gray-500 text-sm">配置不同提供商的模型 API，以便在对话中切换使用。</p>
          </div>

          <div className="grid gap-4">
            {models.map((model) => (
              <div key={model.id} className={cn(
                "flex items-center p-5 border rounded-xl transition-all bg-white group",
                model.isActive ? "border-indigo-500 ring-1 ring-indigo-500 bg-indigo-50/30" : "border-gray-200 hover:border-indigo-300 hover:shadow-md"
              )}>
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center shrink-0 mr-4",
                  model.isActive ? "bg-indigo-100 text-indigo-600" : "bg-gray-100 text-gray-500"
                )}>
                  <Server size={24} />
                </div>
                
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-semibold text-gray-900">{model.name}</h3>
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full uppercase font-mono tracking-wide">
                      {model.provider}
                    </span>
                    {model.isActive && (
                      <span className="flex items-center gap-1 text-xs text-indigo-600 font-medium bg-indigo-50 px-2 py-0.5 rounded-full">
                        <CheckCircle2 size={12} />
                        当前使用
                      </span>
                    )}
                  </div>
                  <div className="flex items-center text-sm text-gray-500 gap-4">
                    <span className="flex items-center gap-1">
                      <Key size={12} />
                      {model.apiKey.substr(0, 3)}...{model.apiKey.substr(-4)}
                    </span>
                    {model.baseUrl && (
                      <span className="text-gray-400 truncate max-w-[200px]" title={model.baseUrl}>
                        {model.baseUrl}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  {!model.isActive && (
                    <button 
                      onClick={() => onUpdateModel(model.id, { isActive: true })}
                      className="px-3 py-1.5 text-xs font-medium text-indigo-600 hover:bg-indigo-50 rounded-lg border border-transparent hover:border-indigo-100"
                    >
                      设为默认
                    </button>
                  )}
                  <button 
                    onClick={() => openEdit(model)}
                    className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                    title="编辑"
                  >
                    <Edit2 size={16} />
                  </button>
                  <button 
                    onClick={() => handleDelete(model.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg"
                    title="删除"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}

            {models.length === 0 && (
              <div className="text-center py-12 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200">
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm text-gray-400">
                  <Server size={32} />
                </div>
                <h3 className="text-gray-900 font-medium mb-1">暂无模型配置</h3>
                <p className="text-gray-500 text-sm mb-4">添加一个模型 API 开始使用</p>
                <button 
                  onClick={() => setShowAddModal(true)}
                  className="px-4 py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100"
                >
                  立即添加
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 relative">
            <button 
              onClick={() => setShowAddModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Server size={20} />
              {editingModel ? '编辑模型' : '添加新模型'}
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">提供商</label>
                <select 
                  value={formData.provider}
                  onChange={(e) => setFormData({...formData, provider: e.target.value as any})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 bg-white"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="gemini">Google Gemini</option>
                  <option value="local">Local (Ollama/LM Studio)</option>
                  <option value="other">其他 (OpenAI Compatible)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">模型名称</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  placeholder="例如：GPT-4o, Claude 3.5 Sonnet"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">API Key</label>
                <div className="relative">
                  <input 
                    type="password" 
                    value={formData.apiKey}
                    onChange={(e) => setFormData({...formData, apiKey: e.target.value})}
                    placeholder="sk-..."
                    className="w-full pl-3 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-mono text-sm"
                  />
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                    <Key size={14} />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Base URL <span className="text-gray-400 font-normal">(可选)</span>
                </label>
                <input 
                  type="text" 
                  value={formData.baseUrl}
                  onChange={(e) => setFormData({...formData, baseUrl: e.target.value})}
                  placeholder="https://api.openai.com/v1"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-mono text-sm"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button 
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button 
                  onClick={handleSave}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow-sm"
                >
                  {editingModel ? '保存修改' : '添加'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
