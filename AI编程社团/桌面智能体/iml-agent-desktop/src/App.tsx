import React, { useState, useEffect } from 'react';
import SkillsView from './components/SkillsView';
import ModelsView from './components/ModelsView';
import SettingsView from './components/SettingsView';
import {
  MessageSquare,
  LayoutGrid,
  Settings,
  Database,
  Plus,
  Send,
  Paperclip,
  Mic,
  Box,
  File,
  Layers,
  Trash2,
  Play,
  Code2,
  X,
  Copy,
  Check
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { initialSkills } from './data/mockData';
import { NavItem, IconButton, TabButton } from './components/ui/Buttons';
import { LLMService } from './services/LLMService';
import { toolRegistry } from './services/ToolRegistry';
import { getIconComponent } from './utils/iconMap';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function App() {
  const [activeTab, setActiveTab] = useState('artifacts');
  const [currentView, setCurrentView] = useState<'chat' | 'skills' | 'models' | 'settings'>('chat');
  const [skills, setSkills] = useState(initialSkills);
  const [models, setModels] = useState<any[]>([]);
  
  // Chat state
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<{ path: string; name: string; content: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [llmService, setLlmService] = useState<LLMService | null>(null);

  // Code sandbox state
  const [extractedCodes, setExtractedCodes] = useState<{ id: string; language: string; code: string; result?: string }[]>([]);
  const [runningCodeId, setRunningCodeId] = useState<string | null>(null);
  const [copiedCodeId, setCopiedCodeId] = useState<string | null>(null);
  const [previewHtml, setPreviewHtml] = useState<string | null>(null);

  // Load persistence data
  useEffect(() => {
    const loadData = async () => {
      try {
        let savedSkills = [];
        let savedModels = [];
        let savedSessions = [];
        let lastSessionId = null;

        if (window.electronStore) {
          savedSkills = await window.electronStore.get('skills');
          savedModels = await window.electronStore.get('models');
          savedSessions = await window.electronStore.get('sessions');
          lastSessionId = await window.electronStore.get('lastSessionId');
        } else {
          // Fallback to localStorage for browser
          const localSkills = localStorage.getItem('skills');
          const localModels = localStorage.getItem('models');
          const localSessions = localStorage.getItem('sessions');
          lastSessionId = localStorage.getItem('lastSessionId');
          
          if (localSkills) savedSkills = JSON.parse(localSkills);
          if (localModels) savedModels = JSON.parse(localModels);
          if (localSessions) savedSessions = JSON.parse(localSessions);
        }

        if (Array.isArray(savedSkills) && savedSkills.length > 0) {
          setSkills(savedSkills);
        }
        
        if (Array.isArray(savedSessions)) {
          setSessions(savedSessions);
          // Load last session or create new
          if (lastSessionId) {
            const lastSession = savedSessions.find((s: any) => s.id === lastSessionId);
            if (lastSession) {
              setMessages(lastSession.messages);
              setCurrentSessionId(lastSessionId);
            }
          }
        }
        
        let currentModels = [];
        if (Array.isArray(savedModels)) {
          currentModels = savedModels;
        }

        // Auto-configure MiniMax if requested
        const miniMaxId = 'minimax-auto-config';
        const hasMiniMax = currentModels.some((m: any) => m.id === miniMaxId);
        
        if (!hasMiniMax) {
          const miniMaxModel = {
            id: miniMaxId,
            name: 'MiniMax-abab6.5',
            provider: 'anthropic',
            apiKey: 'sk-cp-JkoVLSRWdmzgvE7LBzZy3LQfOpIIDNbqYLuqW2OfkNyDmX1qq97CTJUbFw9mhyyLD0WVQBvWhxlqzt2jHWZcLjlVSQeUM9ZNGyvtrG2J2kSXkJA7qUo7Swg',
            baseUrl: 'https://api.minimaxi.com/anthropic',
            isActive: true
          };
          // Deactivate others
          currentModels = currentModels.map((m: any) => ({ ...m, isActive: false }));
          currentModels.push(miniMaxModel);
        }

        setModels(currentModels);
        const activeModel = currentModels.find((m: any) => m.isActive);
        if (activeModel) {
          setLlmService(new LLMService(activeModel));
        }

      } catch (error) {
        console.error('Failed to load data from store:', error);
      }
    };
    loadData();
  }, []);

  // Save sessions and current session
  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      const updatedSessions = sessions.map(s => 
        s.id === currentSessionId 
          ? { ...s, messages: messages, preview: messages[messages.length-1].content.substring(0, 50), time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) } 
          : s
      );
      
      // If current session not found in list (newly created), add it
      if (!sessions.find(s => s.id === currentSessionId)) {
         const newSession = {
            id: currentSessionId,
            title: messages[0].content.substring(0, 20) || '新对话',
            messages: messages,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            preview: messages[messages.length-1].content.substring(0, 50)
         };
         setSessions([newSession, ...sessions]);
         return; // updatedSessions will be stale, let next render handle it or rely on setSessions merging? 
         // Actually better to just setSessions directly here
      } else {
         setSessions(updatedSessions);
      }
    }
  }, [messages]);

  // Persist sessions to store
  useEffect(() => {
    if (window.electronStore) {
      window.electronStore.set('sessions', sessions);
      if (currentSessionId) window.electronStore.set('lastSessionId', currentSessionId);
    } else {
      localStorage.setItem('sessions', JSON.stringify(sessions));
      if (currentSessionId) localStorage.setItem('lastSessionId', currentSessionId);
    }
  }, [sessions, currentSessionId]);

  // Save skills
  useEffect(() => {
    if (skills !== initialSkills) {
      if (window.electronStore) {
        window.electronStore.set('skills', skills);
      } else {
        localStorage.setItem('skills', JSON.stringify(skills));
      }
    }
  }, [skills]);

  // Extract code blocks from messages
  useEffect(() => {
    const codes: { id: string; language: string; code: string; result?: string }[] = [];
    let hasHtml = false;
    messages.forEach((msg, msgIdx) => {
      if (msg.role === 'assistant' && msg.content) {
        // Match code blocks with language
        const codeBlockRegex = /```(\w+)?\s*([\s\S]*?)```/g;
        let match;
        while ((match = codeBlockRegex.exec(msg.content)) !== null) {
          const language = match[1] || 'text';
          const code = match[2].trim();
          if (code) {
            codes.push({
              id: `code-${msgIdx}-${codes.length}`,
              language,
              code,
            });
            if (language === 'html') {
              hasHtml = true;
            }
          }
        }
      }
    });
    setExtractedCodes(codes);

    // Auto-preview HTML if found
    if (hasHtml) {
      const htmlCode = codes.find(c => c.language === 'html');
      if (htmlCode) {
        setPreviewHtml(htmlCode.code);
      }
    }
  }, [messages]);

  // Run code in sandbox
  const handleRunCode = async (codeId: string) => {
    const codeItem = extractedCodes.find(c => c.id === codeId);
    if (!codeItem) return;

    setRunningCodeId(codeId);

    try {
      if (codeItem.language === 'javascript' || codeItem.language === 'js') {
        // Execute JavaScript in a sandboxed way
        const logs: string[] = [];
        const originalLog = console.log;
        const originalError = console.error;

        console.log = (...args) => logs.push(args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));
        console.error = (...args) => logs.push('[Error] ' + args.map(a => typeof a === 'object' ? JSON.stringify(a) : String(a)).join(' '));

        try {
          // eslint-disable-next-line no-new-func
          const fn = new Function(codeItem.code);
          fn();
          const result = logs.length > 0 ? logs.join('\n') : 'Code executed successfully (no output)';
          setExtractedCodes(prev => prev.map(c => c.id === codeId ? { ...c, result } : c));
        } catch (e: any) {
          setExtractedCodes(prev => prev.map(c => c.id === codeId ? { ...c, result: `Error: ${e.message}` } : c));
        } finally {
          console.log = originalLog;
          console.error = originalError;
        }
      } else if (codeItem.language === 'python' || codeItem.language === 'py') {
        // Execute Python via command (requires Python installed)
        if (window.fileSystem) {
          const result = await window.fileSystem.executeCommand(`python -c "${codeItem.code.replace(/"/g, '\\"').replace(/\n/g, '; ')}"`);
          const output = result.success ? (result.stdout || '(no output)') : `Error: ${result.error}`;
          setExtractedCodes(prev => prev.map(c => c.id === codeId ? { ...c, result: output } : c));
        } else {
          setExtractedCodes(prev => prev.map(c => c.id === codeId ? { ...c, result: 'Python execution is only available in Electron app' } : c));
        }
      } else {
        setExtractedCodes(prev => prev.map(c => c.id === codeId ? { ...c, result: `Unsupported language: ${codeItem.language}` } : c));
      }
    } finally {
      setRunningCodeId(null);
    }
  };

  // Copy code to clipboard
  const handleCopyCode = async (codeId: string) => {
    const codeItem = extractedCodes.find(c => c.id === codeId);
    if (codeItem) {
      await navigator.clipboard.writeText(codeItem.code);
      setCopiedCodeId(codeId);
      setTimeout(() => setCopiedCodeId(null), 2000);
    }
  };

  // Save models
  useEffect(() => {
    if (models.length > 0) { // Only save if we have models
      if (window.electronStore) {
        window.electronStore.set('models', models);
      } else {
        localStorage.setItem('models', JSON.stringify(models));
      }
      
      const activeModel = models.find((m: any) => m.isActive);
      if (activeModel) {
        setLlmService(new LLMService(activeModel));
      }
    }
  }, [models]);

  const handleSendMessage = async (customInput?: string) => {
    const textToSend = customInput || input;
    if (!textToSend.trim() || isLoading) return;

    // Ensure we have a session ID
    let sessionId = currentSessionId;
    if (!sessionId) {
      sessionId = Math.random().toString(36).substr(2, 9);
      setCurrentSessionId(sessionId);
      // Create initial session entry
      setSessions(prev => [{
        id: sessionId!,
        title: textToSend.substring(0, 15) + '...',
        messages: [],
        time: 'Just now',
        preview: ''
      }, ...prev]);
    }

    let finalInput = textToSend;
    if (selectedFile) {
      finalInput = `[Context: User uploaded a file named "${selectedFile.name}"]\n\nFile Content:\n\`\`\`\n${selectedFile.content}\n\`\`\`\n\nUser Question: ${textToSend}`;
      setSelectedFile(null); // Clear selected file after sending
    }

    const userMessage = { role: 'user', content: finalInput };
    // Optimistically update UI with user message
    const newMessages = [...messages, userMessage];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      if (!llmService) {
        throw new Error('No active model selected. Please configure a model in settings.');
      }

      await processChatTurn(newMessages, llmService);

    } catch (error: any) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Error: ${error.message || 'Something went wrong'}` 
      }]);
      setIsLoading(false);
    }
  };

  const processChatTurn = async (currentMessages: any[], service: LLMService) => {
      // Add assistant placeholder
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      // Prepare messages with system prompt
      const systemPrompt = toolRegistry.getSystemPrompt();
      const messagesToSend = [
        { role: 'system', content: systemPrompt },
        ...currentMessages
      ];

      let fullContent = '';
      await service.chat(messagesToSend, (chunk) => {
        fullContent += chunk;
        setMessages(prev => {
          const msgs = [...prev];
          msgs[msgs.length - 1] = { role: 'assistant', content: fullContent };
          return msgs;
        });
      });

      // Check for tool calls
      const toolBlockMatch = fullContent.match(/```json\s*(\{[\s\S]*?"tool"[\s\S]*?\})\s*```/);
      if (toolBlockMatch) {
        try {
          const toolData = JSON.parse(toolBlockMatch[1]);
          const { tool, args } = toolData;
          
          // Execute tool
          const result = await toolRegistry.execute(tool, args);
          
          // Add tool result to history and continue chat
          const resultMessage = { 
            role: 'user', 
            content: `[Tool Output for ${tool}]\n${result}\n\nPlease use this result to answer my previous question.` 
          };
          
          const updatedMessages = [
            ...currentMessages, 
            { role: 'assistant', content: fullContent },
            resultMessage
          ];
          
          setMessages(prev => [...prev, resultMessage]);
          
          // Recursive call for next turn
          await processChatTurn(updatedMessages, service);
          
        } catch (e) {
          console.error('Failed to parse or execute tool:', e);
        }
      } else {
        setIsLoading(false);
      }
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentSessionId(null);
    setCurrentView('chat');
  };

  const handleLoadSession = (session: any) => {
    setMessages(session.messages);
    setCurrentSessionId(session.id);
    setCurrentView('chat');
  };

  const handleSkillClick = (skill: any) => {
    // If we are in skills view, switch to chat first
    if (currentView !== 'chat') {
      setCurrentView('chat');
    }
    
    let prompt = `帮我使用技能 "${skill.title}"`;
    if (skill.tag === 'imported-skill') {
      prompt = `我已安装了外部技能 "${skill.title}" (来源: ${skill.desc})。请根据该项目的特性，告诉我这个技能可以用来做什么，并演示如何使用它。`;
    }
    
    handleSendMessage(prompt);
  };

  const handleImportSkill = (skill: any) => {
    setSkills(prev => [...prev, skill]);
  };

  const handleFileUpload = async () => {
    if (window.fileSystem) {
      try {
        const file = await window.fileSystem.selectFile();
        if (file) {
          setSelectedFile(file);
          setActiveTab('files'); // Switch to files tab to show uploaded file
        }
      } catch (error) {
        console.error('Failed to upload file:', error);
        alert('文件读取失败，请重试');
      }
    } else {
      alert('当前环境不支持文件上传功能');
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      try {
        // Only support text files for now
        const text = await file.text();
        setSelectedFile({
          path: (file as any).path || '', // Electron exposes path on File object
          name: file.name,
          content: text
        });
        setActiveTab('files');
      } catch (err) {
        console.error('Failed to read dropped file', err);
        alert('无法读取该文件，请确认是文本文件');
      }
    }
  };

  const handleAddSkill = (skill: any) => {
    // Assign a random icon/color if not provided (mock logic)
    const newSkill = {
      ...skill,
      iconName: 'box', // Default icon
      color: 'bg-gray-100 text-gray-600', // Default color
      id: Math.random().toString(36).substr(2, 9)
    };
    setSkills([...skills, newSkill]);
  };

  const handleAddModel = (model: any) => {
    const newModels = models.map(m => ({ ...m, isActive: false }));
    setModels([...newModels, { ...model, isActive: true }]);
  };

  const handleDeleteModel = (id: string) => {
    setModels(models.filter(m => m.id !== id));
  };

  const handleUpdateModel = (id: string, updates: any) => {
    let newModels = models.map(m => m.id === id ? { ...m, ...updates } : m);
    
    if (updates.isActive) {
      newModels = newModels.map(m => m.id === id ? m : { ...m, isActive: false });
    }
    
    setModels(newModels);
  };

  const handleClearHistory = () => {
    if (confirm('确定要清空所有对话历史吗？')) {
      setMessages([]);
      if (window.electronStore) {
        window.electronStore.delete('chatHistory');
      }
    }
  };

  const renderContent = () => {
    switch (currentView) {
      case 'skills':
        return <SkillsView 
          skills={skills} 
          onAddSkill={handleAddSkill} 
          onImportSkill={handleImportSkill}
          onUseSkill={handleSkillClick}
        />;
      case 'models':
        return <ModelsView 
          models={models} 
          onAddModel={handleAddModel} 
          onDeleteModel={handleDeleteModel}
          onUpdateModel={handleUpdateModel}
        />;
      case 'settings':
        return <SettingsView />;
      default:
        return (
          <>
            {/* 2. History Panel */}
            <div className="w-72 flex flex-col border-r border-gray-200 bg-gray-50/50">
              <div className="p-4">
                <div className="text-xs font-semibold text-gray-500 mb-2 uppercase tracking-wider">历史记录</div>
                <button 
                  onClick={handleNewChat}
                  className="w-full bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg py-2.5 px-4 flex items-center justify-center gap-2 transition-colors shadow-sm font-medium text-sm"
                >
                  <Plus size={18} />
                  新对话
                </button>
              </div>

              <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
                {sessions.length === 0 ? (
                  <div className="text-center py-8 text-gray-400 text-sm">
                    暂无历史记录
                  </div>
                ) : (
                  sessions.map((session) => (
                    <div 
                      key={session.id} 
                      onClick={() => handleLoadSession(session)}
                      className={cn(
                        "group flex flex-col p-3 rounded-lg cursor-pointer transition-colors",
                        currentSessionId === session.id ? "bg-indigo-50 border border-indigo-100" : "hover:bg-gray-100 border border-transparent"
                      )}
                    >
                      <div className={cn(
                        "font-medium text-sm truncate",
                        currentSessionId === session.id ? "text-indigo-900" : "text-gray-700 group-hover:text-gray-900"
                      )}>
                        {session.title}
                      </div>
                      <div className={cn(
                        "text-xs mt-1 truncate",
                        currentSessionId === session.id ? "text-indigo-400" : "text-gray-400"
                      )}>
                        {session.time} · {session.messages.length} 条消息
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* 3. Main Chat Area */}
            <div 
              className="flex-1 flex flex-col bg-white min-w-0"
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              {/* Header */}
              <header className="h-14 border-b border-gray-100 flex items-center px-6 justify-between bg-white">
                <div className="text-sm text-gray-500">
                  <span className="font-semibold text-gray-800">iML Agent Desktop</span>
                  <span className="mx-2">/</span>
                  <span>对话</span>
                </div>
                <div className="flex gap-2">
                  {messages.length > 0 && (
                    <button 
                      onClick={handleClearHistory}
                      className="p-1.5 hover:bg-red-50 text-gray-400 hover:text-red-500 rounded transition-colors"
                      title="清空对话"
                    >
                      <Trash2 size={18} />
                    </button>
                  )}
                  <button 
                    onClick={() => setCurrentView('skills')}
                    className="p-1.5 hover:bg-gray-100 rounded text-gray-400"
                    title="管理技能"
                  >
                    <LayoutGrid size={18} />
                  </button>
                </div>
              </header>

              {/* Chat Content */}
              <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-3xl mx-auto space-y-8">
                  
                  {messages.length === 0 ? (
                    /* Agent Greeting */
                    <div className="flex gap-4">
                      <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
                        <Box size={18} />
                      </div>
                      <div className="space-y-6 flex-1">
                        <div className="bg-gray-50 rounded-2xl rounded-tl-none p-5 text-gray-700 shadow-sm border border-gray-100">
                          <p>你好！我是 iML Agent，你的桌面级智能体助手。请选择一个技能，或者直接告诉我你的需求。</p>
                        </div>

                        {/* Skill Cards */}
                        <div>
                          <h3 className="text-lg font-semibold text-gray-800 mb-4 border-l-4 border-indigo-600 pl-3">您想要做什么？</h3>
                          <div className="grid grid-cols-1 gap-3">
                            {skills.map((skill) => {
                              const Icon = getIconComponent(skill.iconName);
                              return (
                              <div 
                                key={skill.id} 
                                onClick={() => handleSkillClick(skill)}
                                className="flex items-start gap-4 p-4 border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-md transition-all cursor-pointer bg-white group"
                              >
                                <div className={cn("w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-colors", skill.color)}>
                                  <Icon size={20} />
                                </div>
                                <div className="flex-1 min-w-0">
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{skill.title}</span>
                                    <span className="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs rounded-full font-mono">{skill.tag}</span>
                                  </div>
                                  <p className="text-sm text-gray-500 truncate">{skill.desc}</p>
                                </div>
                                <div className="text-gray-300 group-hover:text-indigo-400">→</div>
                              </div>
                            );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Chat Messages */
                    <div className="space-y-6">
                      {messages.map((msg, idx) => (
                        <div key={idx} className={cn("flex gap-4", msg.role === 'user' ? "flex-row-reverse" : "")}>
                          <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                            msg.role === 'user' ? "bg-gray-200 text-gray-600" : "bg-indigo-100 text-indigo-600"
                          )}>
                            {msg.role === 'user' ? <span className="text-xs font-bold">You</span> : <Box size={18} />}
                          </div>
                          <div className={cn("flex flex-col max-w-[80%]", msg.role === 'user' ? "items-end" : "items-start")}>
                            {msg.role !== 'user' && <span className="text-xs text-gray-400 mb-1 ml-1">iML Agent</span>}
                            <div className={cn(
                              "p-4 rounded-2xl shadow-sm",
                              msg.role === 'user' ? "bg-indigo-600 text-white rounded-tr-none" : "bg-white border border-gray-100 text-gray-700 rounded-tl-none"
                            )}>
                              <div className="whitespace-pre-wrap">{msg.content}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                      {isLoading && (
                        <div className="flex gap-4">
                          <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600 shrink-0">
                            <Box size={18} />
                          </div>
                          <div className="flex flex-col">
                            <span className="text-xs text-gray-400 mb-1 ml-1">iML Agent</span>
                            <div className="bg-white border border-gray-100 p-4 rounded-2xl rounded-tl-none text-gray-400 text-sm flex items-center gap-2">
                              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
                              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75" />
                              <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150" />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                </div>
              </div>

              {/* Input Area */}
              <div className="p-6 pt-2">
                <div className="max-w-3xl mx-auto relative">
                  <div className="absolute top-0 left-0 right-0 h-12 bg-gradient-to-t from-white to-transparent -translate-y-full pointer-events-none"></div>
                  {selectedFile && (
                    <div className="mb-2 p-2 bg-indigo-50 border border-indigo-100 rounded-lg flex items-center justify-between">
                      <div className="flex items-center gap-2 text-sm text-indigo-900 truncate">
                        <File size={16} className="text-indigo-500" />
                        <span className="truncate max-w-[200px]">{selectedFile.name}</span>
                      </div>
                      <button onClick={() => setSelectedFile(null)} className="text-indigo-400 hover:text-indigo-600">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  )}
                  <div className="border border-gray-300 rounded-2xl shadow-sm bg-white overflow-hidden focus-within:ring-2 focus-within:ring-indigo-100 focus-within:border-indigo-400 transition-all">
                    <textarea  
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="问我任何问题..." 
                      className="w-full p-4 max-h-40 resize-none outline-none text-gray-700 placeholder:text-gray-400"
                      rows={1}
                    />
                    <div className="flex items-center justify-between px-3 pb-3">
                      <div className="flex gap-1">
                        <IconButton icon={Paperclip} onClick={handleFileUpload} />
                        <IconButton icon={Mic} onClick={() => alert('语音输入功能即将上线')} />
                      </div>
                      <button 
                        onClick={() => handleSendMessage()}
                        disabled={!input.trim() || isLoading}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg p-2 transition-colors"
                      >
                        <Send size={16} />
                      </button>
                    </div>
                  </div>
                  <div className="text-center text-xs text-gray-400 mt-2">
                    AI 生成的内容可能不准确。请核实重要信息。
                  </div>
                </div>
              </div>
            </div>

            {/* 4. Right Panel (Context/Artifacts) */}
            <div className="w-80 border-l border-gray-200 bg-white flex flex-col">
              {/* Spacer for Window Controls */}
              <div className="h-8 w-full bg-white drag-region shrink-0"></div>
              <div className="flex border-b border-gray-200">
                <TabButton active={activeTab === 'preview'} onClick={() => setActiveTab('preview')} icon={Code2} label="预览" />
                <TabButton active={activeTab === 'artifacts'} onClick={() => setActiveTab('artifacts')} icon={Box} label="产物" />
                <TabButton active={activeTab === 'files'} onClick={() => setActiveTab('files')} icon={File} label="文件" />
                <TabButton active={activeTab === 'context'} onClick={() => setActiveTab('context')} icon={Layers} label="上下文" />
              </div>
              
              <div className="flex-1 flex flex-col items-center justify-center text-gray-400 p-8 text-center overflow-y-auto">
                {activeTab === 'preview' && (
                  previewHtml ? (
                    <div className="w-full h-full flex flex-col">
                      <div className="flex items-center justify-between mb-2 px-1">
                        <span className="text-xs font-medium text-gray-600">HTML 预览</span>
                        <button
                          onClick={() => setPreviewHtml(null)}
                          className="p-1 hover:bg-gray-200 rounded"
                          title="关闭预览"
                        >
                          <X size={14} />
                        </button>
                      </div>
                      <iframe
                        srcDoc={previewHtml}
                        className="flex-1 w-full border border-gray-200 rounded-lg bg-white"
                        sandbox="allow-scripts"
                        title="HTML Preview"
                      />
                    </div>
                  ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                        <Code2 size={32} className="opacity-20" />
                      </div>
                      <p className="text-sm">暂无 HTML 预览</p>
                      <p className="text-xs text-gray-300 mt-2">AI 生成的 HTML 代码将显示在这里</p>
                    </>
                  )
                )}

                {activeTab === 'artifacts' && (
                   extractedCodes.length > 0 ? (
                    <div className="w-full h-full space-y-4 text-left overflow-y-auto">
                       {extractedCodes.map((codeItem, idx) => (
                         <div key={codeItem.id} className="bg-gray-50 rounded-lg p-3 text-xs border border-gray-200">
                            <div className="flex items-center justify-between mb-2">
                              <div className="flex items-center gap-2">
                                <Code2 size={14} className="text-indigo-500" />
                                <span className="font-medium text-gray-600">代码片段 {idx + 1}</span>
                                <span className="px-1.5 py-0.5 bg-indigo-100 text-indigo-600 text-[10px] rounded">{codeItem.language}</span>
                              </div>
                              <div className="flex gap-1">
                                <button
                                  onClick={() => handleRunCode(codeItem.id)}
                                  disabled={runningCodeId === codeItem.id}
                                  className="p-1 hover:bg-green-100 text-green-600 rounded transition-colors disabled:opacity-50"
                                  title="运行代码"
                                >
                                  {runningCodeId === codeItem.id ? (
                                    <div className="w-3 h-3 border-2 border-green-600 border-t-transparent rounded-full animate-spin" />
                                  ) : (
                                    <Play size={14} />
                                  )}
                                </button>
                                <button
                                  onClick={() => handleCopyCode(codeItem.id)}
                                  className="p-1 hover:bg-blue-100 text-blue-600 rounded transition-colors"
                                  title="复制代码"
                                >
                                  {copiedCodeId === codeItem.id ? <Check size={14} /> : <Copy size={14} />}
                                </button>
                              </div>
                            </div>
                            <pre className="overflow-x-auto p-2 bg-gray-800 text-gray-100 rounded text-[11px] max-h-32">{codeItem.code}</pre>
                            {codeItem.result && (
                              <div className="mt-2 p-2 bg-gray-900 rounded text-green-400 text-[10px] whitespace-pre-wrap">
                                {codeItem.result}
                              </div>
                            )}
                         </div>
                       ))}
                    </div>
                   ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                        <Box size={32} className="opacity-20" />
                      </div>
                      <p className="text-sm">暂无生成的产物</p>
                      <p className="text-xs text-gray-300 mt-2">AI 生成的代码或内容将显示在这里</p>
                    </>
                   )
                )}

                {activeTab === 'files' && (
                  selectedFile || messages.some(m => m.content.includes('[Context: User uploaded a file')) ? (
                    <div className="w-full h-full text-left space-y-2">
                       {selectedFile && (
                          <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-lg flex items-center gap-2">
                             <File size={20} className="text-indigo-600" />
                             <div className="flex-1 min-w-0">
                                <div className="text-sm font-medium text-indigo-900 truncate">{selectedFile.name}</div>
                                <div className="text-xs text-indigo-500">当前待发送</div>
                             </div>
                          </div>
                       )}
                       {messages.filter(m => m.content.includes('[Context: User uploaded a file')).map((m, idx) => {
                          const fileName = m.content.match(/named "([^"]+)"/)?.[1] || 'Unknown File';
                          return (
                            <div key={idx} className="p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center gap-2">
                               <File size={20} className="text-gray-500" />
                               <div className="flex-1 min-w-0">
                                  <div className="text-sm font-medium text-gray-700 truncate">{fileName}</div>
                                  <div className="text-xs text-gray-400">已上传</div>
                               </div>
                            </div>
                          );
                       })}
                    </div>
                  ) : (
                    <>
                      <div className="w-16 h-16 bg-gray-50 rounded-2xl flex items-center justify-center mb-4">
                        <File size={32} className="opacity-20" />
                      </div>
                      <p className="text-sm">暂无文件</p>
                    </>
                  )
                )}

                {activeTab === 'context' && (
                  <div className="w-full h-full text-left space-y-4">
                     <div className="p-3 bg-gray-50 rounded-lg">
                        <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">当前模型</h4>
                        <div className="text-sm text-gray-800">{models.find(m => m.isActive)?.name || '未选择'}</div>
                     </div>
                     <div className="p-3 bg-gray-50 rounded-lg">
                        <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">会话信息</h4>
                        <div className="text-sm text-gray-800">
                          ID: {currentSessionId || '未保存'}<br/>
                          消息数: {messages.length}
                        </div>
                     </div>
                  </div>
                )}
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <div className="flex h-screen bg-white text-gray-800 font-sans">
      {/* 1. Sidebar Navigation */}
      <div className="w-16 flex flex-col items-center py-6 border-r border-gray-200 bg-white space-y-8 shrink-0">
        <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-xs shadow-lg shadow-indigo-200">
          iML
        </div>
        
        <nav className="flex flex-col space-y-6 w-full items-center">
          <NavItem 
            icon={MessageSquare} 
            active={currentView === 'chat'} 
            onClick={() => setCurrentView('chat')}
          />
          <NavItem 
            icon={LayoutGrid} 
            active={currentView === 'skills'} 
            onClick={() => setCurrentView('skills')}
          />
          <NavItem 
            icon={Database} 
            active={currentView === 'models'} 
            onClick={() => setCurrentView('models')}
          />
          <NavItem 
            icon={Settings} 
            active={currentView === 'settings'} 
            onClick={() => setCurrentView('settings')}
          />
        </nav>
      </div>

      {renderContent()}
    </div>
  );
}
