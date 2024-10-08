# Trabalho-Sistemas-Reais
Trabalho de sistemas reais, simulando o algorítimo Rate monotonic e Deadline Driven

# Instalação
Para instalar o projeto, siga os passos abaixo:

```bash
python -m venv .env
source .env/Scripts/activate
pip install -r requirements.txt
```

# Execução
## Argumentos para o programa
Digite `python main.py -h` para instruções:
```bash
usage: main.py [-h] --file FILE [--time TIME] [--tick TICK] [--algorithm {rm,edf}] [--output OUTPUT]

Simula um escalonador de tarefas

options:
  -h, --help            show this help message and exit
  --file FILE, -f FILE  Caminho para o arquivo de entrada
  --time TIME, -t TIME  Tempo de simulação
  --tick TICK           Tick do sistema
  --algorithm {rm,edf}, -a {rm,edf}
                        Algoritmo de escalonamento
  --output OUTPUT, -o OUTPUT
                        Caminho para o arquivo de saída em formato PNG

```
Por padrão,
- time: Período da maior task + 1
- tick: Maior divisor comum entre os períodos e custos
- algorithm: rm (Rate monotonic)
- output: Vazio, logo gera um gráfico interativo.


## Exemplo de execução
```bash
python main.py -f in -t 100 -a edf --tick 1 -o out.png
```

# Estrutura de arquivos
A estrutura de arquivos do projeto é a seguinte:

```yaml
nome_tarefa1 custo1 periodo1
nome_tarefa2 custo2 periodo2
...
```


### Exemplo
```bash
T1 30 100
T2 35 175
T3 25 200
T4 30 300
```

# Imagens do programa em funcionamento
# Modo interativo
No modo interativo, que é o padrão a menos que você especifique uma saída em imagem com a opção `--output`, é possível aplicar zoom no gráfico, selecionar tarefas específicas para exibição e utilizar a barra de rolagem inferior para navegar pela timeline completa, especialmente útil em simulações de longa duração.
![Modo interativo](read_me_images/exemplo2.png)
## Modo saída de imagem
![Saída em imagem](read_me_images/exemplo1.png)
