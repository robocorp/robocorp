"""
File used to test capabilities of robocorp-windows.
"""


def main():
    import tkinter as tk
    from tkinter import ttk

    # Create a function to display selected option from combobox
    def show_selected_option():
        selected_option = combo_var.get()
        result_label.config(text=f"Selected Option: {selected_option}")

    # Create the main application window
    app = tk.Tk()
    app.title("Tkinter Elements Showcase")

    # Label Widget
    label = tk.Label(app, text="Label Element", font=("Helvetica", 14))
    label.pack(pady=10)

    # Button Widget
    button = tk.Button(app, text="Button Element", command=lambda: button_click())
    button.pack()

    # Function to open a new dialog
    def open_dialog():
        dialog = tk.Toplevel(app)
        dialog.title("New Dialog")

        # Add widgets to the dialog
        label = tk.Label(dialog, text="This is a new dialog.")
        label.pack(padx=20, pady=20)

        close_button = tk.Button(dialog, text="Close Dialog", command=dialog.destroy)
        close_button.pack(pady=10)

    # Button to open the dialog
    open_button = tk.Button(app, text="Open Dialog", command=open_dialog)
    open_button.pack(pady=20)

    # Entry Widget
    entry = tk.Entry(app, width=30)
    entry.pack(pady=10)

    # Radio Buttons
    radio_frame = tk.LabelFrame(app, text="Radio Buttons")
    radio_var = tk.StringVar(value="Option 1")

    radio_button1 = tk.Radiobutton(
        radio_frame, text="Option 1", variable=radio_var, value="Option 1"
    )
    radio_button2 = tk.Radiobutton(
        radio_frame, text="Option 2", variable=radio_var, value="Option 2"
    )
    radio_button1.pack()
    radio_button2.pack()
    radio_frame.pack(pady=10)

    # Checkbuttons
    check_frame = tk.LabelFrame(app, text="Checkbuttons")
    check_var1 = tk.IntVar()
    check_var2 = tk.IntVar()

    check_button1 = tk.Checkbutton(check_frame, text="Check 1", variable=check_var1)
    check_button2 = tk.Checkbutton(check_frame, text="Check 2", variable=check_var2)
    check_button1.pack()
    check_button2.pack()
    check_frame.pack(pady=10)

    # Combobox (Dropdown Menu)
    combo_frame = tk.LabelFrame(app, text="Combobox")
    combo_var = tk.StringVar()
    combo_box = ttk.Combobox(
        combo_frame, textvariable=combo_var, values=["Option A", "Option B", "Option C"]
    )
    combo_box.pack()
    show_button = tk.Button(
        combo_frame, text="Show Selected Option", command=show_selected_option
    )
    show_button.pack()
    result_label = tk.Label(combo_frame, text="", font=("Helvetica", 12))
    result_label.pack()
    combo_frame.pack(pady=10)

    # Function to handle button click event
    def button_click():
        entry_text = entry.get()
        radio_selection = radio_var.get()
        check1_state = check_var1.get()
        check2_state = check_var2.get()

        result_label.config(
            text=(
                f"Entry Text: {entry_text}\nRadio Selection: {radio_selection}\n"
                f"Check 1: {check1_state}\nCheck 2: {check2_state}"
            )
        )

    app.mainloop()


if __name__ == "__main__":
    main()
