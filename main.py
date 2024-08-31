import pandas as pd
import plotly.figure_factory as ff
from dataclasses import dataclass
import queue
import argparse


@dataclass
class Task:
    """
    Representa uma tarefa com informações sobre seu nome, período, custo, 
    tempo de início, tempo restante, deadline e função de prioridade.
    """
    name: str
    period: int
    cost: int
    started_at: int = 0
    remaining_time: int = 0
    deadline: int = 0
    priority_function = lambda x: x.period

    @property
    def priority(self) -> float:
        """
        Calcula a prioridade da tarefa com base na função de prioridade definida.
        """
        return self.priority_function(self)

    def start_task(self, time: int) -> None:
        """
        Marca o tempo que a tarefa começou a rodar e calcula o deadline.

        Args:
            time (int): Tempo atual do sistema.
        """
        self.deadline = time + self.period

    def run_task(self, time: int) -> None:
        """
        Inicia a tarefa e marca o tempo que ela começou a rodar.

        Args:
            time (int): Tempo atual do sistema.
        """
        self.started_at = time
        if self.remaining_time == 0:
            self.remaining_time = self.cost

    def interrupt_task(self, time: int, system_tick: int) -> None:
        """
        Interrompe a tarefa e compensa o tempo que ela já rodou.

        Args:
            time (int): Tempo atual do sistema.
            system_tick (int): Duração do tick do sistema.
        """
        self.remaining_time -= time - self.started_at + system_tick    

    def end_task(self, time: int) -> None:
        """
        Finaliza a tarefa, zerando o tempo restante.

        Args:
            time (int): Tempo atual do sistema.
        """
        self.remaining_time = 0

    def set_priority_function(self, priority_function) -> None:
        """
        Define a função de prioridade para a tarefa.

        Args:
            priority_function: Função que calcula a prioridade da tarefa.
        """
        self.priority_function = priority_function


class TaskQueue:
    """
    Classe que gerencia uma fila de tarefas usando o algoritmo de deadline.
    """
    def __init__(self) -> None:
        self.queue = []

    def put(self, task: Task) -> None:
        self.queue.append(task)
        
    def get(self) -> Task:
        """
        Obtém a tarefa com a maior prioridade (menor deadline).

        Returns:
            Task: A tarefa com a maior prioridade.
        """
        if not self.queue:
            return None
        task = min(self.queue, key=lambda x: x.priority)
        self.queue.remove(task)
        return task
    
    def empty(self) -> bool:
        return len(self.queue) == 0
    
    def peek(self) -> Task:
        """
        Visualiza a tarefa com a maior prioridade sem removê-la da fila.

        Returns:
            Task: A tarefa com a maior prioridade.
        """
        return min(self.queue, key=lambda x: x.priority)
    
    def check_deadlines(self, time: int) -> Task:
        """
        Verifica se há alguma tarefa que perdeu seu deadline.

        Args:
            time (int): Tempo atual do sistema.

        Returns:
            Task: A tarefa que perdeu o deadline, se houver.
        """
        for task in self.queue:
            if task.deadline < time:
                return task
        return None


def from_args(args, tasks):
    """
    Processa os argumentos e cria as tarefas e a fila de tarefas apropriada.

    Args:
        args (argparse.Namespace): Argumentos passados pela linha de comando.
        tasks (list[Task]): Lista de tarefas que será preenchida.

    Returns:
        tuple: Contém o tempo de simulação, tick do sistema e a fila de tarefas.
    """
    with open(args.file, "r") as file:
        # Lê cada linha do arquivo e cria as tarefas
        for line in file:
            name, cost, period = line.split()
            tasks.append(Task(name=name, period=int(period), cost=int(cost)))

    if args.time:
        simulated_time = args.time
    else:
        simulated_time = max(task.period for task in tasks) + 1

    system_tick = args.tick

    q = TaskQueue()
    # Seleciona o algoritmo de escalonamento
    if args.algorithm == "edf":
       for task in tasks:
            task.set_priority_function(lambda x: x.deadline)
    else:
        for task in tasks:
            task.set_priority_function(lambda x: x.period)
        
    return simulated_time, system_tick, q


