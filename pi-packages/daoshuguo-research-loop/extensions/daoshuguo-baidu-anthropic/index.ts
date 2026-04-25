import Anthropic from "@anthropic-ai/sdk";
import type { MessageCreateParamsStreaming } from "@anthropic-ai/sdk/resources/messages.js";
import type {
  Api,
  AssistantMessage,
  AssistantMessageEventStream,
  Context,
  Model,
  SimpleStreamOptions,
  StopReason,
  TextContent,
  Tool,
  ToolCall,
  ToolResultMessage,
} from "@mariozechner/pi-ai";
import {
  calculateCost,
  createAssistantMessageEventStream,
} from "@mariozechner/pi-ai";
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

function sanitize(text: string): string {
  return text.replace(/[\uD800-\uDFFF]/g, "\uFFFD");
}

function convertMessages(messages: (any)[], tools?: Tool[]): any[] {
  const params: any[] = [];
  for (const msg of messages) {
    if (msg.role === "user") {
      if (typeof msg.content === "string") {
        params.push({ role: "user", content: sanitize(msg.content) });
      } else {
        params.push({
          role: "user",
          content: msg.content.map((item: TextContent) => ({ type: "text", text: sanitize(item.text) })),
        });
      }
    } else if (msg.role === "assistant") {
      const blocks: any[] = [];
      for (const block of msg.content) {
        if (block.type === "text" && block.text.trim()) {
          blocks.push({ type: "text", text: sanitize(block.text) });
        } else if (block.type === "toolCall") {
          blocks.push({
            type: "tool_use",
            id: block.id,
            name: block.name,
            input: block.arguments,
          });
        }
      }
      params.push({ role: "assistant", content: blocks });
    } else if (msg.role === "toolResult") {
      const text = msg.content.map((c: any) => c.text ?? "").join("\n");
      params.push({
        role: "user",
        content: [
          {
            type: "tool_result",
            tool_use_id: msg.toolCallId,
            content: sanitize(text),
          },
        ],
      });
    }
  }
  return params;
}

function convertTools(tools?: Tool[]): any[] | undefined {
  if (!tools || tools.length === 0) return undefined;
  return tools.map((tool) => ({
    name: tool.name,
    description: tool.description,
    input_schema: tool.parameters,
  }));
}

function toStopReason(stopReason: string | null | undefined): StopReason {
  if (stopReason === "tool_use") return "toolUse";
  if (stopReason === "max_tokens") return "maxTokens";
  return "stop";
}

export default function daoshuguoBaiduAnthropic(pi: ExtensionAPI) {
  const token = process.env.ANTHROPIC_AUTH_TOKEN;
  const baseUrl = process.env.ANTHROPIC_BASE_URL;
  const modelId = process.env.ANTHROPIC_MODEL || "kimi-k2.5";
  if (!token || !baseUrl) return;

  pi.registerProvider("anthropic", {
    baseUrl,
    apiKey: token,
    authHeader: true,
    api: "anthropic-messages",
    models: [
      {
        id: modelId,
        name: modelId,
        reasoning: true,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 200000,
        maxTokens: 16384,
      },
    ],
    streamSimple: (
      model: Model<Api>,
      context: Context,
      options?: SimpleStreamOptions,
    ): AssistantMessageEventStream => {
      const stream = createAssistantMessageEventStream();
      const client = new Anthropic({
        apiKey: null,
        authToken: token,
        baseURL: baseUrl,
        dangerouslyAllowBrowser: true,
        defaultHeaders: {
          accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      (async () => {
        try {
          const params: MessageCreateParamsStreaming = {
            model: model.id,
            messages: convertMessages(context.messages, context.tools),
            max_tokens: options?.maxTokens || 4096,
            stream: true,
            ...(context.systemPrompt
              ? { system: [{ type: "text", text: sanitize(context.systemPrompt) }] as any }
              : {}),
            ...(context.tools ? { tools: convertTools(context.tools) as any } : {}),
          };

          const response = await client.messages.create(params);
          let text = "";
          let toolCalls: ToolCall[] = [];
          for await (const chunk of response as any) {
            if (chunk.type === "content_block_delta" && chunk.delta?.text) {
              text += chunk.delta.text;
              stream.push({ type: "text_delta", delta: chunk.delta.text });
            } else if (chunk.type === "content_block_start" && chunk.content_block?.type === "tool_use") {
              toolCalls.push({
                type: "toolCall",
                id: chunk.content_block.id,
                name: chunk.content_block.name,
                arguments: {},
              } as ToolCall);
            } else if (chunk.type === "content_block_delta" && chunk.delta?.partial_json && toolCalls.length > 0) {
              const last = toolCalls[toolCalls.length - 1];
              const existing = JSON.stringify(last.arguments || {});
              const merged = existing === "{}" ? chunk.delta.partial_json : existing + chunk.delta.partial_json;
              try {
                last.arguments = JSON.parse(merged);
              } catch {
                // ignore partial parse until complete
              }
            } else if (chunk.type === "message_delta" && chunk.delta?.stop_reason) {
              const message: AssistantMessage = {
                role: "assistant",
                content: [
                  ...(text ? [{ type: "text", text }] : []),
                  ...toolCalls,
                ],
                api: "anthropic-messages",
                provider: "anthropic",
                model: model.id,
                usage: {
                  input: 0,
                  output: 0,
                  cacheRead: 0,
                  cacheWrite: 0,
                  totalTokens: 0,
                  cost: calculateCost(model as any, 0, 0, 0, 0),
                },
                stopReason: toStopReason(chunk.delta.stop_reason),
                timestamp: Date.now(),
              };
              stream.end(message);
              return;
            }
          }

          const message: AssistantMessage = {
            role: "assistant",
            content: [
              ...(text ? [{ type: "text", text }] : []),
              ...toolCalls,
            ],
            api: "anthropic-messages",
            provider: "anthropic",
            model: model.id,
            usage: {
              input: 0,
              output: 0,
              cacheRead: 0,
              cacheWrite: 0,
              totalTokens: 0,
              cost: calculateCost(model as any, 0, 0, 0, 0),
            },
            stopReason: "stop",
            timestamp: Date.now(),
          };
          stream.end(message);
        } catch (error) {
          const message: AssistantMessage = {
            role: "assistant",
            content: [],
            api: "anthropic-messages",
            provider: "anthropic",
            model: model.id,
            usage: {
              input: 0,
              output: 0,
              cacheRead: 0,
              cacheWrite: 0,
              totalTokens: 0,
              cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0, total: 0 },
            },
            stopReason: "error",
            timestamp: Date.now(),
            errorMessage: error instanceof Error ? error.message : String(error),
          };
          stream.push({ type: "error", reason: "error", error: message });
          stream.end();
        }
      })();

      return stream;
    },
  });
}
