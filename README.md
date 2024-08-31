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
## Argumentos para o programa
```bash
python deadline_driven.py [-h] --file FILE --time TIME [--tick TICK] [--algorithm {rm,edf}]
Simula um escalonador de tarefas

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Caminho para o arquivo de entrada
  --time TIME, -t TIME  Tempo de simulação
  --tick TICK           Tick do sistema
  --algorithm {rm,edf}, -a {rm,edf}
                        Algoritmo de escalonamento
```

## Exemplo de execução
```bash
python main.py -f in -t 100 -a edf --tick 1
```

# Estrutura de arquivos
A estrutura de arquivos do projeto é a seguinte:

```yaml
nome_tarefa1 custo1 periodo1
nome_tarefa2 custo2 periodo2
...
```


## Exemplo
```bash
T1 30 100
T2 35 175
T3 25 200
T4 30 300
```
