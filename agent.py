import os
import sys
import anthropic
from tools import tools, execute_tool
from logging_utils import log, setup_logging

def main(task):
    print('Starting agent...')
    setup_logging()
    log({'type': 'event', 'message': 'Agent starting'})

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    conversation = [
        {"role": "user", "content": task}
    ]
    finished = False

    while not finished:
        log({'type': 'state', 'conversation': conversation})

        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "You are a software development agent. You have access to a set of tools to interact with the codebase. You can list files, read files, and modify files. Your goal is to complete the user's request. You should reason about the request, decide which tool to use, and then use it. After each tool use, you will get the result and can decide on the next step. When you believe you have completed the request, you can use the `finish` tool."},
                *conversation
            ],
            tools=tools
        )

        print('LLM response:', response)
        log({'type': 'llm_response', 'response': response.model_dump()})

        conversation.append({"role": "assistant", "content": response.content})

        tool_choice = next((block for block in response.content if block.type == 'tool_use'), None)

        if tool_choice:
            tool_name = tool_choice.name
            tool_input = tool_choice.input

            result = execute_tool(tool_name, tool_input)
            print('Tool result:', result)
            log({'type': 'tool_result', 'tool_name': tool_name, 'tool_input': tool_input, 'result': result})

            if isinstance(result, dict) and result.get("finish"):
                finished = True
                print('Agent finished:', result.get("message"))
                log({'type': 'event', 'message': f'Agent finished: {result.get("message")}'})
            else:
                conversation.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_choice.id,
                            "content": result,
                        }
                    ]
                })
        else:
            print('No tool choice, continuing.')
            log({'type': 'event', 'message': 'No tool choice, continuing.'})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py <task>")
        sys.exit(1)
    task = sys.argv[1]
    main(task)
