import os
import subprocess
import sys
from flask import Flask, request, jsonify
import logging
from config import VideoConfig
from models import load_models
from content import process_json_prompts, generate_content, clear_gpu_memory
from video import create_narrative_video
import json
from groq import Groq

def install_dependencies():
    print("Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "torch", "torchvision"])
    subprocess.run([sys.executable, "-m", "pip", "install", "kokoro>=0.9.2"])
    subprocess.run([sys.executable, "-m", "pip", "install", "soundfile", "diffusers", "moviepy", "scipy", "numpy", "tqdm", "groq", "flask"])
    
    # Instalar espeak-ng no Linux (Colab)
    if os.name != 'nt':  # Se não for Windows
        subprocess.run(["apt-get", "-qq", "-y", "install", "espeak-ng"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Dependências instaladas com sucesso!")

def create_directories():
    print("Criando diretórios necessários...")
    os.makedirs("projetos", exist_ok=True)
    print("Diretórios criados com sucesso!")

def start_api():
    print("Iniciando a API...")
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    app = Flask(__name__)

    # Configurar o cliente Grok
    API_KEY = "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"
    client = Groq(api_key=API_KEY)

    # Mapeamento de idiomas e vozes disponíveis
    IDIOMAS = {
        'a': {'nome': 'inglês americano', 'vozes': ['af_heart', 'af_alloy', 'af_aoede', 'af_bella', 'af_jessica', 'af_korean', 'af_nicole', 'af_nova', 'af_river', 'af_sarah', 'af_sky', 'am_adam', 'am_echo', 'am_eric', 'am_fenrir', 'am_liam', 'am_michael', 'am_onyx', 'am_rhythm', 'am_santa']},
        'b': {'nome': 'inglês britânico', 'vozes': ['bf_alice', 'bf_emma', 'bf_isabella', 'bf_lily', 'bm_daniel', 'bm_fable', 'bm_george', 'bm_lewis']},
        'j': {'nome': 'japonês', 'vozes': ['jf_alpha', 'jf_gongitsune', 'jf_nezumi', 'jf_tebukuro', 'jm_kumo']},
        'z': {'nome': 'chinês mandarim', 'vozes': ['zf_xiaobei', 'zf_xiaoni', 'zf_xiaoxiao', 'zf_xiaoyi', 'zm_yunjian', 'zm_yunxi', 'zm_yunxia', 'zm_yunyang']},
        'e': {'nome': 'espanhol', 'vozes': ['ef_dora', 'em_alex', 'em_santa']},
        'f': {'nome': 'francês', 'vozes': ['ff_siwis']},
        'h': {'nome': 'hindi', 'vozes': ['hf_alpha', 'hf_beta', 'hm_omega', 'hm_psi']},
        'i': {'nome': 'italiano', 'vozes': ['if_sara', 'im_nicola']},
        'p': {'nome': 'português do Brasil', 'vozes': ['pf_dora', 'pm_alex', 'pm_santa']}
    }

    # Carregar modelos
    pipe, kokoro_pipeline = load_models('p')

    @app.route("/generate", methods=["POST"])
    def generate_video():
        try:
            data = request.json
            
            # Validação dos parâmetros obrigatórios
            required_params = ["historia", "num_cenas", "project_name", "video_type", "lang_code"]
            for param in required_params:
                if param not in data:
                    return jsonify({"error": f"Parâmetro obrigatório faltando: {param}"}), 400
            
            # Parâmetros com valores padrão
            estilo = data.get("estilo", "cinematic")
            voice = data.get("voice", IDIOMAS[data["lang_code"]]['vozes'][0])
            add_music = data.get("add_music", False)
            audio_path = data.get("audio_path") if add_music else None
            add_subtitles = data.get("add_subtitles", False)
            enable_video = data.get("enable_video", True)
            
            # Criar pasta para o projeto
            pasta_projeto = os.path.join("projetos", data["project_name"])
            os.makedirs(pasta_projeto, exist_ok=True)
            
            # Gerar storyboard
            json_file_path = os.path.join(pasta_projeto, f"{data['project_name']}_prompts.json")
            storyboard = gerar_storyboard_grok(
                data["historia"],
                data["num_cenas"],
                estilo,
                data["video_type"],
                data["lang_code"]
            )
            
            with open(json_file_path, "w", encoding="utf-8") as f:
                json.dump(storyboard, f, ensure_ascii=False, indent=2)
            
            # Configurar e gerar vídeo
            config = VideoConfig(
                data["video_type"],
                data["project_name"],
                json_file_path,
                audio_path,
                voice,
                output_dir=pasta_projeto,
                lang_code=data["lang_code"],
                add_subtitles=add_subtitles,
                enable_video_generation=enable_video
            )
            
            prompts = process_json_prompts(config.json_file_path)
            content_data = generate_content(pipe, kokoro_pipeline, prompts, config)
            output_path = create_narrative_video(config, content_data)
            
            return jsonify({
                "status": "success",
                "message": "Vídeo gerado com sucesso",
                "output_path": output_path
            })
            
        except Exception as e:
            logger.error(f"Erro durante a geração do vídeo: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "healthy"})

    # Iniciar a API
    print("\n=== API Iniciada ===")
    print("A API está rodando localmente. Para acessá-la no Colab, use o seguinte comando:")
    print("!curl -X POST http://localhost:5000/generate -H 'Content-Type: application/json' -d '{\"historia\":\"sua história\",\"num_cenas\":3,\"project_name\":\"teste\",\"video_type\":\"short\",\"lang_code\":\"p\"}'")
    print("\nPara acessar a API de outro notebook, use:")
    print("import requests")
    print("response = requests.post('http://localhost:5000/generate', json={\"historia\":\"sua história\",\"num_cenas\":3,\"project_name\":\"teste\",\"video_type\":\"short\",\"lang_code\":\"p\"})")
    print("print(response.json())")
    
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    print("=== Iniciando configuração do Video Narrative Generator ===")
    install_dependencies()
    create_directories()
    start_api() 