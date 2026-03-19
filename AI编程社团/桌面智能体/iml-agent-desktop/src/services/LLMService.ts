interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  apiKey: string;
  baseUrl?: string;
}

export class LLMService {
  private config: ModelConfig;

  constructor(config: ModelConfig) {
    this.config = config;
  }

  async chat(messages: ChatMessage[], onStream?: (chunk: string) => void): Promise<string> {
    try {
      const baseUrl = this.config.baseUrl || (
        this.config.provider === 'anthropic' 
          ? 'https://api.anthropic.com' 
          : 'https://api.openai.com/v1'
      );

      if (this.config.provider === 'anthropic') {
        const endpoint = `${baseUrl.replace(/\/+$/, '')}/v1/messages`;
        
        // Extract system message if present
        const systemMessage = messages.find(m => m.role === 'system');
        const chatMessages = messages.filter(m => m.role !== 'system');

        const body: any = {
          model: this.config.name || 'claude-3-sonnet-20240229',
          messages: chatMessages.map(m => ({
            role: m.role,
            content: m.content
          })),
          max_tokens: 4096,
          stream: !!onStream
        };

        if (systemMessage) {
          body.system = systemMessage.content;
        }
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'x-api-key': this.config.apiKey,
            'anthropic-version': '2023-06-01',
            'anthropic-dangerous-direct-browser-access': 'true'
          },
          body: JSON.stringify(body)
        });

        if (!response.ok) {
          const error = await response.json().catch(() => ({}));
          throw new Error(error.error?.message || `API request failed with status ${response.status}`);
        }

        if (onStream && response.body) {
          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let fullContent = '';

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  if (data.type === 'content_block_delta' && data.delta?.text) {
                    onStream(data.delta.text);
                    fullContent += data.delta.text;
                  }
                } catch (e) {
                  // Ignore parse errors for ping/metadata events
                }
              }
            }
          }
          return fullContent;
        } else {
          const data = await response.json();
          return data.content[0]?.text || '';
        }
      }

      // Default to OpenAI compatible
      const endpoint = `${baseUrl.replace(/\/+$/, '')}/chat/completions`;
      
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.config.apiKey}`
        },
        body: JSON.stringify({
          model: this.config.name,
          messages: messages,
          stream: !!onStream
        })
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error?.message || `API request failed with status ${response.status}`);
      }

      if (onStream && response.body) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          
          for (const line of lines) {
            if (line.startsWith('data: ') && line !== 'data: [DONE]') {
              try {
                const data = JSON.parse(line.slice(6));
                const content = data.choices[0]?.delta?.content || '';
                if (content) {
                  onStream(content);
                  fullContent += content;
                }
              } catch (e) {
                console.warn('Failed to parse stream chunk:', line);
              }
            }
          }
        }
        return fullContent;
      } else {
        const data = await response.json();
        return data.choices[0]?.message?.content || '';
      }
    } catch (error) {
      console.error('LLM Service Error:', error);
      throw error;
    }
  }
}
