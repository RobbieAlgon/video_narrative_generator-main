# Video Narrative Generator

Este projeto permite gerar vídeos narrativos automaticamente usando IA. Ele combina imagens geradas pelo Stable Diffusion XL com narração em áudio gerada pelo Kokoro, aplicando efeitos como o Ken Burns para criar vídeos curtos ou longos.

## Como Executar no Google Colab

### 1. Configuração Inicial

1. Abra o Google Colab: https://colab.research.google.com
2. Crie um novo notebook
3. Execute os seguintes comandos para configurar o ambiente:

```python
# Instalar dependências
!pip install torch torchvision
!pip install kokoro>=0.9.2
!pip install soundfile diffusers moviepy scipy numpy tqdm groq flask flask-ngrok

# Instalar espeak-ng (necessário para Kokoro)
!apt-get -qq -y install espeak-ng > /dev/null 2>&1

# Criar estrutura de diretórios
!mkdir -p projetos
```

### 2. Configurar a API

Crie uma nova célula e cole o seguinte código:

```python
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
import os
import logging
from config import VideoConfig
from models import load_models
from content import process_json_prompts, generate_content, clear_gpu_memory
from video import create_narrative_video
import json
from groq import Groq

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

# Iniciar a API com ngrok
run_with_ngrok(app)
app.run()
```

### 3. Usando a API

Depois que a API estiver rodando, você receberá uma URL do ngrok. Use essa URL para fazer requisições à API.

#### Exemplo de requisição para gerar vídeo:

```python
import requests
import json

# Substitua pela URL fornecida pelo ngrok
API_URL = "https://seu-dominio.ngrok-free.app"

# Dados para gerar o vídeo
data = {
    "historia": "Uma aventura na floresta encantada",
    "num_cenas": 3,
    "project_name": "aventura_floresta",
    "video_type": "short",
    "lang_code": "p",
    "estilo": "cinematic",
    "voice": "pf_dora",
    "add_music": False,
    "add_subtitles": True,
    "enable_video": True
}

# Enviar requisição
response = requests.post(f"{API_URL}/generate", json=data)
print(response.json())
```

### 4. Parâmetros da API

- `historia` (obrigatório): O tema/narrativa do vídeo
- `num_cenas` (obrigatório): Número de cenas a serem geradas
- `project_name` (obrigatório): Nome do projeto
- `video_type` (obrigatório): Tipo de vídeo ("short" ou "longo")
- `lang_code` (obrigatório): Código do idioma (ex: "p" para português)
- `estilo` (opcional): Estilo visual (padrão: "cinematic")
- `voice` (opcional): Voz para narração
- `add_music` (opcional): Adicionar música de fundo
- `add_subtitles` (opcional): Adicionar legendas
- `enable_video` (opcional): Habilitar geração de vídeo

### 5. Idiomas disponíveis

- 'a': inglês americano
- 'b': inglês britânico
- 'j': japonês
- 'z': chinês mandarim
- 'e': espanhol
- 'f': francês
- 'h': hindi
- 'i': italiano
- 'p': português do Brasil

## Notas importantes

1. Mantenha o notebook do Colab aberto enquanto estiver usando a API
2. O primeiro carregamento pode demorar alguns minutos devido ao download dos modelos
3. Os vídeos gerados são salvos na pasta `projetos/[project_name]`
4. Se o Colab desconectar, você precisará reiniciar a API

## Solução de problemas

1. Se a API não responder:
   - Verifique se o notebook ainda está rodando
   - Tente reiniciar o runtime do Colab
   - Verifique se todas as dependências foram instaladas corretamente

2. Se houver erro na geração do vídeo:
   - Verifique se todos os parâmetros obrigatórios foram fornecidos
   - Verifique se o idioma e voz selecionados são compatíveis
   - Verifique se há espaço suficiente no disco do Colab
