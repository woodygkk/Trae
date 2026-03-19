import { useState } from 'react';
import { Plus, Github, Search, X } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { getIconComponent } from '../utils/iconMap';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface Skill {
  id: string;
  title: string;
  tag: string;
  desc: string;
  iconName: string;
  color: string;
}

interface SkillsViewProps {
  skills: Skill[];
  onAddSkill: (skill: Skill) => void;
  onImportSkill?: (skill: Skill) => void;
  onUseSkill?: (skill: Skill) => void;
}

export default function SkillsView({ skills, onAddSkill, onImportSkill, onUseSkill }: SkillsViewProps) {
  const [showImportModal, setShowImportModal] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [importUrl, setImportUrl] = useState('');
  const [newSkillData, setNewSkillData] = useState({ title: '', tag: '', desc: '' });

  const handleImport = () => {
    if (!importUrl) return;
    
    // Simple parsing to get a name from URL
    let name = 'Imported Skill';
    try {
      const url = new URL(importUrl);
      const parts = url.pathname.split('/').filter(Boolean);
      if (parts.length >= 2) {
        name = parts[1]; // Repo name
      }
    } catch (e) {
      // ignore
    }

    const skillData: Skill = {
      id: Math.random().toString(36).substr(2, 9),
      title: name,
      tag: 'imported-skill',
      desc: `Imported from ${importUrl}`,
      iconName: 'github',
      color: 'bg-gray-100 text-gray-800'
    };

    if (onImportSkill) {
      onImportSkill(skillData);
    } else {
      onAddSkill(skillData);
    }

    setImportUrl('');
    setShowImportModal(false);
  };

  const handleCreate = () => {
    if (!newSkillData.title) return;

    onAddSkill({
      id: Math.random().toString(36).substr(2, 9),
      title: newSkillData.title,
      tag: newSkillData.tag || 'custom-skill',
      desc: newSkillData.desc || 'No description provided',
      iconName: 'plus', // Default icon
      color: 'bg-indigo-100 text-indigo-600'
    });

    setNewSkillData({ title: '', tag: '', desc: '' });
    setShowCreateModal(false);
  };

  return (
    <div className="flex-1 flex flex-col bg-white min-w-0 h-full">
      {/* Header */}
      <header className="h-14 border-b border-gray-100 flex items-center px-6 justify-between bg-white shrink-0 pr-36">
        <div className="text-sm text-gray-500">
          <span className="font-semibold text-gray-800">iML Agent Desktop</span>
          <span className="mx-2">/</span>
          <span>技能商店</span>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setShowImportModal(true)}
            className="px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
          >
            <Github size={16} />
            从 GitHub 导入
          </button>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="px-3 py-1.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 flex items-center gap-2 shadow-sm"
          >
            <Plus size={16} />
            创建新技能
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-800">已安装技能</h2>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={16} />
              <input 
                type="text" 
                placeholder="搜索技能..." 
                className="pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 w-64"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {skills.map((skill) => {
              const Icon = getIconComponent(skill.iconName);
              return (
              <div key={skill.id} className="flex flex-col p-5 border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all bg-white group h-full">
                <div className="flex items-start justify-between mb-3">
                  <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-colors", skill.color)}>
                    <Icon size={20} />
                  </div>
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="text-gray-400 hover:text-gray-600">
                      <span className="sr-only">Settings</span>
                      •••
                    </button>
                  </div>
                </div>
                
                <h3 className="font-semibold text-gray-900 mb-1">{skill.title}</h3>
                <div className="mb-3">
                  <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full font-mono">{skill.tag}</span>
                </div>
                <p className="text-sm text-gray-500 line-clamp-2 mb-4 flex-1">{skill.desc}</p>
                
                <button 
                  onClick={() => onUseSkill?.(skill)}
                  className="w-full py-2 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors"
                >
                  打开技能
                </button>
              </div>
            );
            })}
          </div>
        </div>
      </div>

      {/* Import Modal */}
      {showImportModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6 relative">
            <button 
              onClick={() => setShowImportModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Github size={20} />
              从 GitHub 导入技能
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">GitHub 仓库链接</label>
                <input 
                  type="text" 
                  value={importUrl}
                  onChange={(e) => setImportUrl(e.target.value)}
                  placeholder="https://github.com/username/repo"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button 
                  onClick={() => setShowImportModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button 
                  onClick={handleImport}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                >
                  导入
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg p-6 relative">
            <button 
              onClick={() => setShowCreateModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X size={20} />
            </button>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Plus size={20} />
              创建新技能
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">技能名称</label>
                <input 
                  type="text" 
                  value={newSkillData.title}
                  onChange={(e) => setNewSkillData({...newSkillData, title: e.target.value})}
                  placeholder="例如：日报助手"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">标签 (ID)</label>
                <input 
                  type="text" 
                  value={newSkillData.tag}
                  onChange={(e) => setNewSkillData({...newSkillData, tag: e.target.value})}
                  placeholder="例如：daily-reporter"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 font-mono text-sm"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
                <textarea 
                  value={newSkillData.desc}
                  onChange={(e) => setNewSkillData({...newSkillData, desc: e.target.value})}
                  placeholder="这个技能是做什么的？"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 resize-none"
                />
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button 
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg"
                >
                  取消
                </button>
                <button 
                  onClick={handleCreate}
                  className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg"
                >
                  创建技能
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
