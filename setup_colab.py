import os
import subprocess
import sys
import shutil

def setup_environment():
    """Configura o ambiente do Colab"""
    print("=== Iniciando configuração do ambiente ===")
    
    # Define o diretório base
    base_dir = "/content"
    project_dir = os.path.join(base_dir, "video_narrative_generator-main")
    
    # Garante que o diretório base existe
    os.makedirs(base_dir, exist_ok=True)
    os.chdir(base_dir)
    print(f"Diretório base: {os.getcwd()}")
    
    # Remove o projeto se existir
    if os.path.exists(project_dir):
        print(f"Removendo projeto existente...")
        shutil.rmtree(project_dir)
    
    # Clona o repositório
    print("Clonando repositório...")
    subprocess.run(["git", "clone", "https://github.com/RobbieAlgon/video_narrative_generator-main.git"], check=True)
    
    # Entra no diretório do projeto
    os.chdir(project_dir)
    print(f"Diretório do projeto: {os.getcwd()}")
    
    # Adiciona o diretório ao PYTHONPATH
    sys.path.insert(0, os.getcwd())
    
    # Instala as dependências
    print("\nInstalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "flask-ngrok", "ngrok"], check=True)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    print("\n=== Ambiente configurado com sucesso! ===")
    return True

def main():
    """Função principal"""
    try:
        # Configura o ambiente
        if not setup_environment():
            print("Erro ao configurar o ambiente")
            return
        
        # Importa as dependências
        from flask import Flask, request, jsonify
        from flask_cors import CORS
        import threading
        import time
        import json
        from pathlib import Path
        import logging
        
        # Importa os módulos do projeto
        try:
            from config import VideoConfig
            from models import load_models
            from content import process_json_prompts, generate_content, clear_gpu_memory
            from video import create_narrative_video
            from groq import Groq
        except ImportError as e:
            print(f"Erro ao importar módulos: {e}")
            print("Verificando diretório atual e conteúdo...")
            print(f"Diretório atual: {os.getcwd()}")
            print("Conteúdo do diretório:")
            for item in os.listdir():
                print(f"- {item}")
            return
        
        # Configuração do Flask
        app = Flask(__name__)
        CORS(app)
        
        # Variável global para armazenar a URL do ngrok
        ngrok_url = None
        
        def setup_ngrok():
            """Configura o ngrok para acesso público"""
            global ngrok_url
            try:
                from flask_ngrok import run_with_ngrok
                from ngrok import ngrok
                
                # Inicia o ngrok
                http_tunnel = ngrok.connect(5000)
                ngrok_url = http_tunnel.public_url
                
                print("\n=== Ngrok Configurado com Sucesso ===")
                print(f"URL pública da API: {ngrok_url}")
                print("Use esta URL para acessar a API de qualquer lugar")
                print("=====================================\n")
                
                return run_with_ngrok
            except Exception as e:
                print(f"Erro ao configurar ngrok: {e}")
                return None
        
        def create_directories():
            print("Criando diretórios necessários...")
            os.makedirs("projetos", exist_ok=True)
            print("Diretórios criados com sucesso!")
        
        def start_api():
            """Inicia a API Flask"""
            print("\nIniciando API...")
            
            # Configurar logging
            logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
            logger = logging.getLogger(__name__)
            
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
            
            @app.route('/generate', methods=['POST'])
            def generate_video():
                """Endpoint para gerar vídeos"""
                try:
                    data = request.json
                    print(f"Recebida requisição: {json.dumps(data, indent=2)}")
                    
                    # Validação dos dados
                    required_fields = ['historia', 'num_cenas', 'project_name', 'video_type', 'lang_code']
                    for field in required_fields:
                        if field not in data:
                            return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400
                    
                    # Processamento da requisição
                    response = {
                        'status': 'success',
                        'message': 'Vídeo em processamento',
                        'data': data
                    }
                    
                    return jsonify(response)
                
                except Exception as e:
                    logger.error(f"Erro durante a geração do vídeo: {e}", exc_info=True)
                    return jsonify({'error': str(e)}), 500
            
            @app.route("/health", methods=["GET"])
            def health_check():
                return jsonify({"status": "healthy"})
            
            # Configura o ngrok
            run_with_ngrok = setup_ngrok()
            if run_with_ngrok:
                run_with_ngrok(app)
            
            # Inicia o servidor Flask
            app.run(host='0.0.0.0', port=5000)
        
        # Cria os diretórios necessários
        create_directories()
        
        # Inicia a API em uma thread separada
        api_thread = threading.Thread(target=start_api)
        api_thread.daemon = True
        api_thread.start()
        
        # Mantém o script rodando
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            sys.exit(0)
    
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        return

if __name__ == '__main__':
    main() 