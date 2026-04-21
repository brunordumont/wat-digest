# Workflow: Daily News Digest — Marketing & Negócios

## Objective
Buscar diariamente as notícias mais relevantes sobre marketing digital, growth, vendas e negócios nas principais fontes brasileiras e enviar um digest formatado por e-mail.

## Configuração do Usuário
- **Nicho**: Marketing digital, negócios, marketing & vendas, growth
- **Contexto**: Assessoria de marketing
- **Frequência**: 1x por dia (recomendado: 8h da manhã)
- **Output**: E-mail com digest formatado em HTML
- **Fontes**: Exame, Forbes BR, InfoMoney, Valor Econômico

## Required Inputs (`.env`)
| Variável | Descrição |
|---|---|
| `NICHE_KEYWORDS` | Palavras-chave para filtrar relevância |
| `RSS_SOURCES` | URLs dos feeds RSS separadas por vírgula |
| `EMAIL_SENDER` | E-mail remetente (Gmail) |
| `EMAIL_PASSWORD` | App Password do Gmail (não a senha principal) |
| `EMAIL_RECIPIENT` | E-mail que vai receber o digest |

## Tools Used (em ordem)
1. `tools/fetch_news.py` — Puxa artigos dos feeds RSS e filtra por palavras-chave
2. `tools/filter_news.py` — Remove duplicatas e artigos sem conteúdo
3. `tools/send_email.py` — Envia o digest por e-mail em HTML

## Execução Manual
```bash
cd "/Users/bruno/Teste Claude Code"
bash tools/run_digest.sh
```

## Agendamento Automático (cron — todo dia às 8h)
```bash
# Abrir crontab:
crontab -e

# Adicionar linha:
0 8 * * * /bin/bash "/Users/bruno/Teste Claude Code/tools/run_digest.sh" >> /tmp/digest.log 2>&1
```

## Setup Inicial
```bash
pip install feedparser python-dotenv requests
```

## Configurar Gmail App Password
1. Acesse: myaccount.google.com/security
2. Ative verificação em 2 etapas (se não tiver)
3. Busque "Senhas de app" → crie uma para "Mail"
4. Cole essa senha em `EMAIL_PASSWORD` no `.env`

## Expected Output
E-mail HTML com:
- Header com data e contagem de matérias
- Cada artigo com: fonte, data, título (clicável), descrição e link
- Footer com as fontes utilizadas

## Edge Cases & Known Issues
- **0 artigos**: Pode ser que o dia tenha poucas notícias relevantes. Considere ampliar `NICHE_KEYWORDS` ou `--days 2`.
- **RSS indisponível**: O script ignora fontes com erro e continua com as demais. Verifique o log.
- **Gmail bloqueando envio**: Use App Password (não a senha normal). Certifique-se que o acesso SMTP está habilitado.
- **Exame/Valor com paywall**: Os RSS entregam título e descrição mesmo sem acesso ao conteúdo completo — suficiente para avaliar se vale a pena ler.

## Manutenção
- Adicionar novas fontes: incluir URL do RSS em `RSS_SOURCES` no `.env`
- Adicionar palavras-chave: incluir em `NICHE_KEYWORDS` no `.env`
- Checar log do cron: `cat /tmp/digest.log`
