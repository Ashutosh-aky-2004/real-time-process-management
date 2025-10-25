import psutil
import tkinter as tk
import subprocess
import shlex
import matplotlib.pyplot as plt
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Enhanced Color Palette
BACKGROUND_COLOR = "#f0faff"
TEXT_COLOR = "#0d1b2a"
BUTTON_COLOR = "#00a676"
ALERT_COLOR = "#ff595e"
HIGHLIGHT_COLOR = "#ffffff"
ACCENT_COLOR_1 = "#6a4c93"
ACCENT_COLOR_2 = "#1982c4"
ACCENT_COLOR_3 = "#ffca3a"
DEFAULT_FONT = ("Arial", 14)
TITLE_FONT = ("Arial", 16, "bold")

# Fetch and filter process data
def get_process_data(filter_name=""):
    return sorted(
        [
            process.info
            for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
            if filter_name.lower() in process.info['name'].lower() and process.info['pid'] != 0
        ],
        key=lambda x: x['cpu_percent'],
        reverse=True
    )

def update_process_table(filter_name=""):
    process_tree.delete(*process_tree.get_children())
    for process in get_process_data(filter_name):
        process_tree.insert(
            "",
            "end",
            values=(
                process['pid'],
                process['name'],
                process['cpu_percent'],
                f"{process['memory_percent']:.2f}%"
            ),
            tags=('high_usage' if process['cpu_percent'] > 80 or process['memory_percent'] > 80 else '',)
        )

cpu_usage_history = []
memory_usage_history = []

def update_usage_graph():
    current_cpu_usage = psutil.cpu_percent()
    current_memory_usage = psutil.virtual_memory().percent
    cpu_usage_history.extend(
        [current_cpu_usage] if len(cpu_usage_history) < 30 else [cpu_usage_history.pop(0), current_cpu_usage]
    )
    memory_usage_history.extend(
        [current_memory_usage] if len(memory_usage_history) < 30 else [memory_usage_history.pop(0), current_memory_usage]
    )
    graph_axes.clear()
    graph_axes.plot(
        cpu_usage_history,
        label='CPU Usage %',
        color=ACCENT_COLOR_1,
        linewidth=3,
        alpha=0.8,
        marker='o',
        markersize=4
    )
    graph_axes.plot(
        memory_usage_history,
        label='Memory Usage %',
        color=ACCENT_COLOR_2,
        linewidth=3,
        alpha=0.8,
        marker='s',
        markersize=4
    )
    graph_axes.set_facecolor('#f5f5f5')
    graph_axes.grid(True, linestyle='--', alpha=0.6)
    graph_axes.set_ylim(0, 100)
    graph_axes.set_title(
        "CPU and Memory Usage Over Time",
        fontsize=12,
        pad=10,
        color=TEXT_COLOR
    )
    graph_axes.legend(loc='upper right', framealpha=0.9)
    for spine in graph_axes.spines.values():
        spine.set_visible(False)
    graph_axes.spines['bottom'].set_visible(True)
    graph_axes.spines['left'].set_visible(True)
    graph_canvas.draw()

def execute_process_action(pid_entry, action, status_label):
    if pid := pid_entry.get():
        try:
            getattr(psutil.Process(int(pid)), action)()
            status_label.config(text=f"Process {pid} {action}ed.", fg=BUTTON_COLOR)
        except Exception as error:
            status_label.config(text=f"Error: {str(error)}", fg=ALERT_COLOR)

def start_new_process():
    if command := new_process_entry.get():
        try:
            subprocess.Popen(shlex.split(command))
            new_process_status_label.config(text=f"Process '{command}' started.", fg=BUTTON_COLOR)
        except Exception as error:
            new_process_status_label.config(text=f"Error: {str(error)}", fg=ALERT_COLOR)

def update_system_summary():
    memory_info = psutil.virtual_memory()
    cpu_usage_label.config(text=f"CPU Usage: {psutil.cpu_percent()}%")
    memory_usage_label.config(text=f"Memory Usage: {memory_info.percent}%")
    total_memory_label.config(text=f"Total Memory: {round(memory_info.total / (1024**3), 2)} GB")

def check_resource_alerts():
    alerts = [
        f"High usage: {process.info['name']} (PID {process.info['pid']})"
        for process in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent'])
        if process.info['pid'] != 0 and (process.info['cpu_percent'] > 98 or process.info['memory_percent'] > 98)
    ]
    if alerts:
        messagebox.showwarning("Resource Alert", "\n".join(alerts))

def periodic_update():
    update_process_table(search_entry.get())
    update_usage_graph()
    update_system_summary()
    # check_resource_alerts()
    main_window.after(2000, periodic_update)

def create_summary_card(parent, title, value, color):
    card_frame = tk.Frame(parent, bg='white', bd=1, relief=tk.RAISED, padx=10, pady=5)
    tk.Label(card_frame, text=title, bg='white', fg=TEXT_COLOR, font=DEFAULT_FONT).pack()
    value_label = tk.Label(
        card_frame,
        text=value,
        bg='white',
        fg=color,
        font=("Arial", 14, "bold")
    )
    value_label.pack()
    card_frame.pack(side=tk.LEFT, padx=10, ipadx=20)
    return value_label

# Main window setup
main_window = tk.Tk()
main_window.title("Enhanced Process Monitor Dashboard")
main_window.geometry("1100x800")
main_window.config(bg=BACKGROUND_COLOR)

