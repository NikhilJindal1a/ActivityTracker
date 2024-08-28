# import time
# import json
# import os
# import tkinter as tk
# from tkinter import ttk, messagebox
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import win32gui
# from threading import Thread, Event
# import mplcursors  # Import mplcursors for interactive tooltips
# from urllib.parse import urlparse

# class ActivityTracker:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Activity Tracker")
#         self.master.geometry("800x600")

#         self.activities = {}
#         self.start_time = None
#         self.tracking = False
#         self.stop_event = Event()

#         self.start_button = ttk.Button(master, text="Start Tracking", command=self.start_tracking)
#         self.start_button.pack(pady=10, padx=20)

#         self.stop_button = ttk.Button(master, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED)
#         self.stop_button.pack(pady=10, padx=20)

#         self.show_chart_button = ttk.Button(master, text="Show Activity Chart", command=self.show_chart)
#         self.show_chart_button.pack(pady=10, padx=20)

#         self.total_time_label = tk.Label(master, text="", font=("Arial", 14))
#         self.total_time_label.pack(pady=10, padx=20)

#         self.reset_data()  # Reset data on initialization

#         # Bind the close event
#         self.master.protocol("WM_DELETE_WINDOW", self.on_close)

#     def start_tracking(self):
#         if not self.tracking:
#             self.tracking = True
#             self.start_time = time.time()
#             self.stop_event.clear()
#             self.track_thread = Thread(target=self.track)
#             self.track_thread.start()

#             self.start_button.config(state=tk.DISABLED)
#             self.stop_button.config(state=tk.NORMAL)

#     def stop_tracking(self):
#         if self.tracking:
#             self.tracking = False
#             self.stop_event.set()
#             total_time = time.time() - self.start_time
#             self.activities["Total Time"] = total_time
#             self.save_data()

#             self.start_button.config(state=tk.NORMAL)
#             self.stop_button.config(state=tk.DISABLED)

#             # Update total time label
#             self.total_time_label.config(text=f"Total Time: {self.format_time(total_time)}")

#     def track(self):
#         while not self.stop_event.is_set():
#             active_window = self.get_active_window()
#             if active_window:
#                 self.activities.setdefault(active_window, 0)
#                 self.activities[active_window] += 1
#                 self.update_chart()  # Update the chart after each activity update
#             time.sleep(1)
#             self.save_data()  # Periodic save

#     def get_active_window(self):
#         try:
#             window = win32gui.GetForegroundWindow()
#             active_window = win32gui.GetWindowText(window)
#             active_window = self.map_window_title(active_window)
#         except Exception as e:
#             active_window = None
#         return active_window

#     def map_window_title(self, title):
#         # Extract domain name from URLs
#         if " - " in title:
#             title_parts = title.split(" - ")
#             last_part = title_parts[-1]
#             if "http" in last_part or "www." in last_part:
#                 parsed_url = urlparse(last_part)
#                 return parsed_url.netloc  # Return domain name for URLs

#         return title

#     def save_data(self):
#         try:
#             with open("activities.json", "w") as file:
#                 json.dump(self.activities, file)
#         except IOError as e:
#             messagebox.showerror("Error", f"Failed to save data: {e}")

#     def load_data(self):
#         if os.path.exists("activities.json"):
#             try:
#                 with open("activities.json", "r") as file:
#                     self.activities = json.load(file)
#             except json.JSONDecodeError:
#                 self.activities = {}
#             except IOError as e:
#                 messagebox.showerror("Error", f"Failed to load data: {e}")
#         else:
#             self.activities = {}

#     def reset_data(self):
#         self.activities = {}
#         self.save_data()

#     def show_chart(self):
#         if not self.activities:
#             messagebox.showinfo("No Data", "No activity data to show.")
#             return

#         # Prepare data for the pie chart
#         filtered_activities = self.filter_activities(self.activities)
#         labels = list(filtered_activities.keys())
#         sizes = list(filtered_activities.values())

#         # Remove 'Total Time' if present to avoid showing its percentage
#         if 'Total Time' in labels:
#             labels.remove('Total Time')
#             sizes.remove(self.activities['Total Time'])

#         total_time = sum(sizes)

#         fig, ax = plt.subplots(figsize=(10, 7))  # Increase the figure size
#         wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
#         ax.axis('equal')

