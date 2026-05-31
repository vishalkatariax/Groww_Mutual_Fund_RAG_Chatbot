import { IConfigHandler, ContinueConfig } from "continue";

const config: ContinueConfig = {
  models: [
    {
      title: "Ollama - Qwen 2.5 Coder (Recommended)",
      provider: "ollama",
      model: "qwen2.5-coder:7b",
      apiBase: "http://localhost:11434",
    },
    {
      title: "Ollama - Llama 2",
      provider: "ollama",
      model: "llama2",
      apiBase: "http://localhost:11434",
    },
    {
      title: "Ollama - Mistral",
      provider: "ollama",
      model: "mistral",
      apiBase: "http://localhost:11434",
    },
  ],
  tabAutocompleteModel: {
    title: "Ollama - Qwen 2.5 Coder",
    provider: "ollama",
    model: "qwen2.5-coder:7b",
    apiBase: "http://localhost:11434",
  },
  embeddingsProvider: {
    provider: "ollama",
    model: "nomic-embed-text",
  },
  slashCommands: [
    {
      name: "share",
      description: "Export the current chat session",
    },
    {
      name: "project",
      description: "Learn about the current project structure",
    },
  ],
  contextProviders: [
    {
      name: "codebase",
      params: {},
    },
    {
      name: "docs",
      params: {},
    },
    {
      name: "open-files",
      params: {},
    },
  ],
};

export default config;
