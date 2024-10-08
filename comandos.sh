#/bin/bash
# Earliest deadline first, exemplo padrão
python main.py -f in2 -t 30 -a edf

# Rate monotonic, exemplo padrão
python main.py -f in2 -t 30 -a rm

# Rate monotonic, exemplo in2 com tarefas com cost, deadline * 5
python main.py -f in5 -t 150 -a rm

# Outro exemplo, com EDF e RM 
python main.py -f in -t 900 -a edf 
python main.py -f in -t 900 -a rm

# Mesmo exemplo, com --out out.png, edf
python main.py -f in -t 900 -a edf --out out.png

# Exemplo com Deadlines perdidas
python main.py -f in4 -t 30 -a edf
python main.py -f in4 -t 30 -a rm
