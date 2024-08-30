import pandas as pd
import plotly.figure_factory as ff
from dataclasses import dataclass
import queue


@dataclass
class Task:
    name: str
    period: int
    cost: int
    priority: int = 0
    started_at: int = 0
    remaining_time: int = 0

    def start_task(self, time):
        self.started_at = time

        if self.remaining_time == 0:
            self.remaining_time = self.cost
    
    def interrupt_task(self, time, system_tick):
        # Update the remaining time of the task
        # Compensate for the time that has passed since the task started
        self.remaining_time += 0

    def end_task(self, time):
        self.remaining_time = 0
    




# Generate some tasks, with name, cost, period.
tasks = []
task_count, simulated_time, system_tick = map(int, input().split())
for i in range(task_count):
    name, cost, period = input().split()
    tasks.append(Task(name, int(period), int(cost)))


# Rate monotonic scheduling algorithm

for task in tasks:
    task.priority = task.period


system_tick = 1
time = 0
current_task = None

#df = pd.DataFrame([])

q = queue.PriorityQueue()
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
            q.put((task.priority, task))

    # If there is no current task, get the next one
    if not current_task and q.qsize() > 0:
        _, current_task = q.get()
        current_task.start_task(time)
    

    # Check if there is a higher priority task
    if not q.empty():
        next_task = q.queue[0][1]
        if next_task.priority < current_task.priority:
            current_task.interrupt_task(time, system_tick)
            q.put((current_task.priority, current_task)) # Put the current task back in the queue
            df = pd.concat([df, pd.DataFrame({'Task': [current_task.name], 'Start': [current_task.started_at], 'Finish': [time]})])
            #print(f"Task {current_task.name} finished at {time}")
            current_task = next_task
            current_task.start_task(time)
            q.get()

    
    time += system_tick

if df.empty:
    print("No tasks were scheduled")
    exit()
# Create subtitle



color_rotation = ['rgb(0, 0, 255)', 'rgb(122, 122, 122)', 'rgb(255, 0, 0)', 'rgb(255, 255, 0)', 'rgb(255, 0, 255)', 'rgb(0, 255, 255)']
colors = {task.name: color_rotation[i % len(color_rotation)] for i, task in enumerate(tasks)}
fig = ff.create_gantt(df, bar_width = 0.4, show_colorbar=True,  group_tasks=True, index_col='Task', showgrid_x=True,
                      colors=colors)                       
subtitle = "<b>Tasks:</b> " + ", ".join([f"<span style='color:{colors[task.name]}'>{task.name}({task.cost}, {task.period})</span>" for task in tasks])
                      
fig.update_layout(
    xaxis_type='linear',
    autosize=False,
    width=800,
    height=400,
    title={
        'text': "Gantt Chart",
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

# Show the fig as img
fig.show()