#         # Add interactivity with cursor
#         cursor = mplcursors.cursor(hover=True)
#         @cursor.connect("add")
#         def update_tooltip(sel):
#             index = sel.target.index
#             label = labels[index]
#             size = sizes[index]
#             duration = self.format_time(size)
#             if size >= 3600:
#                 tooltip_text = f"{label}: {duration} ({size:.1f} sec)"
#             elif size >= 60:
#                 tooltip_text = f"{label}: {duration[3:]} ({size:.1f} sec)"
#             else:
#                 tooltip_text = f"{label}: {duration[6:]} ({size:.1f} sec)"
#             sel.annotation.set_text(tooltip_text)

#         chart_window = tk.Toplevel(self.master)
#         chart_window.title("Activity Chart")
#         chart_window.geometry("800x600")  # Increase the size of the chart window

#         canvas = FigureCanvasTkAgg(fig, master=chart_window)
#         canvas.draw()
#         canvas.get_tk_widget().pack()

#         # Display total time outside the chart
#         total_time_str = f"Total Time: {self.format_time(self.activities['Total Time'])}"
#         plt.figtext(0.5, 0.02, total_time_str, ha="center", fontsize=12)

#     def update_chart(self):
#         if hasattr(self, 'chart_window') and self.chart_window:
#             # Get latest data
#             filtered_activities = self.filter_activities(self.activities)
#             labels = list(filtered_activities.keys())
#             sizes = list(filtered_activities.values())

#             # Remove 'Total Time' if present to avoid showing its percentage
#             if 'Total Time' in labels:
#                 labels.remove('Total Time')
#                 sizes.remove(self.activities['Total Time'])

#             total_time = sum(sizes)

#             # Clear existing plot
#             plt.clf()

#             # Replot pie chart with updated data
#             fig, ax = plt.subplots(figsize=(10, 7))
#             wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
#             ax.axis('equal')

#             # Add interactivity with cursor
#             cursor = mplcursors.cursor(hover=True)
#             @cursor.connect("add")
#             def update_tooltip(sel):
#                 index = sel.target.index
#                 label = labels[index]
#                 size = sizes[index]
#                 duration = self.format_time(size)
#                 if size >= 3600:
#                     tooltip_text = f"{label}: {duration} ({size:.1f} sec)"
#                 elif size >= 60:
#                     tooltip_text = f"{label}: {duration[3:]} ({size:.1f} sec)"
#                 else:
#                     tooltip_text = f"{label}: {duration[6:]} ({size:.1f} sec)"
#                 sel.annotation.set_text(tooltip_text)

#             canvas = FigureCanvasTkAgg(fig, master=self.chart_window)
#             canvas.draw()
#             canvas.get_tk_widget().pack()

#     def format_pct(self, pct, all_sizes, total_time):
#         absolute = int(pct/100.*total_time)
#         return f"{pct:.1f}%\n({self.format_time(absolute)})"

#     def format_time(self, seconds):
#         hours, remainder = divmod(seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)

#         if hours > 0:
#             return f"{int(hours)} hr {int(minutes)} min {seconds:.1f} sec"
#         elif minutes > 0:
#             return f"{int(minutes)} min {seconds:.1f} sec"
#         else:
#             return f"{seconds:.1f} sec"

#     def on_close(self):
#         if self.tracking:
#             self.stop_tracking()
#         self.master.destroy()

#     def filter_activities(self, activities):
#         filtered_activities = {}
#         ignore_list = [
#             'Start menu', 'Search', 'Task Switching', 'Task View',
#             'Cortana', 'File Explorer', 'Program Manager'
#         ]

#         for activity, count in activities.items():
#             if any(ignore in activity for ignore in ignore_list):
#                 continue
#             # Extract domain name from URLs and add to filtered activities
#             if "http" in activity or "www." in activity:
#                 parsed_url = urlparse(activity)
#                 domain_name = parsed_url.netloc
#                 filtered_activities.setdefault(domain_name, 0)
#                 filtered_activities[domain_name] += count
#             else:
#                 filtered_activities[activity] = count

#         return filtered_activities

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ActivityTracker(master=root)
#     root.mainloop()















import time
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import win32gui
from threading import Thread, Event

