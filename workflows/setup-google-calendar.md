# Setup: Google Calendar API

Como conectar o Google Calendar para que o Catch consulte slots livres de Bruno automaticamente.

---

## O que você vai precisar

- Conta Google do Bruno (a mesma da agenda)
- Acesso ao Google Cloud Console

---

## Passo 1 — Criar projeto no Google Cloud

1. Acesse [console.cloud.google.com](https://console.cloud.google.com)
2. No topo, clique em **"Select a project"** > **"New Project"**
3. Nome: `axis-agents` (ou qualquer nome)
4. Clique em **Create**

---

## Passo 2 — Ativar a API do Google Calendar

1. No menu lateral: **APIs & Services** > **Library**
2. Pesquise: `Google Calendar API`
3. Clique em **Enable**

---

## Passo 3 — Criar credenciais OAuth

1. No menu lateral: **APIs & Services** > **Credentials**
2. Clique em **+ Create Credentials** > **OAuth client ID**
3. Se pedir para configurar a tela de consentimento:
   - User Type: **External**
   - App name: `Axis Agents`
   - User support email: seu email
   - Developer contact: seu email
   - Salve e continue sem preencher o resto
4. De volta em Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: `axis-catch`
   - Clique em **Create**
5. Clique em **Download JSON**
6. Renomeie o arquivo baixado para `credentials.json`
7. Mova para a raiz deste projeto: `/Users/bruno/TESTE CLAUDE CODE/credentials.json`

---

## Passo 4 — Instalar dependências

```bash
cd /Users/bruno/TESTE\ CLAUDE\ CODE
pip install -r requirements.txt
```

---

## Passo 5 — Autenticar (primeira vez)

```bash
python tools/get_calendar_slots.py
```

- Vai abrir uma janela no browser pedindo para fazer login com a conta do Google
- Autorize o acesso à agenda
- Um arquivo `token.json` será criado automaticamente na raiz do projeto
- Nas próximas execuções, o token é reutilizado (renovação automática)

---

## Passo 6 — Testar

```bash
python tools/get_calendar_slots.py --morning 1 --afternoon 1
```

Saída esperada:
```json
{
  "date": "2026-05-22",
  "slots": [
    {
      "dia_semana": "Sexta",
      "data": "22/05",
      "hora": "09:00",
      "datetime_iso": "2026-05-22T09:00:00-03:00",
      "label": "Sexta (22/05) às 09:00"
    },
    {
      "dia_semana": "Sexta",
      "data": "22/05",
      "hora": "14:00",
      "datetime_iso": "2026-05-22T14:00:00-03:00",
      "label": "Sexta (22/05) às 14:00"
    }
  ]
}
```

---

## Segurança

- `credentials.json` e `token.json` estão no `.gitignore` e **nunca entram no repositório**
- O escopo é `calendar.readonly` — apenas leitura, sem modificar a agenda
- Se precisar revogar: [myaccount.google.com/permissions](https://myaccount.google.com/permissions)

---

## Troubleshooting

**Erro: `credentials.json não encontrado`**
Verifique se o arquivo está na raiz do projeto (não dentro de `tools/`).

**Erro: `Access blocked: app not verified`**
Na tela de consentimento do Google, clique em **Advanced** > **Go to axis-agents (unsafe)**.
Isso é normal para apps em desenvolvimento — apenas você usará.

**Token expirado**
Delete `token.json` e rode o script novamente para reautenticar.
