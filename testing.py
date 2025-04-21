import tkinter as tk
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

zoom_level = 100
ax = None
canvas = None
time = None
breath = None
is_drag = False
drag = (0, 0)


def plot_graph():
    global ax, canvas, time, breath, zoom_level

    file_path = path_var.get()
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path, header=None, usecols=[0,5])
        time = df[0]
        breath = df[5]

        for widget in graph_frame.winfo_children():
            widget.destroy()

        zoom_level = 100
        zoom_label.config(text=f"Zoom: {zoom_level}%")

        apnea_events = []
        current_event = []
        for i in range(len(breath)):
            if breath[i] <= 2:
                current_event.append(i)
            else:
                if len(current_event) >= 3:
                    apnea_events.append(current_event)
                current_event = []
        if len(current_event) >= 3:
            apnea_events.append(current_event)

        classified_events = []
        for event in apnea_events:
            start = event[0]
            end = event[-1]
            after_end = breath[end + 1] if end + 1 < len(breath) else 0

            if after_end > 5:
                classified_events.append((start, end, 'OSA'))
            elif after_end <= 2:
                classified_events.append((start, end, 'CSA'))
            else:
                classified_events.append((start, end, 'MSA'))

        fig = Figure(figsize=(9, 4), dpi=100)
        ax = fig.add_subplot(111)

        last_end = 0
        for start, end, event_type in classified_events:
            if start > last_end:
                ax.plot(time[last_end:start], breath[last_end:start], color='green')

            color = {'OSA': 'red', 'CSA': 'blue', 'MSA': 'orange'}[event_type]
            ax.plot(time[start:end + 1], breath[start:end + 1], color=color, linewidth=0.5)

            last_end = end + 2

        if last_end < len(time):
            ax.plot(time[last_end:], breath[last_end:], color='green')

        osa_count = sum(1 for _, _, t in classified_events if t == 'OSA')
        csa_count = sum(1 for _, _, t in classified_events if t == 'CSA')
        msa_count = sum(1 for _, _, t in classified_events if t == 'MSA')

        ax.set_title(f"OSA: {osa_count}   CSA: {csa_count}   MSA: {msa_count}", fontsize=12)
        ax.set_xlabel("Time")
        ax.set_ylabel("Breath Value")
        ax.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()

        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        canvas.mpl_connect("button_press_event", on_press)
        canvas.mpl_connect("button_release_event", on_release)
        canvas.mpl_connect("motion_notify_event", on_drag)
        
        canvas_widget.bind("<MouseWheel>", on_mousewheel)

        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

    except Exception as e:
        print(f"Error: {e}")

def zoom(factor):
    global ax, canvas, zoom_level
    if ax is None or canvas is None:
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2

    x_range = (xlim[1] - xlim[0]) * factor
    y_range = (ylim[1] - ylim[0]) * factor

    ax.set_xlim(x_center - x_range / 2, x_center + x_range / 2)
    ax.set_ylim(y_center - y_range / 2, y_center + y_range / 2)

    canvas.draw()

    if factor < 1:
        zoom_level *= 1.2
    else:
        zoom_level /= 1.2
        
    zoom_level = max(10, min(zoom_level, 1000))
    zoom_label.config(text=f"Zoom: {int(zoom_level)}%")
    
    resize_canvas(zoom_level)
    canvas.draw()
    
def resize_canvas(zoom_level):
    scale = zoom_level / 100
    new_width = int(600 * scale)
    new_height = int(300 * scale)
    canvas.get_tk_widget().config(width=new_width, height=new_height)
    canvas.get_tk_widget().update_idletasks()

def zoom_in():
    zoom(0.8)

def zoom_out():
    zoom(1.2)

def reset_zoom():
    global ax, canvas, time, breath, zoom_level
    if ax is None or time is None or breath is None:
        return
    ax.set_xlim(time.iloc[0], time.iloc[-1])
    ax.set_ylim(breath.min(), breath.max())
    zoom_level = 100
    resize_canvas(zoom_level)
    canvas.draw()
    
    zoom_label.config(text=f"Zoom: {int(zoom_level)}%")

def on_press(event):
    global is_drag, drag
    if event.inaxes:
        is_drag = True
        drag = (event.xdata, event.ydata)

def on_release(event):
    global is_drag
    is_drag = False

def on_drag(event):
    global is_drag, drag, ax, canvas
    if is_drag and event.inaxes and drag:
        dx = drag[0] - event.xdata
        dy = drag[1] - event.ydata
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ax.set_xlim(xlim[0] + dx, xlim[1] + dx)
        ax.set_ylim(ylim[0] + dy, ylim[1] + dy)
        drag = (event.xdata, event.ydata)
        canvas.draw()

def on_mousewheel(event):
    if event.delta > 0:
        zoom_in()
    else:
        zoom_out()

# GUI setup
root = tk.Tk()
root.title("Breath Trend Viewer")
root.geometry("1100x700")

path_var = tk.StringVar(root, value="https://raw.githubusercontent.com/Pratyaksh568/Test/refs/heads/main/DATA2304.csv")

tk.Label(root, text="CSV File Path:", font=("Arial", 12)).pack(pady=5)
tk.Entry(root, text=path_var, width=80, font=("Arial", 11)).pack(pady=5)
tk.Button(root, text="Plot Graph", command=plot_graph, font=("Arial", 11)).pack(pady=5)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

tk.Button(button_frame, text="Zoom In", command=zoom_in, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Zoom Out", command=zoom_out, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
tk.Button(button_frame, text="Reset Zoom", command=reset_zoom, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

zoom_label = tk.Label(button_frame, text="Zoom: 0%", font=("Arial", 10, "bold"))
zoom_label.pack(side=tk.LEFT, padx=10)

graph_frame = tk.Frame(root)
graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)

root.mainloop()