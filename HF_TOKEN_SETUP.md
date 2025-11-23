# Configuração do Token do Hugging Face

## Por que preciso de um token?

Alguns modelos do Hugging Face podem exigir autenticação, especialmente se você:
- Estiver usando modelos privados
- Estiver fazendo muitas requisições (rate limits)
- Estiver em um ambiente corporativo com restrições

## Como obter um token

1. Acesse: https://huggingface.co/settings/tokens
2. Faça login na sua conta do Hugging Face
3. Clique em "New token"
4. Escolha um nome para o token (ex: "voice-translator")
5. Selecione o tipo: "Read" é suficiente para baixar modelos públicos
6. Clique em "Generate token"
7. **Copie o token imediatamente** (você não poderá vê-lo novamente!

## Como configurar o token

### Opção 1: Arquivo .env (Recomendado)

1. Crie um arquivo `.env` na raiz do projeto:
```bash
# No Windows
echo HF_TOKEN=seu_token_aqui > .env

# No Linux/Mac
echo "HF_TOKEN=seu_token_aqui" > .env
```

2. Edite o arquivo `.env` e substitua `seu_token_aqui` pelo seu token real:
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

3. O token será carregado automaticamente quando você executar o aplicativo.

### Opção 2: Variável de Ambiente do Sistema

#### Windows (PowerShell):
```powershell
$env:HF_TOKEN="seu_token_aqui"
```

#### Windows (CMD):
```cmd
set HF_TOKEN=seu_token_aqui
```

#### Linux/Mac:
```bash
export HF_TOKEN="seu_token_aqui"
```

### Opção 3: Docker

Adicione a variável de ambiente no `docker-compose.yml`:

```yaml
environment:
  - HF_TOKEN=seu_token_aqui
```

Ou passe como argumento ao executar:

```bash
docker run --rm -e HF_TOKEN=seu_token_aqui -p 5000:5000 voice-translator
```

## Verificação

O token será usado automaticamente quando você executar o aplicativo. Se o modelo ainda não carregar, verifique:

1. O token está correto (começa com `hf_`)
2. O arquivo `.env` está na raiz do projeto
3. Você instalou `python-dotenv` (`pip install python-dotenv`)

## Nota de Segurança

⚠️ **NUNCA** commite o arquivo `.env` no Git! Ele já está no `.gitignore` para sua proteção.

