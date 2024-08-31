import pandas as pd
import plotly.figure_factory as ff
from dataclasses import dataclass
import queue
import argparse


@dataclass
class Task:
    name: str
    period: int
    cost: int
    started_at: int = 0
    remaining_time: int = 0
    deadline: int = 0
    priority_function = lambda x: 1 / x.period

    @property
    def priority(self):
        return self.priority_function(self)

    def start_task(self, time):
        self.deadline = time + self.period

    def run_task(self, time):
        self.started_at = time

        if self.remaining_time == 0:
            self.remaining_time = self.cost
            
    
    def interrupt_task(self, time, system_tick):
        # Update the remaining time of the task
        # Compensate for the time that has passed since the task started
        self.remaining_time -= time - self.started_at + system_tick    

    def end_task(self, time):
        self.remaining_time = 0

    def set_priority_function(self, priority_function):
        self.priority_function = priority_function


class DeadlineTaskQueue:
    def __init__(self):
        self.queue = []

    def put(self, task: Task):
        self.queue.append(task)
        
    def get(self):
        if not self.queue:
            return None
        task = min(self.queue, key=lambda x: x.priority)
        self.queue.remove(task)
        return task
    
    def empty(self):
        return len(self.queue) == 0
    
    def peek(self):
        return min(self.queue, key=lambda x: x.priority)
    

class RateMonotonicTaskQueue(queue.PriorityQueue):
    def put(self, task: Task):
        super().put((task.priority, task))
        
    def get(self):
        _, task = super().get()
        return task
    
    def peek(self):
        _, task = self.queue[0]
        return task


def from_args(args, tasks):
    with open(args.file, "r") as file:
    # until the end of the file
        for line in file:
            name, cost, period = line.split()
            tasks.append(Task(name=name, period=int(period), cost=int(cost)))

    if args.time:
        simulated_time = args.time
    else:
        simulated_time = max(task.period for task in tasks) + 1

    system_tick = args.tick



    if args.algorithm == "edf":
       q = DeadlineTaskQueue()
       for task in tasks:
            task.set_priority_function(lambda x: x.deadline)
    else:
        q = RateMonotonicTaskQueue()
        for task in tasks:
            task.set_priority_function(lambda x: x.period)
        
    return simulated_time,system_tick,q


parser = argparse.ArgumentParser(description='Simula um escalonador de tarefas')
parser.add_argument('--file', '-f', type=str, required=True, help='Caminho para o arquivo de entrada')
parser.add_argument('--time', '-t', type=int, required=True, help='Tempo de simulação')
parser.add_argument('--tick', type=int, required=False, help='Tick do sistema', default=1)
parser.add_argument('--algorithm', '-a', choices=['rm', 'edf'], required=False, help='Algoritmo de escalonamento', default='rm')
args = parser.parse_args()

tasks = []

simulated_time, system_tick, q = from_args(args, tasks)

time = 0
current_task = None
df = pd.DataFrame([])
while time < simulated_time:
    # Simulate time
    if current_task:
        current_task.remaining_time -= system_tick
    # Check if the current task has finished
    if current_task and current_task.remaining_time <= 0:
        current_task.end_task(time)
        df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
        #print(f"Task {current_task.name} finished at {time}")
        current_task = None
    
    # Start tasks at their period
    for task in tasks:
        if time == 0 or time % task.period == 0:
            task.start_task(time)
            q.put(task)

    # If there is no current task, get the next one
    if not current_task and not q.empty():
        current_task = q.get()
        current_task.run_task(time)
    

    # Check if there is a higher priority task
    if not q.empty():
        next_task = q.peek()
        if next_task.priority < current_task.priority:
            current_task.interrupt_task(time, system_tick)
            q.put(current_task) # Put the current task back in the queue
            df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
            #print(f"Task {current_task.name} finished at {time}")
            current_task = next_task
            current_task.run_task(time)
            q.get()

    
    time += system_tick

# if there is a task, end it and add it to the dataframe
if current_task:
    current_task.end_task(time)
    df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
    #print(f"Task {current_task.name} finished at {time}")

if df.empty:
    print("No tasks were scheduled")
    exit()

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
