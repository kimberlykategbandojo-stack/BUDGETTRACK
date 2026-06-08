import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)
app.secret_key = "salary_budget_secret_key"

# Make `now` available to all templates
@app.context_processor
def inject_now():
    return {"now": datetime.now()}

DATA_FILE = os.path.join("data", "expenses.json")

# ──────────────────────────────────────────────
# Default recommended budget percentages
# ──────────────────────────────────────────────
RECOMMENDED = {
    "Bills":          0.20,
    "Groceries":      0.30,
    "Transportation": 0.10,
    "Savings":        0.20,
    "Health":         0.10,
    "Entertainment":  0.05,
    "Other":          0.05,
}

CATEGORIES = list(RECOMMENDED.keys())


# ──────────────────────────────────────────────
# JSON helpers
# ──────────────────────────────────────────────
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ──────────────────────────────────────────────
# Calculation helpers
# ──────────────────────────────────────────────
def calc_summary(data):
    salary = data.get("salary") or 0
    expenses = data.get("expenses", [])

    total_spent = sum(float(e["amount"]) for e in expenses)
    remaining   = salary - total_spent
    pct_used    = round((total_spent / salary * 100), 1) if salary else 0

    # Per-category totals
    category_totals = {c: 0.0 for c in CATEGORIES}
    for e in expenses:
        cat = e.get("category", "Other")
        if cat in category_totals:
            category_totals[cat] += float(e["amount"])

    # Recommended vs actual
    allocation = []
    for cat, pct in RECOMMENDED.items():
        recommended_amt = salary * pct
        actual_amt      = category_totals.get(cat, 0)
        over_budget     = actual_amt > recommended_amt
        allocation.append({
            "category":    cat,
            "recommended": round(recommended_amt, 2),
            "actual":      round(actual_amt, 2),
            "pct":         round(pct * 100),
            "over":        over_budget,
        })

    # Insights
    insights = []
    if expenses:
        top_cat = max(category_totals, key=category_totals.get)
        if category_totals[top_cat] > 0:
            insights.append(f"You spent the most on <strong>{top_cat}</strong> (₱{category_totals[top_cat]:,.2f}).")

        for item in allocation:
            if item["over"] and item["actual"] > 0:
                insights.append(f"<strong>{item['category']}</strong> exceeded the recommended budget by ₱{item['actual'] - item['recommended']:,.2f}.")
            if item["category"] == "Savings" and item["actual"] < item["recommended"] and salary > 0:
                insights.append(f"Savings are below target. You saved ₱{item['actual']:,.2f} of the recommended ₱{item['recommended']:,.2f}.")

    return {
        "salary":          salary,
        "total_spent":     round(total_spent, 2),
        "remaining":       round(remaining, 2),
        "pct_used":        pct_used,
        "category_totals": category_totals,
        "allocation":      allocation,
        "insights":        insights,
    }


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────
@app.route("/", methods=["GET", "POST"])
def index():
    data = load_data()

    if request.method == "POST":
        action = request.form.get("action")

        # ── Save / update salary ──
        if action == "set_salary":
            salary_str = request.form.get("salary", "").strip()
            month      = request.form.get("month", "").strip()
            if not salary_str:
                flash("Please enter a salary amount.", "danger")
            else:
                try:
                    salary = float(salary_str)
                    if salary < 0:
                        raise ValueError
                    data["salary"] = salary
                    data["month"]  = month
                    save_data(data)
                    flash("Salary saved successfully.", "success")
                except ValueError:
                    flash("Please enter a valid positive salary.", "danger")

        # ── Add expense ──
        elif action == "add_expense":
            name     = request.form.get("name", "").strip()
            amount   = request.form.get("amount", "").strip()
            category = request.form.get("category", "").strip()
            date     = request.form.get("date", "").strip()
            note     = request.form.get("note", "").strip()

            errors = []
            if not name:     errors.append("Expense name is required.")
            if not amount:   errors.append("Amount is required.")
            if not category: errors.append("Category is required.")
            if not date:     errors.append("Date is required.")

            if not errors:
                try:
                    amt = float(amount)
                    if amt <= 0:
                        raise ValueError
                except ValueError:
                    errors.append("Amount must be a positive number.")

            if errors:
                for e in errors:
                    flash(e, "danger")
            else:
                # Generate a simple unique ID
                exp_id = str(int(datetime.now().timestamp() * 1000))
                data["expenses"].append({
                    "id":       exp_id,
                    "name":     name,
                    "amount":   float(amount),
                    "category": category,
                    "date":     date,
                    "note":     note,
                })
                save_data(data)
                flash("Expense added.", "success")

        # ── Edit expense ──
        elif action == "edit_expense":
            exp_id   = request.form.get("exp_id")
            name     = request.form.get("name", "").strip()
            amount   = request.form.get("amount", "").strip()
            category = request.form.get("category", "").strip()
            date     = request.form.get("date", "").strip()
            note     = request.form.get("note", "").strip()

            errors = []
            if not name:     errors.append("Expense name is required.")
            if not amount:   errors.append("Amount is required.")
            if not category: errors.append("Category is required.")
            if not date:     errors.append("Date is required.")

            if not errors:
                try:
                    amt = float(amount)
                    if amt <= 0:
                        raise ValueError
                except ValueError:
                    errors.append("Amount must be a positive number.")

            if errors:
                for e in errors:
                    flash(e, "danger")
            else:
                for exp in data["expenses"]:
                    if exp["id"] == exp_id:
                        exp["name"]     = name
                        exp["amount"]   = float(amount)
                        exp["category"] = category
                        exp["date"]     = date
                        exp["note"]     = note
                        break
                save_data(data)
                flash("Expense updated.", "success")

        # ── Delete expense ──
        elif action == "delete_expense":
            exp_id = request.form.get("exp_id")
            data["expenses"] = [e for e in data["expenses"] if e["id"] != exp_id]
            save_data(data)
            flash("Expense deleted.", "success")

        # ── Reset all data ──
        elif action == "reset":
            save_data({"salary": None, "month": "", "expenses": []})
            flash("All data has been reset.", "info")

        return redirect(url_for("index"))

    # GET request
    summary     = calc_summary(data)
    filter_cat  = request.args.get("category", "")
    filter_date = request.args.get("date", "")

    expenses = data.get("expenses", [])
    if filter_cat:
        expenses = [e for e in expenses if e["category"] == filter_cat]
    if filter_date:
        expenses = [e for e in expenses if e["date"] == filter_date]

    # Sort expenses by date descending
    expenses = sorted(expenses, key=lambda x: x["date"], reverse=True)

    return render_template(
        "index.html",
        data=data,
        summary=summary,
        expenses=expenses,
        categories=CATEGORIES,
        filter_cat=filter_cat,
        filter_date=filter_date,
    )


@app.route("/report")
def report():
    data    = load_data()
    summary = calc_summary(data)
    return render_template("report.html", data=data, summary=summary, categories=CATEGORIES)


if __name__ == "__main__":
    app.run(debug=True)
