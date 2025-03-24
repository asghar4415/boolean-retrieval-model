import tkinter as tk
from tkinter import messagebox, scrolledtext
from main import BooleanRetrievalModel

# Initialize IR Model
ir_model = BooleanRetrievalModel()

# Query Handler Function


def search_query():
    query = query_entry.get().strip()
    if not query:
        messagebox.showwarning("Empty Query", "Please enter a query.")
        return

    if '/' in query:
        results = ir_model.process_proximity_query(query)
    else:
        results = ir_model.process_boolean_query(query)

    result_display.delete(1.0, tk.END)

    if results:
        result_display.insert(tk.END, "Matching Document IDs:\n\n")

        # Format results in table-like layout (5 columns per row)
        for i in range(len(results)):
            # fixed-width 5 spaces
            result_display.insert(tk.END, f"{results[i]:<5}")
            if (i + 1) % 5 == 0:
                result_display.insert(tk.END, "\n")
    else:
        result_display.insert(tk.END, "No matching documents found.")


# Set up Main Window
window = tk.Tk()
window.title("Boolean IR Model")
window.geometry("650x600")
window.configure(bg="#f0f0f0")

# Title Label
tk.Label(window, text="Boolean IR Model", bg="#f0f0f0",
         font=("Arial", 16, "bold")).pack(pady=10)

# Query Input Section
tk.Label(window, text="Enter Your Query:",
         bg="#f0f0f0", font=("Arial", 12)).pack(pady=5)
query_entry = tk.Entry(window, width=70, font=("Arial", 12))
query_entry.pack(pady=5)

# Search Button
search_btn = tk.Button(window, text="Search", command=search_query, font=(
    "Arial", 12), bg="#4CAF50", fg="white", width=15)
search_btn.pack(pady=10)

# Result Display Box
result_display = scrolledtext.ScrolledText(
    window, wrap=tk.WORD, width=75, height=12, font=("Arial", 10))
result_display.pack(pady=10)

# Guide Section
guide_text = (
    "QUERY GUIDE:\n"
    "• Simple Boolean Queries:\n"
    "   ➤ Example: image AND restoration\n"
    "   ➤ Example: NOT deep\n\n"
    "• Complex Boolean Queries (3 terms max):\n"
    "   ➤ Example: time AND series AND classification\n"
    "   ➤ Example: time AND series OR classification\n\n"
    "• Proximity Queries:\n"
    "   ➤ Format: term1 term2 /k\n"
    "   ➤ Example: neural information /2\n"
    "   ➤ Example: feature track /5"
)

guide_label = tk.Label(window, text=guide_text, bg="#f0f0f0",
                       justify="left", anchor="w", font=("Arial", 10))
guide_label.pack(padx=20, pady=10, fill="both")

# Run UI Loop
window.mainloop()
