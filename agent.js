import Anthropic from '@anthropic-ai/sdk';
import { tools, getTool, executeTool } from './tools.js';
import { log } from './logging.js';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

async function main() {
  console.log('Starting agent...');
  await log({ type: 'event', message: 'Agent starting' });

  let conversation = [
    { role: 'user', content: 'Hello! Please list the files in the current directory.' },
  ];
  let finished = false;

  while (!finished) {
    await log({ type: 'state', conversation });

    const response = await client.messages.create({
      model: 'claude-3-opus-20240229',
      max_tokens: 1024,
      messages: [
        { role: 'user', content: 'You are a software development agent. You have access to a set of tools to interact with the codebase. You can list files, read files, and modify files. Your goal is to complete the user\'s request. You should reason about the request, decide which tool to use, and then use it. After each tool use, you will get the result and can decide on the next step. When you believe you have completed the request, you can use the `finish` tool.' },
        ...conversation,
      ],
      tools: tools,
    });

    console.log('LLM response:', response);
    await log({ type: 'llm_response', response });

    conversation.push({ role: 'assistant', content: response.content });

    const toolChoice = response.content.find(block => block.type === 'tool_use');

    if (toolChoice) {
      const toolName = toolChoice.name;
      const toolInput = toolChoice.input;
      const tool = getTool(toolName);

      if (tool) {
        const result = await executeTool(tool, toolInput);
        console.log('Tool result:', result);
        await log({ type: 'tool_result', toolName, toolInput, result });

        if (result.finish) {
          finished = true;
          console.log('Agent finished:', result.message);
          await log({ type: 'event', message: `Agent finished: ${result.message}` });
        } else {
          conversation.push({
            role: 'user',
            content: [
              {
                type: 'tool_result',
                tool_use_id: toolChoice.id,
                content: result,
              },
            ],
          });
        }
      } else {
        console.error('Unknown tool:', toolName);
        await log({ type: 'error', message: `Unknown tool: ${toolName}` });
        conversation.push({
          role: 'user',
          content: [
            {
              type: 'tool_result',
              tool_use_id: toolChoice.id,
              content: `Error: Unknown tool ${toolName}`,
              is_error: true,
            },
          ],
        });
      }
    } else {
      console.log('No tool choice, continuing.');
      await log({ type: 'event', message: 'No tool choice, continuing.' });
    }
  }
}

main();
