import tkinter as tk
from tkinter import messagebox
from database import connect_db
import hashlib

# ---------------- MAIN WINDOW ----------------

root = tk.Tk()
root.title("Gym Diet Management System")
root.geometry("950x700")
root.configure(bg="#eef3f8")


def clear():
    for widget in root.winfo_children():
        widget.destroy()


def title(text):
    tk.Label(
        root,
        text=text,
        font=("Arial", 23, "bold"),
        bg="#eef3f8",
        fg="#183153"
    ).pack(pady=20)


# ---------------- REGISTRATION ----------------

def register():
    clear()
    title("Member Registration")

    fields = {}

    labels = [
        "Name", "Age", "Weight (kg)", "Height (cm)",
        "Fitness Goal", "Daily Budget", "Username", "Password"
    ]

    for label in labels:
        tk.Label(root, text=label, bg="#eef3f8").pack()

        entry = tk.Entry(
            root,
            show="*" if label == "Password" else ""
        )
        entry.pack(pady=3)
        fields[label] = entry

    def save():
        conn = None
        try:
            values = [fields[x].get().strip() for x in fields]

            if not all(values):
                messagebox.showerror("Error", "Fill all fields")
                return

            password_hash = hashlib.sha256(
                fields["Password"].get().encode()
            ).hexdigest()

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO Members
                (name, age, weight, height, fitness_goal,
                 budget, username, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fields["Name"].get().strip(),
                int(fields["Age"].get()),
                float(fields["Weight (kg)"].get()),
                float(fields["Height (cm)"].get()),
                fields["Fitness Goal"].get().strip(),
                float(fields["Daily Budget"].get()),
                fields["Username"].get().strip(),
                password_hash
            ))

            conn.commit()
            messagebox.showinfo(
                "Success",
                "Registration completed successfully!"
            )
            home()

        except Exception as e:
            messagebox.showerror("Registration Error", str(e))

        finally:
            if conn:
                conn.close()

    tk.Button(
        root, text="Register",
        command=save,
        bg="#218c74", fg="white",
        width=20
    ).pack(pady=12)

    tk.Button(root, text="Back", command=home).pack()


# ---------------- LOGIN ----------------

def login():
    clear()
    title("Member Login")

    tk.Label(root, text="Username", bg="#eef3f8").pack()
    username = tk.Entry(root)
    username.pack(pady=5)

    tk.Label(root, text="Password", bg="#eef3f8").pack()
    password = tk.Entry(root, show="*")
    password.pack(pady=5)

    def check_login():
        conn = None
        try:
            hashed = hashlib.sha256(
                password.get().encode()
            ).hexdigest()

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                SELECT member_id, name
                FROM Members
                WHERE username=? AND password_hash=?
            """, (username.get().strip(), hashed))

            user = cur.fetchone()

            if user:
                dashboard(user[0], user[1])
            else:
                messagebox.showerror(
                    "Login Error",
                    "Invalid username or password"
                )

        except Exception as e:
            messagebox.showerror("Login Error", str(e))

        finally:
            if conn:
                conn.close()

    tk.Button(
        root, text="Login",
        command=check_login,
        bg="#218c74", fg="white",
        width=20
    ).pack(pady=15)

    tk.Button(root, text="Back", command=home).pack()


# ---------------- DASHBOARD ----------------

def dashboard(member_id, name):
    clear()
    title("Welcome, " + name + "!")

    tk.Label(
        root,
        text="GYM DIET MANAGEMENT SYSTEM",
        font=("Arial", 16),
        bg="#eef3f8"
    ).pack(pady=10)

    buttons = [
        ("View Diet Plan",
         lambda: diet_plan(member_id, name)),

        ("Add Food & Track Calories",
         lambda: track_food(member_id, name)),

        ("View Diet History",
         lambda: history(member_id, name)),

        ("Find Food Alternatives",
         lambda: food_alternatives(member_id, name)),

        ("Daily Diet Score",
         lambda: daily_score(member_id, name)),

        ("Logout", home)
    ]

    for button_text, command in buttons:
        tk.Button(
            root,
            text=button_text,
            width=32,
            command=command
        ).pack(pady=8)


# ---------------- DIET PLAN ----------------

def diet_plan(member_id, name):
    clear()
    title("Your Diet Plan")

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT fitness_goal, budget
            FROM Members
            WHERE member_id=?
        """, (member_id,))

        result = cur.fetchone()

        if not result:
            messagebox.showerror("Error", "Member not found")
            return

        goal, budget = result

        tk.Label(
            root,
            text=f"Fitness Goal: {goal}",
            font=("Arial", 14),
            bg="#eef3f8"
        ).pack(pady=8)

        tk.Label(
            root,
            text=f"Daily Budget: Rs. {budget}",
            font=("Arial", 14),
            bg="#eef3f8"
        ).pack(pady=8)

        cur.execute("""
            SELECT food_name, calories, protein, price
            FROM Foods
            WHERE price <= ?
            ORDER BY price ASC
        """, (budget,))

        foods = cur.fetchall()

        if foods:
            for food in foods:
                tk.Label(
                    root,
                    text=f"{food[0]} | {food[1]} kcal | "
                         f"{food[2]}g protein | Rs.{food[3]}",
                    bg="#eef3f8"
                ).pack(pady=4)
        else:
            tk.Label(
                root,
                text="No foods found within your budget.",
                bg="#eef3f8"
            ).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Diet Plan Error", str(e))

    finally:
        if conn:
            conn.close()

    tk.Button(
        root,
        text="Back",
        command=lambda: dashboard(member_id, name)
    ).pack(pady=20)


