# BudgetTrack — Salary Budgeting App

A personal finance web app built with **Python + Flask + Bootstrap 5**.  
No database required — data is stored in a local JSON file.

---

## Features

- Set your monthly salary (saved until you update or reset it)
- Add, edit, and delete expenses with category + date + note
- Automatic calculations: total spent, remaining balance, % used
- Filter expenses by category or date
- Recommended budget allocation (50/30/20-style) vs actual
- Reports page with Chart.js bar chart and spending insights
- Print-friendly report
- Full data reset

---

## Project Structure

```
salary-budgeting-app/
├── app.py                          # Flask app + routes + calculations
├── requirements.txt                # Python dependencies
├── README.md
├── data/
│   └── expenses.json               # Persistent storage (JSON file)
├── templates/
│   ├── base.html                   # Shared layout, navbar, flash messages
│   ├── index.html                  # Dashboard (salary form + expense form + table)
│   ├── report.html                 # Reports page with chart and insights
│   └── partials/
│       ├── summary_cards.html      # 4 summary KPI cards
│       ├── expense_table.html      # Expense table with edit/delete
│       └── allocation_table.html   # Recommended vs actual allocation table
└── static/
    ├── css/style.css               # Minimal custom styles
    └── js/app.js                   # Edit modal population + date defaults
```

---

## How to Run

### 1. Clone or download the project

```bash
cd salary-budgeting-app
```

### 2. (Optional but recommended) Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

### 5. Open in browser

```
http://127.0.0.1:5000
```

---

## How It Works

### Data persistence
All data (salary + expenses) is stored in `data/expenses.json`.  
This file is read on every page load and written on every form submission.  
No database is needed — the JSON file acts as a simple flat-file store.

### Calculations
Done in Python inside `calc_summary()` in `app.py`:
- **Total spent** = sum of all expense amounts
- **Remaining** = salary − total spent
- **% used** = (total spent / salary) × 100
- **Per-category totals** = group and sum expenses by category
- **Recommended vs actual** = compare actual category spending to salary × recommended %

### Data flow
1. User fills form → POST to Flask route
2. Flask validates input → reads JSON → modifies data → writes JSON → redirects
3. On GET, Flask reads JSON → calculates summary → passes to Jinja template → renders page

---

## Future Improvements

- Multi-month support (separate budgets per month)
- Export to CSV or PDF
- Recurring expenses
- Income sources beyond salary
- Dark mode toggle
- Password protection or multi-user support
