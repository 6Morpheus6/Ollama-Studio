module.exports = {
  daemon: true,
  run: [
    // Launch Ollama Model Creator Gradio Web UI
    {
      method: "shell.run",
      params: {
        venv: "env",
        env: { },
        message: [
          "python app.py"
        ],
        on: [{
          // Monitor for Gradio's HTTP URL output
          "event": "/http:\\/\\/[^\\s\\/]+:\\d{2,5}(?=[^\\w]|$)/",
          "done": true
        }]
      }
    },
    // Set the local URL variable for the "Open Web UI" button
    {
      method: "local.set",
      params: {
        url: "{{input.event[0]}}"
      }
    }
  ]
}