# ---------------- FOOD TRACKING ----------------

def track_food(member_id, name):
    clear()
    title("Daily Food Tracking")

    tk.Label(root, text="Food ID", bg="#eef3f8").pack()
    food_id = tk.Entry(root)
    food_id.pack(pady=5)

    tk.Label(
        root,
        text="Quantity (servings)",
        bg="#eef3f8"
    ).pack()

    quantity = tk.Entry(root)
    quantity.pack(pady=5)

    def save_food():
        conn = None
        try:
            selected_id = int(food_id.get())
            selected_quantity = float(quantity.get())

            if selected_quantity <= 0:
                messagebox.showerror(
                    "Error",
                    "Quantity must be greater than zero"
                )
                return

            conn = connect_db()
            cur = conn.cursor()

            cur.execute(
                "SELECT food_id FROM Foods WHERE food_id=?",
                (selected_id,)
            )

            if not cur.fetchone():
                messagebox.showerror("Error", "Food ID does not exist")
                return

            cur.execute("""
                INSERT INTO Diet_Logs
                (member_id, food_id, quantity)
                VALUES (?, ?, ?)
            """, (
                member_id,
                selected_id,
                selected_quantity
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                "Food recorded successfully!"
            )

            food_id.delete(0, tk.END)
            quantity.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Tracking Error", str(e))

        finally:
            if conn:
                conn.close()

    tk.Button(
        root,
        text="Save Food",
        command=save_food,
        bg="#218c74",
        fg="white"
    ).pack(pady=15)

    tk.Button(
        root,
        text="Back",
        command=lambda: dashboard(member_id, name)
    ).pack()


# ---------------- DIET HISTORY ----------------

def history(member_id, name):
    clear()
    title("Diet History & Nutrition Summary")

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT F.food_name, F.calories, F.protein,
                   F.price, D.quantity, D.log_date
            FROM Diet_Logs D
            JOIN Foods F ON D.food_id = F.food_id
            WHERE D.member_id = ?
            ORDER BY D.log_date DESC
        """, (member_id,))

        records = cur.fetchall()

        total_calories = 0
        total_protein = 0
        total_cost = 0

        if not records:
            tk.Label(
                root,
                text="No food records found.",
                bg="#eef3f8"
            ).pack(pady=10)

        for record in records:
            food_name = record[0]
            calories = float(record[1])
            protein = float(record[2])
            price = float(record[3])
            quantity = float(record[4])
            log_date = record[5]

            total_calories += calories * quantity
            total_protein += protein * quantity
            total_cost += price * quantity

            tk.Label(
                root,
                text=f"{food_name} | "
                     f"{calories * quantity:.1f} kcal | "
                     f"{protein * quantity:.1f}g protein | "
                     f"Qty: {quantity} | {log_date}",
                bg="#eef3f8"
            ).pack(pady=4)

        tk.Label(
            root,
            text="----- Nutrition Summary -----",
            font=("Arial", 16, "bold"),
            bg="#eef3f8"
        ).pack(pady=15)

        summary = [
            f"Total Calories: {total_calories:.1f} kcal",
            f"Total Protein: {total_protein:.1f} g",
            f"Total Food Cost: Rs. {total_cost:.2f}"
        ]

        for item in summary:
            tk.Label(
                root,
                text=item,
                font=("Arial", 13),
                bg="#eef3f8"
            ).pack(pady=5)

    except Exception as e:
        messagebox.showerror("History Error", str(e))

    finally:
        if conn:
            conn.close()

    tk.Button(
        root,
        text="Back",
        command=lambda: dashboard(member_id, name)
    ).pack(pady=20)


# ---------------- FOOD ALTERNATIVES ----------------

def food_alternatives(member_id, name):
    clear()
    title("Budget-Friendly Food Alternatives")

    tk.Label(
        root,
        text="Enter Food ID to find cheaper alternatives",
        bg="#eef3f8"
    ).pack(pady=10)

    tk.Label(root, text="Food ID:", bg="#eef3f8").pack()
    food_id = tk.Entry(root)
    food_id.pack(pady=5)

    def find_alternatives():
        conn = None
        try:
            selected_id = int(food_id.get())

            conn = connect_db()
            cur = conn.cursor()

            cur.execute("""
                SELECT food_name, calories, protein, price
                FROM Foods
                WHERE food_id=?
            """, (selected_id,))

            selected_food = cur.fetchone()

            if not selected_food:
                messagebox.showerror("Error", "Food ID not found")
                return

            food_name = selected_food[0]
            protein = float(selected_food[2])
            price = float(selected_food[3])

            cur.execute("""
                SELECT food_name, calories, protein, price
                FROM Foods
                WHERE price < ?
                AND protein >= ?
                ORDER BY price ASC
            """, (price, protein * 0.5))

            alternatives = cur.fetchall()

            clear()
            title("Food Alternatives")

            tk.Label(
                root,
                text=f"Selected Food: {food_name}",
                font=("Arial", 14, "bold"),
                bg="#eef3f8"
            ).pack(pady=10)

            tk.Label(
                root,
                text=f"Original Price: Rs. {price}",
                bg="#eef3f8"
            ).pack(pady=5)

            if alternatives:
                for food in alternatives:
                    tk.Label(
                        root,
                        text=f"{food[0]} | {food[1]} kcal | "
                             f"{food[2]}g protein | Rs.{food[3]}",
                        bg="#eef3f8"
                    ).pack(pady=5)
            else:
                tk.Label(
                    root,
                    text="No cheaper alternatives found.",
                    bg="#eef3f8"
                ).pack(pady=10)

            tk.Button(
                root,
                text="Back to Dashboard",
                command=lambda: dashboard(member_id, name)
            ).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Alternatives Error", str(e))

        finally:
            if conn:
                conn.close()

    tk.Button(
        root,
        text="Find Alternatives",
        command=find_alternatives,
        bg="#218c74",
        fg="white"
    ).pack(pady=15)

    tk.Button(
        root,
        text="Back",
        command=lambda: dashboard(member_id, name)
    ).pack()


# ---------------- DAILY DIET SCORE ----------------

def daily_score(member_id, name):
    clear()
    title("Daily Diet Tracking Score")

    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()

        cur.execute("""
            SELECT COUNT(*)
            FROM Diet_Logs
            WHERE member_id = ?
            AND log_date = CAST(GETDATE() AS DATE)
        """, (member_id,))

        food_count = cur.fetchone()[0]

        score = min(food_count * 20, 100)

        tk.Label(
            root,
            text=f"Food entries recorded today: {food_count}",
            font=("Arial", 14),
            bg="#eef3f8"
        ).pack(pady=15)

        tk.Label(
            root,
            text=f"Your Daily Tracking Score: {score}/100",
            font=("Arial", 18, "bold"),
            fg="#218c74",
            bg="#eef3f8"
        ).pack(pady=15)

        if score == 0:
            message = "Start recording your food today!"
        elif score < 100:
            message = "Keep recording your meals!"
        else:
            message = "Excellent tracking consistency!"

        tk.Label(
            root,
            text=message,
            font=("Arial", 13),
            bg="#eef3f8"
        ).pack(pady=10)

    except Exception as e:
        messagebox.showerror("Score Error", str(e))

    finally:
        if conn:
            conn.close()

    tk.Button(
        root,
        text="Back to Dashboard",
        command=lambda: dashboard(member_id, name)
    ).pack(pady=20)


# ---------------- HOME PAGE ----------------

def home():
    clear()
    title("GYM DIET MANAGEMENT SYSTEM")

    tk.Label(
        root,
        text="Your Personal Fitness & Nutrition Assistant",
        font=("Arial", 14),
        bg="#eef3f8"
    ).pack(pady=15)

    tk.Button(
        root,
        text="Member Registration",
        width=30,
        command=register
    ).pack(pady=12)

    tk.Button(
        root,
        text="Member Login",
        width=30,
        command=login
    ).pack(pady=12)

    tk.Button(
        root,
        text="Exit",
        width=30,
        command=root.destroy
    ).pack(pady=12)


# ---------------- START APPLICATION ----------------

home()
root.mainloop()