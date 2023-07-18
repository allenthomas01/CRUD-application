import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os

from dotenv import load_dotenv

load_dotenv()


HOST = '127.0.0.1'
USER = 'root'
PASSWORD = os.getenv('YOUR_DB_PASSWORD_IN_ENV_FILE')
DATABASE = 'CRUD'

class StudentCRUDApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Student CRUD Application")
        self.geometry("1920x1080")

        self.tree = ttk.Treeview(self, columns=("ID", "Name", "Class", "Batch Year", "Mobile"))
        self.tree.heading("#1", text="ID")
        self.tree.heading("#2", text="Name")
        self.tree.heading("#3", text="Class")
        self.tree.heading("#4", text="Batch Year")
        self.tree.heading("#5", text="Mobile")
        self.tree.grid(row=6, column=0, columnspan=4, padx=10, pady=5)

        tk.Label(self, text="Student Name:").grid(row=0, column=0, padx=10, pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(self, textvariable=self.name_var).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Student Class:").grid(row=1, column=0, padx=10, pady=5)
        self.class_var = tk.StringVar()
        tk.Entry(self, textvariable=self.class_var).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Batch Year:").grid(row=2, column=0, padx=10, pady=5)
        self.batch_var = tk.IntVar()
        tk.Entry(self, textvariable=self.batch_var).grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Mobile Number:").grid(row=3, column=0, padx=10, pady=5)
        self.mobile_var = tk.StringVar()
        tk.Entry(self, textvariable=self.mobile_var).grid(row=3, column=1, padx=10, pady=5)

        tk.Button(self, text="Create", command=self.create_student).grid(row=5, column=0, padx=10, pady=5)
        tk.Button(self, text="Read", command=self.read_students).grid(row=5, column=1, padx=10, pady=5)
        tk.Button(self, text="Update", command=self.update_student).grid(row=5, column=2, padx=10, pady=5)
        tk.Button(self, text="Delete", command=self.delete_student).grid(row=5, column=3, padx=10, pady=5)

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

        self.create_database_and_table()

    def create_database_and_table(self):
        conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD)
        cursor = conn.cursor()

        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE};")
        cursor.execute(f"USE {DATABASE};")

        # Create a table to store student details
        cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            class VARCHAR(50) NOT NULL,
                            batch_year INT NOT NULL,
                            mobile VARCHAR(15) NOT NULL UNIQUE);''')

        conn.commit()
        conn.close()

    def clear_entries(self):
        self.name_var.set("")
        self.class_var.set("")
        self.batch_var.set("")
        self.mobile_var.set("")

    def create_student(self):
        name = self.name_var.get()
        student_class = self.class_var.get()
        batch_year = self.batch_var.get()
        mobile = self.mobile_var.get()

        if not name or not student_class or not batch_year or not mobile:
            messagebox.showwarning("Error", "Please fill all the fields.")
            return

        try:
            conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = conn.cursor()
            query = "INSERT INTO students (name, class, batch_year, mobile) VALUES (%s, %s, %s, %s)"
            values = (name, student_class, batch_year, mobile)
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            self.clear_entries()
            messagebox.showinfo("Success", "Student record created successfully.")
            self.read_students()
        except mysql.connector.IntegrityError as e:
            messagebox.showerror("Error", f"Error while creating the student record: Mobile number already exists.")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error while creating the student record: {e}")

    def read_students(self):
        try:
            conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            conn.close()

            self.tree.delete(*self.tree.get_children())

            for student in students:
                self.tree.insert("", "end", values=student)
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error while fetching student records: {e}")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, 'values')
        if values:
            self.name_var.set(values[1])
            self.class_var.set(values[2])
            self.batch_var.set(values[3])
            self.mobile_var.set(values[4])

    def update_student(self):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, 'values')
        if not values:
            messagebox.showwarning("Warning", "Please select a student to update.")
            return

        name = self.name_var.get()
        student_class = self.class_var.get()
        batch_year = self.batch_var.get()
        mobile = self.mobile_var.get()

        if not name or not student_class or not batch_year or not mobile:
            messagebox.showwarning("Error", "Please fill all the fields.")
            return

        try:
            conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = conn.cursor()
            query = "UPDATE students SET name=%s, class=%s, batch_year=%s, mobile=%s WHERE id=%s"
            values = (name, student_class, batch_year, mobile, values[0])
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            self.clear_entries()
            messagebox.showinfo("Success", "Student record updated successfully.")
            self.read_students()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error while updating the student record: {e}")

    def delete_student(self):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, 'values')
        if not values:
            messagebox.showwarning("Warning", "Please select a student to delete.")
            return

        try:
            conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
            cursor = conn.cursor()
            query = "DELETE FROM students WHERE id=%s"
            cursor.execute(query, (values[0],))
            conn.commit()
            conn.close()
            self.clear_entries()
            messagebox.showinfo("Success", "Student record deleted successfully.")
            self.read_students()
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Error while deleting the student record: {e}")

if __name__ == "__main__":
    app = StudentCRUDApp()
    app.mainloop()
