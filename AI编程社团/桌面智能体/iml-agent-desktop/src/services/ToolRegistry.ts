
export interface Tool {
  name: string;
  description: string;
  parameters: {
    type: string;
    properties: Record<string, any>;
    required?: string[];
  };
  execute: (args: any) => Promise<string>;
}

class ToolRegistry {
  private tools: Map<string, Tool> = new Map();

  register(tool: Tool) {
    this.tools.set(tool.name, tool);
  }

  getTools(): Tool[] {
    return Array.from(this.tools.values());
  }

  getTool(name: string): Tool | undefined {
    return this.tools.get(name);
  }

  async execute(name: string, args: any): Promise<string> {
    const tool = this.tools.get(name);
    if (!tool) {
      throw new Error(`Tool ${name} not found`);
    }
    try {
      return await tool.execute(args);
    } catch (error: any) {
      return `Error executing tool ${name}: ${error.message}`;
    }
  }

  getSystemPrompt(): string {
    const toolsDesc = this.getTools().map(t => {
      return `Tool: ${t.name}
Description: ${t.description}
Parameters: ${JSON.stringify(t.parameters)}`;
    }).join('\n\n');

    return `You are an intelligent agent with access to the following tools:

${toolsDesc}

To use a tool, you MUST format your response strictly as a JSON block like this:
\`\`\`json
{
  "tool": "tool_name",
  "args": {
    "arg_name": "value"
  }
}
\`\`\`

When you receive the tool result, use it to answer the user's question.
If you don't need to use a tool, just answer normally.
`;
  }
}

export const toolRegistry = new ToolRegistry();

// Register default tools
toolRegistry.register({
  name: 'open_browser',
  description: 'Open a URL in the default web browser',
  parameters: {
    type: 'object',
    properties: {
      url: { type: 'string', description: 'The URL to open' }
    },
    required: ['url']
  },
  execute: async ({ url }) => {
    // In a real Electron app, we would use shell.openExternal(url)
    // Since we are in renderer, we can use window.open or better, call main process
    // For now, let's use window.open which might be blocked or open a new tab
    try {
        window.open(url, '_blank');
        return `Successfully opened ${url}`;
    } catch (e) {
        return `Failed to open ${url}`;
    }
  }
});

// We can add more tools here later, like 'search_web' (simulated) or 'calculator'
toolRegistry.register({
    name: 'calculator',
    description: 'Perform a mathematical calculation',
    parameters: {
        type: 'object',
        properties: {
            expression: { type: 'string', description: 'The mathematical expression to evaluate (e.g., "2 + 2")' }
        },
        required: ['expression']
    },
    execute: async ({ expression }) => {
        try {
            // Safety: simple eval is dangerous, but for a demo local agent controlled by user it's acceptable-ish
            // Better to use a safe math parser, but for now:
            // eslint-disable-next-line no-eval
            const result = eval(expression);
            return `${result}`;
        } catch (e) {
            return `Error calculating: ${e}`;
        }
    }
});

// System command execution tool
toolRegistry.register({
    name: 'execute_command',
    description: 'Execute a terminal command on the local system and return the output',
    parameters: {
        type: 'object',
        properties: {
            command: { type: 'string', description: 'The terminal command to execute (e.g., "dir", "ls", "node -v")' }
        },
        required: ['command']
    },
    execute: async ({ command }) => {
        try {
            if (window.fileSystem) {
                const result = await window.fileSystem.executeCommand(command);
                if (result.success) {
                    return `Command executed successfully:\n\nSTDOUT:\n${result.stdout || '(no output)'}\n\nSTDERR:\n${result.stderr || '(no errors)'}`;
                } else {
                    return `Command failed:\n\nError: ${result.error}\n\nSTDOUT:\n${result.stdout || '(no output)'}\n\nSTDERR:\n${result.stderr || '(no errors)'}`;
                }
            } else {
                return 'Error: Terminal execution is only available in Electron app';
            }
        } catch (e: any) {
            return `Error executing command: ${e.message}`;
        }
    }
});

// Web search tool
toolRegistry.register({
    name: 'web_search',
    description: 'Search the web for information using a search engine',
    parameters: {
        type: 'object',
        properties: {
            query: { type: 'string', description: 'The search query' },
            num_results: { type: 'number', description: 'Number of results to return (default: 5)', default: 5 }
        },
        required: ['query']
    },
    execute: async ({ query, num_results = 5 }) => {
        try {
            // Use DuckDuckGo HTML search (no API key required)
            const response = await fetch(
                `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`,
                { method: 'GET' }
            );
            const html = await response.text();

            // Parse results from HTML (simple regex approach)
            const results: string[] = [];
            const resultRegex = /<a class="result__a" href="([^"]+)"[^>]*>([^<]+)<\/a>/g;
            let match;
            let count = 0;

            while ((match = resultRegex.exec(html)) !== null && count < num_results) {
                const title = match[2].replace(/<[^>]+>/g, '').trim();
                const url = match[1];
                results.push(`${count + 1}. ${title}\n   URL: ${url}`);
                count++;
            }

            if (results.length === 0) {
                return `No search results found for "${query}"`;
            }

            return `Search results for "${query}":\n\n${results.join('\n\n')}`;
        } catch (e: any) {
            return `Search failed: ${e.message}`;
        }
    }
});

// Open URL in browser
toolRegistry.register({
    name: 'open_url',
    description: 'Open a URL in the default web browser',
    parameters: {
        type: 'object',
        properties: {
            url: { type: 'string', description: 'The URL to open' }
        },
        required: ['url']
    },
    execute: async ({ url }) => {
        try {
            if (window.fileSystem) {
                const result = await window.fileSystem.openExternal(url);
                if (result.success) {
                    return `Successfully opened ${url} in browser`;
                } else {
                    return `Failed to open URL: ${result.error}`;
                }
            } else {
                // Fallback to window.open for browser preview
                window.open(url, '_blank');
                return `Opened ${url} in new tab`;
            }
        } catch (e: any) {
            return `Error opening URL: ${e.message}`;
        }
    }
});
