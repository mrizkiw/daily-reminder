import tkinter as tk
from tkinter import simpledialog, messagebox
import datetime
import os
import json

REMINDER_FILE = "reminders.json"
STATUS_FILE = "reminder_status.txt"

def load_reminders():
    if not os.path.exists(REMINDER_FILE):
        # Default reminders
        return [
            {"name": "HSR", "reset_hour": 3, "reset_minute": 0},
            {"name": "Wuwa", "reset_hour": 3, "reset_minute": 0},
            {"name": "ZZZ", "reset_hour": 3, "reset_minute": 0},
            {"name": "GFL2", "reset_hour": 15, "reset_minute": 0},
            {"name": "Wows", "reset_hour": 1, "reset_minute": 0},
        ]
    with open(REMINDER_FILE, "r") as f:
        return json.load(f)

def save_reminders(reminders):
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f)

def load_status():
    if not os.path.exists(STATUS_FILE):
        return {}
    with open(STATUS_FILE, "r") as f:
        lines = f.readlines()
    status = {}
    for line in lines:
        name, date = line.strip().split(",")
        status[name] = date
    return status

def save_status(status):
    with open(STATUS_FILE, "w") as f:
        for name, date in status.items():
            f.write(f"{name},{date}\n")

def reset_status_if_needed(reminders, status):
    now = datetime.datetime.now()
    changed = False
    for reminder in reminders:
        reset_hour = reminder.get("reset_hour", 0)
        reset_minute = reminder.get("reset_minute", 0)
        reset_time = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)
        if now >= reset_time:
            # Jika sudah lewat waktu reset, hapus status jika waktu reset sudah terlewati
            reset_str = reset_time.strftime("%Y-%m-%d %H:%M")
            if status.get(reminder["name"], "") and now.strftime("%Y-%m-%d %H:%M") >= status[reminder["name"]]:
                status[reminder["name"]] = ""
                changed = True
    if changed:
        save_status(status)

def get_next_reset(reminder):
    now = datetime.datetime.now()
    reset_hour = reminder.get("reset_hour", 0)
    reset_minute = reminder.get("reset_minute", 0)
    reset_time = now.replace(hour=reset_hour, minute=reset_minute, second=0, microsecond=0)
    if now >= reset_time:
        reset_time += datetime.timedelta(days=1)
    return reset_time.strftime("%Y-%m-%d %H:%M")

class ReminderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Daily Reminder")
        self.configure(bg="#f5f6fa")
        self.reminders = load_reminders()
        self.status = load_status()
        reset_status_if_needed(self.reminders, self.status)
        self.vars = {}
        self.check_buttons = {}
        self.create_widgets()
        self.update_clock()

    def create_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.clock_label = tk.Label(self, font=("Segoe UI", 24, "bold"), bg="#f5f6fa", fg="#0097e6")
        self.clock_label.pack(pady=(15, 0))

        header = tk.Label(self, text="Daily Reminder", font=("Segoe UI", 20, "bold"), bg="#f5f6fa", fg="#273c75")
        header.pack(pady=(10, 5))

        today_label = tk.Label(self, text=f"Today: {datetime.datetime.now().strftime('%A, %d %B %Y')}", font=("Segoe UI", 12), bg="#f5f6fa", fg="#353b48")
        today_label.pack(pady=(0, 15))

        frame = tk.Frame(self, bg="#f5f6fa")
        frame.pack(padx=20, pady=10, fill="x")

        self.vars = {}
        self.check_buttons = {}

        for reminder in self.reminders:
            var = tk.BooleanVar(value=self.status.get(reminder["name"], "") == datetime.datetime.now().strftime("%Y-%m-%d"))
            row = tk.Frame(frame, bg="#f5f6fa")
            row.pack(fill="x", pady=4)
            btn = tk.Button(
                row,
                text=self.get_checkbox_text(reminder["name"], var.get()),
                font=("Segoe UI", 14),
                bg="#f5f6fa",
                fg="#44bd32" if var.get() else "#353b48",
                bd=0,
                anchor="w",
                relief="flat",
                command=lambda n=reminder["name"]: self.toggle_reminder(n)
            )
            btn.pack(side="left", fill="x", expand=True, ipadx=8)
            edit_btn = tk.Button(
                row, text="✏️", font=("Segoe UI", 12), bg="#f5f6fa", bd=0,
                command=lambda r=reminder: self.edit_reminder(r)
            )
            edit_btn.pack(side="right", padx=2)
            del_btn = tk.Button(
                row, text="🗑️", font=("Segoe UI", 12), bg="#f5f6fa", bd=0,
                command=lambda r=reminder: self.delete_reminder(r)
            )
            del_btn.pack(side="right", padx=2)
            self.vars[reminder["name"]] = var
            self.check_buttons[reminder["name"]] = btn

        add_btn = tk.Button(self, text="➕ Add Reminder", font=("Segoe UI", 12, "bold"), bg="#00b894", fg="white", command=self.add_reminder, relief="flat")
        add_btn.pack(pady=(10, 0), ipadx=10, ipady=2)

        reset_btn = tk.Button(self, text="🔄 Reset All", font=("Segoe UI", 12, "bold"), bg="#e1b12c", fg="white", command=self.reset_all, relief="flat")
        reset_btn.pack(pady=(10, 10), ipadx=10, ipady=2)

        self.status_label = tk.Label(self, text="", font=("Segoe UI", 10), bg="#f5f6fa", fg="#e84118")
        self.status_label.pack(pady=(0, 10))
        self.update_status_label()

        # --- Tambahan agar window resize otomatis ---
        self.update_idletasks()
        min_width = 400
        min_height = max(540, self.winfo_height())
        self.geometry(f"{min_width}x{min_height}")

    def get_checkbox_text(self, name, checked):
        return f"{'✅' if checked else '⬜'}  {name}"

    def toggle_reminder(self, name):
        var = self.vars[name]
        var.set(not var.get())
        if var.get():
            # Simpan waktu reset berikutnya
            reminder = next(r for r in self.reminders if r["name"] == name)
            self.status[name] = get_next_reset(reminder)
        else:
            self.status[name] = ""
        save_status(self.status)
        self.check_buttons[name].config(
            text=self.get_checkbox_text(name, var.get()),
            fg="#44bd32" if var.get() else "#353b48",
            bg="#dff9fb" if var.get() else "#f5f6fa"
        )
        self.update_status_label()

    def reset_all(self):
        for name, var in self.vars.items():
            var.set(False)
            self.status[name] = ""
            self.check_buttons[name].config(
                text=self.get_checkbox_text(name, False),
                fg="#353b48",
                bg="#f5f6fa"
            )
        save_status(self.status)
        self.update_status_label()

    def update_status_label(self):
        done = [name for name, var in self.vars.items() if var.get()]
        if done:
            self.status_label.config(text=f"Completed: {', '.join(done)}")
        else:
            self.status_label.config(text="No reminders completed today.")

    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.config(text=now)
        self.status = load_status()
        reset_status_if_needed(self.reminders, self.status)
        for name, var in self.vars.items():
            checked = bool(self.status.get(name, ""))
            var.set(checked)
            self.check_buttons[name].config(
                text=self.get_checkbox_text(name, checked),
                fg="#44bd32" if checked else "#353b48",
                bg="#dff9fb" if checked else "#f5f6fa"
            )
        self.update_status_label()
        self.after(1000, self.update_clock)

    def add_reminder(self):
        name = simpledialog.askstring("Add Reminder", "Reminder name:")
        if not name:
            return
        try:
            hour = int(simpledialog.askstring("Add Reminder", "Reset hour (0-23):"))
            minute = int(simpledialog.askstring("Add Reminder", "Reset minute (0-59):"))
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid", "Jam dan menit harus diisi dengan benar (0-23 dan 0-59).")
            return
        for r in self.reminders:
            if r["name"] == name:
                messagebox.showerror("Duplicate", "Reminder name already exists.")
                return
        self.reminders.append({"name": name, "reset_hour": hour, "reset_minute": minute})
        save_reminders(self.reminders)
        self.create_widgets()

    def edit_reminder(self, reminder):
        name = simpledialog.askstring("Edit Reminder", "Reminder name:", initialvalue=reminder["name"])
        if not name:
            return
        try:
            hour = int(simpledialog.askstring("Edit Reminder", "Reset hour (0-23):", initialvalue=str(reminder.get("reset_hour", 0))))
            minute = int(simpledialog.askstring("Edit Reminder", "Reset minute (0-59):", initialvalue=str(reminder.get("reset_minute", 0))))
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError
        except Exception:
            messagebox.showerror("Invalid", "Jam dan menit harus diisi dengan benar (0-23 dan 0-59).")
            return
        for r in self.reminders:
            if r["name"] == name and r is not reminder:
                messagebox.showerror("Duplicate", "Reminder name already exists.")
                return
        old_name = reminder["name"]
        reminder["name"] = name
        reminder["reset_hour"] = hour
        reminder["reset_minute"] = minute
        if old_name != name:
            self.status[name] = self.status.pop(old_name, "")
        save_reminders(self.reminders)
        save_status(self.status)
        self.create_widgets()

    def delete_reminder(self, reminder):
        if messagebox.askyesno("Delete", f"Delete reminder '{reminder['name']}'?"):
            self.reminders.remove(reminder)
            self.status.pop(reminder["name"], None)
            save_reminders(self.reminders)
            save_status(self.status)
            self.create_widgets()

if __name__ == "__main__":
    app = ReminderApp()
    app.geometry("400x560")
    app.mainloop()