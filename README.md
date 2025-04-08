# Video Narrative Generator

Este projeto permite gerar vídeos narrativos automaticamente usando IA. Ele combina imagens geradas pelo Stable Diffusion XL com narração em áudio gerada pelo Kokoro, aplicando efeitos como o Ken Burns para criar vídeos curtos ou longos.

## Como Executar no Google Colab

1. Abra o Google Colab: https://colab.research.google.com
2. Crie um novo notebook
3. Cole e execute o seguinte código:

```python
# Clonar o repositório
!git clone https://github.com/RobbieAlgon/video_narrative_generator-main.git
%cd video_narrative_generator-main

# Executar o script de setup
!python setup_colab.py
```

4. Aguarde a instalação das dependências e o início da API
5. Quando a API iniciar, você receberá uma URL do ngrok
6. Use a URL para fazer requisições à API

### Exemplo de requisição para gerar vídeo:

```python
import requests

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

## Parâmetros da API

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

## Idiomas disponíveis

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