class ActivityTracker:
    def __init__(self, master):
        self.master = master
        self.master.title("Activity Tracker")
        self.master.geometry("800x600")

        self.activities = {}
        self.start_time = None
        self.tracking = False
        self.stop_event = Event()

        self.start_button = ttk.Button(master, text="Start Tracking", command=self.start_tracking)
        self.start_button.pack(pady=10, padx=20)

        self.stop_button = ttk.Button(master, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED)
        self.stop_button.pack(pady=10, padx=20)

        self.show_chart_button = ttk.Button(master, text="Show Activity Chart", command=self.show_chart)
        self.show_chart_button.pack(pady=10, padx=20)

        self.total_time_label = tk.Label(master, text="", font=("Arial", 14))
        self.total_time_label.pack(pady=10, padx=20)

        self.reset_data()

        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_tracking(self):
        if not self.tracking:
            self.tracking = True
            self.start_time = time.time()
            self.stop_event.clear()
            self.track_thread = Thread(target=self.track)
            self.track_thread.start()

            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_tracking(self):
        if self.tracking:
            self.tracking = False
            self.stop_event.set()
            total_time = time.time() - self.start_time
            self.activities["Total Time"] = total_time
            self.save_data()

            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

            self.total_time_label.config(text=f"Total Time: {self.format_time(total_time)}")

    def track(self):
        while not self.stop_event.is_set():
            active_window = self.get_active_window()
            if active_window:
                self.activities.setdefault(active_window, 0)
                self.activities[active_window] += 1
                self.update_chart()
            time.sleep(1)
            self.save_data()

    def get_active_window(self):
        try:
            window = win32gui.GetForegroundWindow()
            active_window = win32gui.GetWindowText(window)
            active_window = self.map_window_title(active_window)
        except Exception as e:
            active_window = None
        return active_window

    def map_window_title(self, title):
        mapping = {
            "Visual Studio Code": "Visual Studio Code",
            "Notepad": "Notepad",
            "Paint": "Paint",
            "Colaboratory": "Colab",
            "YouTube": "YouTube",
            "Google Drive": "Google Drive",
            "WhatsApp": "WhatsApp",
            "LinkedIn": "LinkedIn",
            "3D Objects": "3D Objects"
        }
        for key in mapping:
            if key in title:
                return mapping[key]
        return None

    def save_data(self):
        try:
            with open("activities.json", "w") as file:
                json.dump(self.activities, file)
        except IOError as e:
            messagebox.showerror("Error", f"Failed to save data: {e}")

    def load_data(self):
        if os.path.exists("activities.json"):
            try:
                with open("activities.json", "r") as file:
                    self.activities = json.load(file)
            except json.JSONDecodeError:
                self.activities = {}
            except IOError as e:
                messagebox.showerror("Error", f"Failed to load data: {e}")
        else:
            self.activities = {}

    def reset_data(self):
        self.activities = {}
        self.save_data()

    def show_chart(self):
        if not self.activities:
            messagebox.showinfo("No Data", "No activity data to show.")
            return

        filtered_activities = self.filter_activities(self.activities)
        labels = list(filtered_activities.keys())
        sizes = list(filtered_activities.values())

        if 'Total Time' in labels:
            labels.remove('Total Time')
            sizes.remove(self.activities['Total Time'])

        total_time = sum(sizes)

        fig, ax = plt.subplots(figsize=(10, 7))
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
        ax.axis('equal')

        chart_window = tk.Toplevel(self.master)
        chart_window.title("Activity Chart")
        chart_window.geometry("800x600")

        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

        total_time_str = f"Total Time: {self.format_time(self.activities['Total Time'])}"
        plt.figtext(0.5, 0.02, total_time_str, ha="center", fontsize=12)

    def update_chart(self):
        if hasattr(self, 'chart_window') and self.chart_window:
            filtered_activities = self.filter_activities(self.activities)
            labels = list(filtered_activities.keys())
            sizes = list(filtered_activities.values())

            if 'Total Time' in labels:
                labels.remove('Total Time')
                sizes.remove(self.activities['Total Time'])

            total_time = sum(sizes)

            plt.clf()

            fig, ax = plt.subplots(figsize=(10, 7))
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
            ax.axis('equal')

            canvas = FigureCanvasTkAgg(fig, master=self.chart_window)
            canvas.draw()
            canvas.get_tk_widget().pack()

    def format_pct(self, pct, all_sizes, total_time):
        absolute = int(pct/100.*total_time)
        return f"{pct:.1f}%\n({self.format_time(absolute)})"

    def format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            return f"{int(hours)} hr {int(minutes)} min {seconds:.1f} sec"
        elif minutes > 0:
            return f"{int(minutes)} min {seconds:.1f} sec"
        else:
            return f"{seconds:.1f} sec"

    def on_close(self):
        if self.tracking:
            self.stop_tracking()
        self.master.destroy()

    def filter_activities(self, activities):
        filtered_activities = {activity: time for activity, time in activities.items() if activity}
        return filtered_activities