# Header
header_frame = tk.Frame(main_window, bg=ACCENT_COLOR_1, height=50)
tk.Label(
    header_frame,
    text="System Process Monitor",
    bg=ACCENT_COLOR_1,
    fg="white",
    font=("Arial", 16, "bold")
).pack(pady=10, fill=tk.X)
header_frame.pack(fill=tk.X)

# Summary
summary_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
summary_frame.pack(pady=10, padx=20, fill=tk.X)
cpu_usage_label = create_summary_card(summary_frame, "CPU Usage", "0%", ACCENT_COLOR_1)
memory_usage_label = create_summary_card(summary_frame, "Memory Usage", "0%", ACCENT_COLOR_2)
total_memory_label = create_summary_card(summary_frame, "Total Memory", "0 GB", ACCENT_COLOR_3)

# Search
search_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
search_frame.pack(pady=10, padx=20, fill=tk.X)
tk.Label(search_frame, text="Search Process:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=DEFAULT_FONT).pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame, font=DEFAULT_FONT, bd=2, relief=tk.GROOVE)
search_entry.pack(side=tk.LEFT, padx=5, ipady=3, fill=tk.X, expand=True)

# Process Actions
action_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
action_frame.pack(pady=10, padx=20, fill=tk.X)
tk.Label(action_frame, text="Process Actions:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=TITLE_FONT).pack(anchor=tk.W)
pid_frame = tk.Frame(action_frame, bg=BACKGROUND_COLOR)
pid_frame.pack(fill=tk.X, pady=5)
tk.Label(pid_frame, text="Enter PID:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=DEFAULT_FONT).pack(side=tk.LEFT)
pid_entry = tk.Entry(pid_frame, font=DEFAULT_FONT, bd=2, relief=tk.GROOVE)
pid_entry.pack(side=tk.LEFT, padx=5, ipady=3)
action_status_label = tk.Label(main_window, text="", fg=BUTTON_COLOR, bg=BACKGROUND_COLOR, font=DEFAULT_FONT)
action_status_label.pack(pady=5)
for text, action, color in [
    ("Kill", "terminate", ALERT_COLOR),
    ("Suspend", "suspend", "#ff9e00"),
    ("Resume", "resume", BUTTON_COLOR)
]:
    tk.Button(
        pid_frame,
        text=text,
        bg=color,
        fg="white",
        font=DEFAULT_FONT,
        bd=0,
        padx=15,
        pady=5,
        relief=tk.RAISED,
        command=lambda act=action: execute_process_action(pid_entry, act, action_status_label)
    ).pack(side=tk.LEFT, padx=5)

# Treeview
process_tree_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
process_tree_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
tree_style = ttk.Style()
tree_style.theme_use('clam')
tree_style.configure(
    "Treeview",
    background="white",
    foreground=TEXT_COLOR,
    fieldbackground="white",
    rowheight=30,
    font=DEFAULT_FONT,
    bordercolor=BACKGROUND_COLOR
)
tree_style.configure(
    "Treeview.Heading",
    font=("Arial", 12, "bold"),
    background=ACCENT_COLOR_1,
    foreground="white",
    relief=tk.FLAT
)
tree_style.map('Treeview', background=[('selected', '#cfe2f3')], foreground=[('selected', TEXT_COLOR)])
process_tree = ttk.Treeview(
    process_tree_frame,
    columns=("PID", "Name", "CPU %", "Memory %"),
    show='headings'
)
for column in ["PID", "Name", "CPU %", "Memory %"]:
    process_tree.heading(column, text=column)
    process_tree.column(column, width=150, anchor=tk.CENTER)
process_tree.tag_configure('high_usage', background='#ffebee')
process_tree.pack(fill=tk.BOTH, expand=True)

# Create Process
new_process_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
new_process_frame.pack(pady=10, padx=20, fill=tk.X)
tk.Label(
    new_process_frame,
    text="Create New Process:",
    bg=BACKGROUND_COLOR,
    fg=TEXT_COLOR,
    font=TITLE_FONT
).pack(anchor=tk.W)
new_process_entry = tk.Entry(new_process_frame, font=DEFAULT_FONT, bd=2, relief=tk.GROOVE)
new_process_entry.pack(side=tk.LEFT, padx=5, ipady=3, fill=tk.X, expand=True)
tk.Button(
    new_process_frame,
    text="Start",
    bg=BUTTON_COLOR,
    fg="white",
    font=DEFAULT_FONT,
    bd=0,
    padx=15,
    pady=5,
    command=start_new_process
).pack(side=tk.LEFT, padx=5)
new_process_status_label = tk.Label(
    main_window,
    text="",
    fg=BUTTON_COLOR,
    bg=BACKGROUND_COLOR,
    font=DEFAULT_FONT
)
new_process_status_label.pack(pady=5)

# Graph
graph_frame = tk.Frame(main_window, bg=BACKGROUND_COLOR)
graph_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
graph_figure, graph_axes = plt.subplots(figsize=(8, 3), facecolor=BACKGROUND_COLOR)
graph_figure.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.2)
graph_canvas = FigureCanvasTkAgg(graph_figure, master=graph_frame)
graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Footer
footer_frame = tk.Frame(main_window, bg=ACCENT_COLOR_1, height=30)
tk.Label(
    footer_frame,
    text="System Monitor v1.0",
    bg=ACCENT_COLOR_1,
    fg="white",
    font=("Arial", 10)
).pack(pady=5, fill=tk.X, side=tk.BOTTOM)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

periodic_update()
main_window.mainloop()
