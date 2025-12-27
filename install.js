module.exports = {
  run: [
    // Install Ollama Model Creator dependencies from requirements.txt
    {
      method: "shell.run",
      params: {
        venv: "env",
        message: [
          "uv pip install -r requirements.txt"
        ],
      }
    },
    {
      method: "notify",
      params: {
        html: "Installation complete! Make sure Ollama is installed on your system, then click 'Start' to launch Ollama Model Creator."
      }
    }
  ]
}
