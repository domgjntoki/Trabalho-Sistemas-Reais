# Trabalho-Sistemas-Reais
Trabalho de sistemas reais, simulando o algorítimo Rate monotonic e Deadline Driven

# Instalação
Para instalar o projeto, siga os passos abaixo:

## CMD
```cmd
python -m venv .env
.env\Scripts\activate
pip install -r requirements.txt
```

## Powershell
```powershell
python -m venv .env
.\.env\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Bash, git bash
```bash
python -m venv .env
source .env/Scripts/activate
pip install -r requirements.txt
```

# Execução
Para executar o projeto, siga os passos abaixo:

```bash
python rate_monotonic.py < in
```

ou 

```bash
python deadline_driven.py < in
```

Ou qualquer outro arquivo de entrada que desejar.

# Estrutura de arquivos
A estrutura de arquivos do projeto é a seguinte:

```yaml
quantidade_de_tarefas tempo_de_simulacao tick_do_sistema
nome_tarefa1 custo1 periodo1
nome_tarefa2 custo2 periodo2
...
```


# Exemplo
```bash
4 500 1
T1 30 100
T2 35 175
T3 25 200
T4 30 300
```
