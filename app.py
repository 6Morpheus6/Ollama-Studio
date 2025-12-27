#!/usr/bin/env python3
import os
import ollama
import warnings
import requests
import tempfile
import subprocess
import gradio as gr
from dataclasses import dataclass
from typing import Generator, Callable, Optional, Tuple

warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- KONFIGURATION ---
OLLAMA_HOST = "http://127.0.0.1:11434"

CSS = """
.header { text-align: center; margin-bottom: 20px; }
.header h1 { margin-bottom: 0; }
"""

# =============================================================================
# TEIL 1: LOGIK FÜR DEN MODEL CREATOR
# =============================================================================

def get_local_models_subprocess():
    """Get list of local Ollama models via subprocess (for Creator)."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True
        )
        lines = result.stdout.strip().split('\n')[1:]
        models = [line.split()[0] for line in lines if line.strip()]
        return models if models else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None

def validate_temperature(temp_str):
    try:
        temp = float(temp_str)
        if temp < 0:
            return False, "Temperature must be non-negative."
        return True, temp
    except ValueError:
        return False, "Invalid temperature. Please enter a numeric value."

def get_model_updates():
    """Hilfsfunktion: Holt frische Modelle und erstellt Updates für alle Dropdowns."""
    models = get_local_models_subprocess() or []
    return (
        gr.update(choices=models), 
        gr.update(choices=models), 
        gr.update(choices=models)
    )

def create_model_logic(prompt_file, base_model, new_model_name, temperature):
    """Logik zum Erstellen des Modells mit Auto-Refresh."""
    no_update = (gr.update(), gr.update(), gr.update())

    if not prompt_file: return "❌ Error: Select a prompt file.", "", *no_update
    if not base_model: return "❌ Error: Select a base model.", "", *no_update
    if not new_model_name.strip(): return "❌ Error: Provide a model name.", "", *no_update
    
    is_valid, result = validate_temperature(temperature)
    if not is_valid: return f"❌ Error: {result}", "", *no_update
    temp_value = result
    
    try:
        file_path = prompt_file.name if hasattr(prompt_file, 'name') else prompt_file
        with open(file_path, 'r', encoding='utf-8') as f:
            custom_prompt = f.read()
    except Exception as e:
        return f"❌ Error reading prompt file: {str(e)}", "", *no_update
    
    if not custom_prompt.strip(): return "❌ Error: Prompt file is empty.", "", *no_update
    
    modelfile_content = f'FROM {base_model}\nPARAMETER temperature {temp_value}\nSYSTEM """\n{custom_prompt}\n"""\n'
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='_Modelfile', delete=False, encoding='utf-8') as f:
            modelfile_path = f.name
            f.write(modelfile_content)
        
        process = subprocess.Popen(
            ["ollama", "create", new_model_name, "-f", modelfile_path],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        
        output_lines = [line.rstrip() for line in process.stdout]
        process.wait()
        output_text = '\n'.join(output_lines)
        
        try: os.unlink(modelfile_path)
        except: pass
        
        if process.returncode == 0:
            upd1, upd2, upd3 = get_model_updates()
            msg = f"✅ Custom model '{new_model_name}' created!\nRun: ollama run {new_model_name}"
            return msg, output_text, upd1, upd2, upd3
        else:
            return f"❌ Failed. Return code: {process.returncode}", output_text, *no_update
            
    except Exception as e:
        return f"❌ Error creating model: {str(e)}", "", *no_update

def refresh_creator_models():
    models = get_local_models_subprocess()
    return gr.Dropdown(choices=models if models else [], value=models[0] if models else None)


# =============================================================================
# TEIL 2: LOGIK FÜR DIE DEBATTE
# =============================================================================

@dataclass
class DebateConfig:
    model_1: str
    model_2: str
    topic: str
    rounds: int

class OllamaService:
    def __init__(self, host: str = OLLAMA_HOST):
        self.host = host
        self.client = ollama.Client(host=host)

    def get_models(self) -> list[str]:
        try:
            resp = requests.get(f"{self.host}/api/tags", timeout=5)
            if resp.ok:
                return [m["name"] for m in resp.json().get("models", [])]
        except requests.RequestException:
            pass
        return []

    def chat(self, model: str, message: str) -> str:
        response = self.client.chat(
            model=model, messages=[{"role": "user", "content": message}]
        )
        return response["message"]["content"]

class DebateEngine:
    def __init__(self, service: OllamaService):
        self.service = service

    def run(self, config: DebateConfig, on_progress: Optional[Callable[[float, str], None]] = None) -> Generator[str, None, None]:
        output = self._header(config)
        yield output
        prompt = f"Let's discuss: {config.topic}. Share your perspective."

        for round_num in range(1, config.rounds + 1):
            if on_progress:
                on_progress(round_num / config.rounds, f"Round {round_num}/{config.rounds}")

            output += f"### 🔵 {config.model_1} — Round {round_num}\n\n"
            yield output
            try:
                reply_1 = self.service.chat(config.model_1, prompt)
                output += f"{reply_1}\n\n"
                yield output
            except Exception as e:
                yield output + f"⚠️ Error: {e}"; return

            output += f"### 🟢 {config.model_2} — Round {round_num}\n\n"
            yield output
            try:
                reply_2 = self.service.chat(config.model_2, reply_1)
                output += f"{reply_2}\n\n"
                yield output
                prompt = reply_2
            except Exception as e:
                yield output + f"⚠️ Error: {e}"; return

            output += "---\n\n"
            yield output

        output += "## ✅ Debate Complete\n"
        yield output

    def _header(self, config: DebateConfig) -> str:
        return f"## 🎭 {config.topic}\n\n| Model 1 | Model 2 | Rounds |\n|---|---|---|\n| {config.model_1} | {config.model_2} | {config.rounds} |\n\n---\n"

# Services
debate_service = OllamaService()
debate_engine = DebateEngine(debate_service)

def get_debate_models():
    models = debate_service.get_models()
    return models if models else ["No models found"]

def refresh_debate_models():
    choices = get_debate_models()
    def_1 = choices[0] if choices else None
    def_2 = choices[1] if len(choices) > 1 else def_1
    return gr.update(choices=choices, value=def_1), gr.update(choices=choices, value=def_2)

def start_debate(m1, m2, topic, rounds, progress=gr.Progress()):
    # 1. Validierung
    if not m1 or not m2 or not topic.strip():
        # Kein Download-Button Update
        yield "⚠️ Please check inputs.", gr.update(visible=False)
        return

    config = DebateConfig(m1, m2, topic.strip(), int(rounds))
    
    # Variable um den gesamten Text zu speichern
    full_transcript = ""

    # 2. Debatte läuft (Button bleibt unsichtbar)
    for update in debate_engine.run(config, on_progress=lambda pct, msg: progress(pct, desc=msg)):
        full_transcript = update
        yield update, gr.update(visible=False)

    # 3. Debatte fertig -> Datei speichern
    try:
        # Temporäre Datei erstellen (oder überschreiben)
        filename = "debate_transcript.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_transcript)
        
        # 4. Finales Yield: Text UND Button sichtbar machen
        yield full_transcript, gr.update(value=filename, visible=True)
    except Exception as e:
        yield full_transcript + f"\n\n❌ Error saving file: {e}", gr.update(visible=False)


# =============================================================================
# TEIL 3: MAIN APP UI
# =============================================================================

initial_debate_models = get_debate_models()
initial_creator_models = get_local_models_subprocess()

with gr.Blocks(title="Ollama Studio", css=CSS, theme=gr.themes.Soft()) as app:
    
    gr.HTML("""
        <div class="header">
            <h1>🦙 Ollama Studio</h1>
            <p>Debate Arena & Model Creator</p>
        </div>
    """)

    with gr.Tabs():
        
        # --- TAB 1: DEBATE ARENA ---
        with gr.TabItem("🎭 Debate Arena"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("#### ⚙️ Debate Config")
                    deb_model_1 = gr.Dropdown(choices=initial_debate_models, value=initial_debate_models[0] if initial_debate_models else None, label="🔵 Model 1")
                    deb_model_2 = gr.Dropdown(choices=initial_debate_models, value=initial_debate_models[1] if len(initial_debate_models) > 1 else initial_debate_models[0], label="🟢 Model 2")
                    deb_refresh_btn = gr.Button("🔄 Refresh Models", size="sm")
                    deb_topic = gr.Textbox(label="Topic", placeholder="Should AI be regulated?", lines=2)
                    deb_rounds = gr.Slider(1, 10, value=3, step=1, label="Rounds")
                    deb_start_btn = gr.Button("🚀 Start Debate", variant="primary")           
                    deb_download_btn = gr.DownloadButton(
                        label="💾 Download Transcript (.txt)", 
                        visible=False
                    )

                with gr.Column(scale=2):
                    gr.Markdown("#### 📜 Transcript")
                    deb_output = gr.Markdown("*Ready to debate...*")
                    
            deb_refresh_btn.click(refresh_debate_models, outputs=[deb_model_1, deb_model_2])
            
            # Update: outputs enthält jetzt auch den Button
            deb_start_btn.click(
                start_debate, 
                inputs=[deb_model_1, deb_model_2, deb_topic, deb_rounds], 
                outputs=[deb_output, deb_download_btn]
            )

        # --- TAB 2: MODEL CREATOR ---
        with gr.TabItem("🛠️ Model Creator"):
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 📝 Define Model")
                    crt_file = gr.File(label="System Prompt File (.txt/.md)", file_types=[".txt", ".md"])
                    crt_base_model = gr.Dropdown(choices=initial_creator_models or [], label="Base Model", value=initial_creator_models[0] if initial_creator_models else None)
                    crt_refresh_btn = gr.Button("🔄 Refresh Models", size="sm")
                    
                    crt_name = gr.Textbox(label="New Model Name", placeholder="my-custom-model")
                    crt_temp = gr.Textbox(label="Temperature", value="1.8")
                    crt_create_btn = gr.Button("🏗️ Create Model", variant="primary")
                
                with gr.Column():
                    gr.Markdown("#### 📊 Output")
                    crt_status = gr.Textbox(label="Status", lines=4)
                    crt_details = gr.Textbox(label="Log", lines=8)

            crt_refresh_btn.click(refresh_creator_models, outputs=[crt_base_model])
            
            crt_create_btn.click(
                create_model_logic, 
                inputs=[crt_file, crt_base_model, crt_name, crt_temp], 
                outputs=[crt_status, crt_details, deb_model_1, deb_model_2, crt_base_model]
            )

if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)