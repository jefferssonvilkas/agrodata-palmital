# AgroData Palmital — MVP Web

Dashboard de dados agrícolas com IA Claude integrada.
Deploy gratuito no Streamlit Cloud — sem servidor, sem cartão.

## Como publicar (5 minutos)

### 1. Subir no GitHub
```
Crie um repositório público no github.com
Faça upload dos 3 arquivos: app.py, requirements.txt, README.md
```

### 2. Deploy no Streamlit Cloud
```
Acesse: share.streamlit.io
Clique em "New app"
Conecte seu GitHub e selecione este repositório
Main file: app.py
Clique em Deploy
```

### 3. Usar o MVP
```
Acesse a URL gerada (ex: seunome-agrodata.streamlit.app)
Cole sua chave Claude na barra lateral
Selecione a fazenda e comece a perguntar
```

## Funcionalidades do MVP
- Preços em tempo real (soja, milho, cana)
- Clima Palmital/SP
- Chat IA com Claude — perguntas livres sobre os dados
- Atalhos de perguntas frequentes
- 3 fazendas de exemplo pré-cadastradas

## Próxima versão (com banco de dados)
- Conectar PostgreSQL real (Supabase gratuito)
- Preços reais do CEPEA via scraping
- Clima real do INMET
- Cadastro de novos produtores
- Histórico de conversas
- Integração WhatsApp
