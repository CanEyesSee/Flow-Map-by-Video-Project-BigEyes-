import tkinter as tk
import subprocess

scripts = ["display", "capture", ""]
temp_value = 0

def run_script(script_number):
    subprocess.run(["python", scripts[script_number]+".py"])

def slider_changed(value):
    temp_value = int(value)
    label1.config(text=str(scripts[temp_value]))

root = tk.Tk()
root.title("Selection App")
root.geometry("300x250")

slider1 = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, command=slider_changed)
slider1.pack(pady=20)

label1 = tk.Label(root, text=scripts[temp_value])
label1.pack(pady=20)

button1 = tk.Button(root, text="Open Program", command=lambda: run_script(slider1.get()))
button1.pack(pady=20)

root.mainloop()