if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityTracker(root)
    root.mainloop()




















# import time
# import json
# import os
# import tkinter as tk
# from tkinter import ttk, messagebox
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import win32gui
# from threading import Thread, Event
# import re

# class ActivityTracker:
#     def __init__(self, master):
#         self.master = master
#         self.master.title("Activity Tracker")
#         self.master.geometry("800x600")

#         self.activities = {}
#         self.start_time = None
#         self.tracking = False
#         self.stop_event = Event()

#         self.start_button = ttk.Button(master, text="Start Tracking", command=self.start_tracking)
#         self.start_button.pack(pady=10, padx=20)

#         self.stop_button = ttk.Button(master, text="Stop Tracking", command=self.stop_tracking, state=tk.DISABLED)
#         self.stop_button.pack(pady=10, padx=20)

#         self.show_chart_button = ttk.Button(master, text="Show Activity Chart", command=self.show_chart)
#         self.show_chart_button.pack(pady=10, padx=20)

#         self.total_time_label = tk.Label(master, text="", font=("Arial", 14))
#         self.total_time_label.pack(pady=10, padx=20)

#         self.reset_data()
#         self.master.protocol("WM_DELETE_WINDOW", self.on_close)

#     def start_tracking(self):
#         if not self.tracking:
#             self.tracking = True
#             self.start_time = time.time()
#             self.stop_event.clear()
#             self.track_thread = Thread(target=self.track)
#             self.track_thread.start()

#             self.start_button.config(state=tk.DISABLED)
#             self.stop_button.config(state=tk.NORMAL)

#     def stop_tracking(self):
#         if self.tracking:
#             self.tracking = False
#             self.stop_event.set()
#             total_time = time.time() - self.start_time
#             self.activities["Total Time"] = total_time
#             self.save_data()

#             self.start_button.config(state=tk.NORMAL)
#             self.stop_button.config(state=tk.DISABLED)

#             self.total_time_label.config(text=f"Total Time: {self.format_time(total_time)}")

#     def track(self):
#         while not self.stop_event.is_set():
#             active_window = self.get_active_window()
#             if active_window:
#                 self.activities.setdefault(active_window, 0)
#                 self.activities[active_window] += 1
#                 self.update_chart()
#             time.sleep(1)
#             self.save_data()

#     def get_active_window(self):
#         try:
#             window = win32gui.GetForegroundWindow()
#             active_window = win32gui.GetWindowText(window)
#             active_window = self.map_window_title(active_window)
#         except Exception as e:
#             active_window = None
#         return active_window

#     def map_window_title(self, title):
#         # Match specific website titles
#         if 'Best and Top Private Engineering Colleges in Himachal Pradesh' in title:
#             return 'JUIT'
#         if 'Dr. B.R. Ambedkar National Institute of Technology, Jalandhar' in title:
#             return 'NITJ'
#         if 'VR AR MR' in title:
#             return 'VRARMR'
#         if 'Wikipedia' in title:
#             return 'Wikipedia'
        
#         # Match common browser patterns and extract the main part of the title
#         browser_patterns = [
#             r' - Google Chrome',
#             r' - Mozilla Firefox',
#             r' - Microsoft Edge',
#             r' - Opera',
#             r' - Safari'
#         ]
        
#         for pattern in browser_patterns:
#             if pattern in title:
#                 site_title = re.sub(pattern, '', title).strip()
#                 # Further refine if it's a URL
#                 if ' - ' in site_title:
#                     site_title = site_title.split(' - ')[0]
#                 return site_title

#         # Filter out unwanted titles
#         unwanted_titles = [
#             "ActivityTracker and",
#             "Profile 1 - Microsoft Edge",
#             "New Tab",
#             "Settings",
#             "This PC",
#             "Program Manager",
#             "Search",
#             "Jump List for Python 3.12 (64-bit)"
#         ]

#         for unwanted in unwanted_titles:
#             if unwanted in title:
#                 return None

