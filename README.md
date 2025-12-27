# 🦙 Ollama Studio

A Gradio web interface for creating custom Ollama models with your own system prompts and parameters, designed for easy installation via [Pinokio](https://pinokio.computer/).

## Features

- **One-Click Install** - Pinokio handles all dependencies automatically
- **Modern Gradio UI** - Clean, intuitive interface for model creation
- **Custom System Prompts** - Upload your own prompt files (.txt, .md)
- **Base Model Selection** - Choose from any locally installed Ollama model
- **Temperature Control** - Fine-tune model creativity and randomness
- **Real-time Feedback** - See model creation progress and detailed output
- **Cross-Platform** - Works on Windows, macOS, and Linux

## Prerequisites

**Ollama must be installed on your system before using this tool.**

- Download and install Ollama from: [https://ollama.ai](https://ollama.ai)
- Pull at least one base model: `ollama pull llama3.2`

## Installation

### Via Pinokio (Recommended)

1. Install [Pinokio](https://pinokio.computer/)
2. Search for "Ollama Model Creator" or add this repository URL
3. Click **Install** - Pinokio will:
   - Create a Python virtual environment
   - Install Gradio and dependencies
4. Click **Start** to launch the web UI

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ollama-model-creator.git
cd ollama-model-creator

# Create virtual environment
python -m venv env
source env/bin/activate  # Linux/Mac
# or: env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

## Start Ollama Studio

1. **Start** the app via Pinokio or `python app.py`
2. Open `http://127.0.0.1:7860` in your browser

## Usage - Debate Arena

1. Select 2 models for the dropdown menus (don't mix GGUF with normal models)
2. Choose a topic
3. Select the Debate Rounds
4. Click **Start Debate**
5. Optionally download the Debate as text file

[YouTube - Debate Arena](https://youtu.be/iOjumLr2gWY)
[![Debeta Arena Video](https://img.youtube.com/vi/iOjumLr2gWY/0.jpg)](https://youtu.be/iOjumLr2gWY)

## Usage - Ollama Maker

1. **Select a prompt file** containing your custom system instructions
2. **Choose a base model** from your locally installed Ollama models
3. **Enter a name** for your new custom model (e.g., `my-assistant`)
4. **Set temperature** (0.0-2.0, default 1.0)
5. Click **Create Model**
6. Wait for the model to be created
7. Run your new model: `ollama run my-assistant`

[YouTube - Ollama Maker:](https://www.youtube.com/watch?v=WDtpR9dGEtg)
[![Ollama Maker video](https://img.youtube.com/vi/WDtpR9dGEtg/0.jpg)](https://www.youtube.com/watch?v=WDtpR9dGEtg)

## Settings Guide

| Setting | Default | Description |
|---------|---------|-------------|
| Prompt File | - | Text file with your custom system prompt |
| Base Model | First available | Ollama model to use as foundation |
| New Model Name | my-custom-model | Name for your custom model |
| Temperature | 1.0 | Controls randomness (0.0=focused, 2.0=creative) |

## Temperature Guide

- **0.1 - 0.5**: More focused, deterministic, factual responses
- **0.6 - 1.0**: Balanced creativity and coherence (recommended)
- **1.1 - 2.0**: More creative, diverse, unpredictable outputs

## System Requirements

### Minimum

- **Ollama**: Installed and running
- **RAM**: 8GB
- **Storage**: Minimal (depends on Ollama models)

### Recommended

- **RAM**: 16GB+
- **Storage**: SSD for better performance

## Example Prompt File

Create a text file (e.g., `assistant.txt`) with your system prompt:

```txt
You are a helpful coding assistant specialized in Python.
You provide clear, concise code examples with explanations.
You follow best practices and modern Python conventions.
```

Then use this file to create your custom model!

## Troubleshooting

### "No local Ollama models found"

- Make sure Ollama is installed and running
- Pull at least one model: `ollama pull llama3.2`
- Verify with: `ollama list`

### "ollama command not found"

- Ensure Ollama is installed and in your system PATH
- Restart your terminal/command prompt after installation

## Credits

- **Authored by**: [ERP-Legend](https://github.com/reefer42)
- **Co-authored by**: [PierrunoYT](https://github.com/PierrunoYT) and [Morpheus](https://github.com/6Morpheus6)
- **Ollama**: [Ollama](https://ollama.ai)
- **Gradio**: [Gradio](https://gradio.app)
- **Pinokio**: [Pinokio](https://pinokio.computer/)

## License

MIT
