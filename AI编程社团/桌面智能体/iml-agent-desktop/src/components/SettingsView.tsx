import { useState } from 'react';
import { Settings, Shield, Globe, Monitor, Key, CheckCircle2, AlertCircle } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function SettingsView() {
  const [activationCode, setActivationCode] = useState('');
  const [isActivated, setIsActivated] = useState(false);
  const [error, setError] = useState('');

  const handleActivate = () => {
    if (!activationCode.trim()) {
      setError('请输入有效的激活码');
      return;
    }
    
    // Mock activation logic
    if (activationCode.length > 5) {
      setIsActivated(true);
      setError('');
    } else {
      setError('激活码无效，请检查后重试');
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-white min-w-0 h-full">
      {/* Header */}
      <header className="h-14 border-b border-gray-100 flex items-center px-6 justify-between bg-white shrink-0 pr-36">
        <div className="text-sm text-gray-500">
          <span className="font-semibold text-gray-800">iML Agent Desktop</span>
          <span className="mx-2">/</span>
          <span>软件设置</span>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        <div className="max-w-2xl mx-auto space-y-8">
          
          {/* Activation Section */}
          <section className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Key size={20} className="text-indigo-600" />
                产品激活
              </h2>
              <p className="text-sm text-gray-500 mt-1">请输入您的许可证密钥以解锁所有高级功能。</p>
            </div>
            
            <div className="p-6">
              {isActivated ? (
                <div className="flex items-center gap-3 text-green-600 bg-green-50 p-4 rounded-lg border border-green-100">
                  <CheckCircle2 size={24} />
                  <div>
                    <div className="font-medium">已激活专业版</div>
                    <div className="text-sm text-green-700 opacity-90">您的许可证有效，感谢您的支持！</div>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">激活码</label>
                    <div className="flex gap-3">
                      <input 
                        type="text" 
                        value={activationCode}
                        onChange={(e) => {
                          setActivationCode(e.target.value);
                          setError('');
                        }}
                        placeholder="XXXX-XXXX-XXXX-XXXX"
                        className={cn(
                          "flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500/20 font-mono text-sm uppercase",
                          error ? "border-red-300 focus:border-red-500 focus:ring-red-500/20" : "border-gray-300 focus:border-indigo-500"
                        )}
                      />
                      <button 
                        onClick={handleActivate}
                        className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors shadow-sm whitespace-nowrap"
                      >
                        激活
                      </button>
                    </div>
                    {error && (
                      <div className="flex items-center gap-1.5 text-red-600 text-sm mt-2">
                        <AlertCircle size={14} />
                        {error}
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-gray-400">
                    还没有激活码？ <a href="#" className="text-indigo-600 hover:underline">点击购买</a> 或 <a href="#" className="text-indigo-600 hover:underline">联系支持</a>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* General Settings Placeholders */}
          <section className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="p-6 border-b border-gray-100 bg-gray-50/50">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                <Settings size={20} className="text-gray-600" />
                常规设置
              </h2>
            </div>
            <div className="p-0 divide-y divide-gray-100">
              <div className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center">
                    <Monitor size={18} />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">外观主题</div>
                    <div className="text-xs text-gray-500">浅色模式 (默认)</div>
                  </div>
                </div>
                <button className="text-sm text-gray-500 hover:text-indigo-600">更改</button>
              </div>
              
              <div className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center">
                    <Globe size={18} />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">语言</div>
                    <div className="text-xs text-gray-500">简体中文</div>
                  </div>
                </div>
                <button className="text-sm text-gray-500 hover:text-indigo-600">更改</button>
              </div>

              <div className="p-4 flex items-center justify-between hover:bg-gray-50 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center">
                    <Shield size={18} />
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">隐私与安全</div>
                    <div className="text-xs text-gray-500">管理数据权限</div>
                  </div>
                </div>
                <button className="text-sm text-gray-500 hover:text-indigo-600">查看</button>
              </div>
            </div>
          </section>

          {/* About Section */}
          <section className="text-center pt-8 pb-4">
            <div className="w-12 h-12 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-indigo-200 mx-auto mb-4">
              iML
            </div>
            <h3 className="text-gray-900 font-medium">iML Agent Desktop</h3>
            <p className="text-gray-500 text-sm mt-1">Version 1.0.0 (Beta)</p>
            <div className="flex items-center justify-center gap-4 mt-4 text-sm text-gray-400">
              <a href="#" className="hover:text-gray-600">服务条款</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-600">隐私政策</a>
              <span>•</span>
              <a href="#" className="hover:text-gray-600">检查更新</a>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
