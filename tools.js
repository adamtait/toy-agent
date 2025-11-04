import fs from 'fs/promises';

const tools = [
  {
    name: 'list_files',
    description: 'Lists all files and directories under the given directory.',
    input_schema: {
      type: 'object',
      properties: {
        path: {
          type: 'string',
          description: 'The directory path to list files from. Defaults to the root of the repo.',
        },
      },
    },
  },
  {
    name: 'read_file',
    description: 'Reads the content of the specified file in the repo.',
    input_schema: {
      type: 'object',
      properties: {
        filepath: {
          type: 'string',
          description: 'The path of the file to read, relative to the repo root.',
        },
      },
      required: ['filepath'],
    },
  },
  {
    name: 'replace_with_git_merge_diff',
    description: 'Performs a targeted search-and-replace to modify an existing file. The format is a Git merge diff.',
    input_schema: {
      type: 'object',
      properties: {
        filepath: {
          type: 'string',
          description: 'The path of the file to modify.',
        },
        merge_diff: {
          type: 'string',
          description: 'The diff to apply to the file.',
        },
      },
      required: ['filepath', 'merge_diff'],
    },
  },
  {
    name: 'finish',
    description: 'Signals that the agent has completed the task.',
    input_schema: {
      type: 'object',
      properties: {
        message: {
          type: 'string',
          description: 'A message to the user indicating that the task is complete.',
        },
      },
    },
  },
];

function getTool(name) {
  return tools.find(tool => tool.name === name);
}

async function executeTool(tool, input) {
  try {
    switch (tool.name) {
      case 'list_files':
        return JSON.stringify(await fs.readdir(input.path || '.'));
      case 'read_file':
        return await fs.readFile(input.filepath, 'utf-8');
      case 'replace_with_git_merge_diff':
        const originalContent = await fs.readFile(input.filepath, 'utf-8');
        const lines = input.merge_diff.split('\n');
        const searchLines = [];
        const replaceLines = [];
        let inSearchBlock = false;
        let inReplaceBlock = false;

        for (const line of lines) {
          if (line.startsWith('<<<<<<< SEARCH')) {
            inSearchBlock = true;
            continue;
          }
          if (line.startsWith('=======')) {
            inSearchBlock = false;
            inReplaceBlock = true;
            continue;
          }
          if (line.startsWith('>>>>>>> REPLACE')) {
            inReplaceBlock = false;
            continue;
          }
          if (inSearchBlock) {
            searchLines.push(line);
          }
          if (inReplaceBlock) {
            replaceLines.push(line);
          }
        }

        const searchContent = searchLines.join('\n');
        const replaceContent = replaceLines.join('\n');

        const newContent = originalContent.split(searchContent).join(replaceContent);
        await fs.writeFile(input.filepath, newContent);
        return `Successfully modified ${input.filepath}`;
      case 'finish':
        return { finish: true, message: input.message };
      default:
        throw new Error(`Unknown tool: ${tool.name}`);
    }
  } catch (error) {
    return `Error executing tool ${tool.name}: ${error.message}`;
  }
}

export { tools, getTool, executeTool };