# Configura o parser de argumentos da linha de comando
parser = argparse.ArgumentParser(description='Simula um escalonador de tarefas')
parser.add_argument('--file', '-f', type=str, required=True, help='Caminho para o arquivo de entrada')
parser.add_argument('--time', '-t', type=int, required=False, help='Tempo de simulação')
parser.add_argument('--tick', type=int, required=False, help='Tick do sistema', default=1)
parser.add_argument('--algorithm', '-a', choices=['rm', 'edf'], required=False, help='Algoritmo de escalonamento', default='rm')
args = parser.parse_args()

tasks = []

# Inicializa as tarefas e a fila de tarefas
simulated_time, system_tick, q = from_args(args, tasks)

# Inicia a simulação do escalonador
time = 0
current_task = None
df = pd.DataFrame([])
while time < simulated_time:
    # Simula o tempo
    if current_task:
        current_task.remaining_time -= system_tick

    # Verifica se a tarefa atual terminou
    if current_task and current_task.remaining_time <= 0:
        current_task.end_task(time)
        df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
        current_task = None
    
    # Inicia as tarefas em seu período
    for task in tasks:
        if time == 0 or time % task.period == 0:
            task.start_task(time)
            q.put(task)

    # Se não há tarefa atual, obtém a próxima
    if not current_task and not q.empty():
        current_task = q.get()
        current_task.run_task(time)
    
    # Verifica se há uma tarefa de maior prioridade
    if not q.empty():
        next_task = q.peek()
        if next_task.priority < current_task.priority:
            current_task.interrupt_task(time, system_tick)
            q.put(current_task) # Coloca a tarefa atual de volta na fila
            df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
            current_task = next_task
            current_task.run_task(time)
            q.get()

    # Verifica se alguma tarefa perdeu o deadline
    missed_task = q.check_deadlines(time)

    if missed_task:
        print(f"Task {missed_task.name} missed its deadline at {time}")
    time += system_tick

# Se ainda há uma tarefa, finaliza e adiciona ao dataframe
if current_task:
    current_task.end_task(time)
    df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
    #print(f"Task {current_task.name} finished at {time}")

# Verifica se há tarefas para exibir
if df.empty:
    print("No tasks were scheduled")
    exit()

# Define uma lista de cores em formato RGB para diferenciar visualmente as tarefas no gráfico.
color_rotation = ['rgb(0, 0, 255)', 'rgb(122, 122, 122)', 'rgb(255, 0, 0)', 'rgb(122, 122, 0)', 'rgb(255, 0, 255)', 'rgb(0, 255, 255)']
colors = {task.name: color_rotation[i % len(color_rotation)] for i, task in enumerate(tasks)}
fig = ff.create_gantt(df, bar_width = 0.4, show_colorbar=True,  group_tasks=True, index_col='Task', showgrid_x=True,
                      colors=colors)                       
subtitle = "<b>Tasks:</b> " + ", ".join([f"<span style='color:{colors[task.name]}'>{task.name}({task.cost}, {task.period})</span>" for task in tasks])

if args.algorithm == "rm":
    title = "Rate Monotonic"
else:
    title = "Deadline Driven"
                     
fig.update_layout(
    xaxis_type='linear',
    autosize=False,
    width=800,
    height=400,
    title={
        'text': f"<b>{title}</b>",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    },
    annotations=[
        dict(
            x=0.5,
            y=-0.15,
            xref='paper',
            yref='paper',
            text=subtitle,
            showarrow=False,
            font=dict(size=12)
        )
    ],
    xaxis=dict(
        tickmode='array',
        tickvals=[period for task in tasks for period in range(0, simulated_time, task.period)],
        ticktext=[str(period) for task in tasks for period in range(0, simulated_time, task.period)]
    )
)

# Adiciona linhas verticais no gráfico para indicar os períodos de cada tarefa:
for i, task in enumerate(tasks):
    for period in range(0, simulated_time, task.period):
        fig.add_shape(
            type="line",
            x0=period,
            y0=0,
            x1=period,
            y1=1,
            xref='x',
            yref='paper',
            line=dict(color=color_rotation[i % len(color_rotation)], width=1, dash="dash")
        )

# Save the figure png
fig.show()
