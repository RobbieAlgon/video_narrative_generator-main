# Video Narrative Generator - Google Colab Setup

Este projeto permite gerar vídeos narrativos automaticamente usando IA. Este guia explica como configurar e rodar o projeto no Google Colab.

## Pré-requisitos

- Conta no Google Colab
- Acesso à internet
- Conta no ngrok (para expor a API)

## Configuração no Google Colab

1. Abra o Google Colab: https://colab.research.google.com

2. Faça upload dos seguintes arquivos para o Colab:
   - `api.py`
   - `config.py`
   - `content.py`
   - `models.py`
   - `video.py`
   - `requirements.txt`
   - `colab_setup.ipynb`

3. Execute o notebook `colab_setup.ipynb`:
   - Clique em "Runtime" > "Run all"
   - Aguarde a instalação das dependências

4. Quando o ngrok iniciar, você receberá uma URL pública para acessar a API

## Usando a API

A API expõe dois endpoints:

1. `GET /health` - Verifica se a API está funcionando
2. `POST /generate` - Gera um novo vídeo narrativo

### Exemplo de requisição para gerar vídeo

```json
{
    "historia": "Uma aventura na floresta",
    "num_cenas": 3,
    "project_name": "aventura_floresta",
    "video_type": "short",
    "lang_code": "p",
    "estilo": "cinematic",
    "voice": "pf_dora",
    "add_music": false,
    "add_subtitles": true,
    "enable_video": true
}
```

### Parâmetros da requisição

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

### Idiomas disponíveis

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

1. O primeiro carregamento pode demorar alguns minutos devido ao download dos modelos
2. Os vídeos gerados são salvos na pasta `projetos/[project_name]`
3. Mantenha o notebook do Colab aberto enquanto estiver usando a API
4. Se precisar reiniciar a API, execute novamente a última célula do notebook

## Solução de problemas

1. Se a API não responder:
   - Verifique se o notebook ainda está rodando
   - Tente reiniciar o runtime do Colab
   - Verifique se todas as dependências foram instaladas corretamente

2. Se houver erro na geração do vídeo:
   - Verifique se todos os parâmetros obrigatórios foram fornecidos
   - Verifique se o idioma e voz selecionados são compatíveis
   - Verifique se há espaço suficiente no disco do Colab
