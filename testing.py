



import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def plot_graph():
    file_path = path_var.get()
    if not file_path:
        return

    try:
        df = pd.read_csv(file_path, header=None)
        time = df[0]
        breath = df[5]

        # Clear previous widgets in the frame
        for widget in graph_frame.winfo_children():
            widget.destroy()

        # Detect Apnea Events
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

        # Classify events
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

        # Plotting
        fig, ax = plt.subplots(figsize=(9, 4))

        last_end = 0
        for start, end, event_type in classified_events:
            if start > last_end:
                ax.plot(time[last_end:start], breath[last_end:start], color='green')

            color = {'OSA': 'red', 'CSA': 'blue', 'MSA': 'orange'}[event_type]
            ax.plot(time[start:end+1], breath[start:end+1], color=color, linewidth=2)

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

        # Embed plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()

        # Add toolbar (zoom, pan, save)
        toolbar = NavigationToolbar2Tk(canvas, graph_frame)
        toolbar.update()
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Now pack the canvas
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except Exception as e:
        print(f"Error: {e}")

# GUI setup
root = tk.Tk()
root.title("Breath Trend Viewer")
root.geometry("1000x600")

path_var = tk.StringVar(root, value="C:\\Users\\Deckmount\\Documents\\DATA0637.csv")

tk.Label(root, text="CSV File Path:", font=("Arial", 12)).pack(pady=5)
tk.Entry(root, width=70, font=("Arial", 11)).pack(pady=5)
tk.Button(root, text="Plot Graph", command=plot_graph, font=("Arial", 11)).pack(pady=5)

graph_frame = tk.Frame(root)
graph_frame.pack(fill=tk.BOTH, expand=True, pady=10)

root.mainloop()