#         mapping = {
#             "Visual Studio Code": "Visual Studio Code",
#             "Notepad": "Notepad",
#             "Paint": "Paint",
#             "Colaboratory": "Colab",
#             "YouTube": "YouTube",
#             "Google Drive": "Google Drive",
#             "WhatsApp": "WhatsApp",
#             "LinkedIn": "LinkedIn",
#             "3D Objects": "3D Objects"
#         }

#         for key in mapping:
#             if key in title:
#                 return mapping[key]

#         return title if title else None

#     def save_data(self):
#         try:
#             with open("activities.json", "w") as file:
#                 json.dump(self.activities, file)
#         except IOError as e:
#             messagebox.showerror("Error", f"Failed to save data: {e}")

#     def load_data(self):
#         if os.path.exists("activities.json"):
#             try:
#                 with open("activities.json", "r") as file:
#                     self.activities = json.load(file)
#             except json.JSONDecodeError:
#                 self.activities = {}
#             except IOError as e:
#                 messagebox.showerror("Error", f"Failed to load data: {e}")
#         else:
#             self.activities = {}

#     def reset_data(self):
#         self.activities = {}
#         self.save_data()

#     def show_chart(self):
#         if not self.activities:
#             messagebox.showinfo("No Data", "No activity data to show.")
#             return

#         filtered_activities = self.filter_activities(self.activities)
#         labels = list(filtered_activities.keys())
#         sizes = list(filtered_activities.values())

#         if 'Total Time' in labels:
#             labels.remove('Total Time')
#             sizes.remove(self.activities['Total Time'])

#         total_time = sum(sizes)

#         fig, ax = plt.subplots(figsize=(10, 7))
#         wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
#         ax.axis('equal')

#         chart_window = tk.Toplevel(self.master)
#         chart_window.title("Activity Chart")
#         chart_window.geometry("800x600")

#         canvas = FigureCanvasTkAgg(fig, master=chart_window)
#         canvas.draw()
#         canvas.get_tk_widget().pack()

#         total_time_str = f"Total Time: {self.format_time(self.activities['Total Time'])}"
#         plt.figtext(0.5, 0.02, total_time_str, ha="center", fontsize=12)

#     def update_chart(self):
#         if hasattr(self, 'chart_window') and self.chart_window:
#             filtered_activities = self.filter_activities(self.activities)
#             labels = list(filtered_activities.keys())
#             sizes = list(filtered_activities.values())

#             if 'Total Time' in labels:
#                 labels.remove('Total Time')
#                 sizes.remove(self.activities['Total Time'])

#             total_time = sum(sizes)

#             plt.clf()

#             fig, ax = plt.subplots(figsize=(10, 7))
#             wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct=lambda pct: self.format_pct(pct, sizes, total_time), startangle=140, colors=plt.cm.Paired.colors)
#             ax.axis('equal')

#             canvas = FigureCanvasTkAgg(fig, master=self.chart_window)
#             canvas.draw()
#             canvas.get_tk_widget().pack()

#     def format_pct(self, pct, all_sizes, total_time):
#         absolute = int(pct/100.*total_time)
#         return f"{pct:.1f}%\n({self.format_time(absolute)})"

#     def format_time(self, seconds):
#         hours, remainder = divmod(seconds, 3600)
#         minutes, seconds = divmod(remainder, 60)

#         if hours > 0:
#             return f"{int(hours)} hr {int(minutes)} min {seconds:.1f} sec"
#         elif minutes > 0:
#             return f"{int(minutes)} min {seconds:.1f} sec"
#         else:
#             return f"{seconds:.1f} sec"

#     def on_close(self):
#         if self.tracking:
#             self.stop_tracking()
#         self.master.destroy()

#     def filter_activities(self, activities):
#         filtered_activities = {activity: time for activity, time in activities.items() if activity and activity not in [
#             "ActivityTracker and", "Profile 1 - Microsoft Edge", "New Tab", "Settings", "This PC", "Program Manager", "Search", "Jump List for Python 3.12 (64-bit)"]}
        
#         # Handle specific window titles such as Wikipedia
#         for key in list(filtered_activities.keys()):
#             if "Wikipedia" in key:
#                 filtered_activities["Wikipedia"] = filtered_activities.pop(key)

#         # Remove entries with unwanted patterns
#         pattern = r'https://www\.google\..*'
#         filtered_activities = {k: v for k, v in filtered_activities.items() if not re.match(pattern, k)}

#         return filtered_activities

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ActivityTracker(root)
#     root.mainloop()


























