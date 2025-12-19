#!/usr/bin/env python3
"""
Compact Expense Tracker GUI (Listbox) — full features, minimal code
Features kept:
- Add expense (date, amount, category dropdown, description)
- List view (Listbox)
- Delete selected
- Category totals
- Monthly summary (YYYY-MM)
- Search by keyword + date range
- Daily & Weekly limit checks
- Export report (.txt)
- Save/load JSON (expenses.json)
No external libraries.
"""
import json, os, uuid
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

DATA_FILE = "expenses.json"
CATS = ["General","Food","Transport","Shopping","Bills","Entertainment","Other"]

# ----- persistence -----
def load_items():
    if not os.path.exists(DATA_FILE): return []
    try:
        with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
    except Exception:
        return []

def save_items(items):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(items,f,ensure_ascii=False,indent=2)

# ----- utilities -----
def fmt_item(e):
    return f"{e['date']} | ₹{float(e['amount']):.2f} | {e['category'][:12]:12} | {e['description'][:40]:40} | {e['id']}"

def totals_by_category(items, month=None):
    t={}
    for e in items:
        if month and not e.get("date","").startswith(month): continue
        t[e.get("category","General")] = t.get(e.get("category","General"),0)+float(e.get("amount",0))
    return t

def month_summary(items, ym):
    sel=[e for e in items if e.get("date","")[:7]==ym]
    return {"month":ym,"total":sum(float(e["amount"]) for e in sel),"count":len(sel),"by_cat":totals_by_category(sel)}

def search_items(items, kw=None, start=None, end=None):
    kw=(kw or "").lower()
    res=[]
    for e in items:
        ok=True
        if kw and kw not in (e.get("description","")+" "+e.get("category","")).lower(): ok=False
        if ok and start and end:
            try:
                d=datetime.strptime(e.get("date","1970-01-01"),"%Y-%m-%d").date()
                if d < start or d > end: ok=False
            except Exception:
                ok=False
        if ok: res.append(e)
    return sorted(res, key=lambda x: x.get("date",""), reverse=True)

# ----- GUI -----
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini Full-Feature Expense Tracker")
        self.geometry("820x520")
        self.items = load_items()
        self._build()
        self._refresh()

    def _build(self):
        top = ttk.Frame(self,padding=8); top.pack(fill="x")
        ttk.Label(top,text="Date (YYYY-MM-DD):").grid(row=0,column=0,sticky="w")
        self.date = tk.StringVar(value=datetime.today().strftime("%Y-%m-%d"))
        ttk.Entry(top,textvariable=self.date,width=12).grid(row=0,column=1,padx=6)

        ttk.Label(top,text="Amount:").grid(row=0,column=2,sticky="w")
        self.amount = tk.StringVar()
        ttk.Entry(top,textvariable=self.amount,width=10).grid(row=0,column=3,padx=6)

        ttk.Label(top,text="Category:").grid(row=0,column=4,sticky="w")
        self.cat = tk.StringVar(value=CATS[0])
        ttk.Combobox(top,textvariable=self.cat,values=CATS,width=18).grid(row=0,column=5,padx=6)

        ttk.Label(top,text="Description:").grid(row=1,column=0,sticky="w",pady=6)
        self.desc = tk.StringVar()
        ttk.Entry(top,textvariable=self.desc,width=68).grid(row=1,column=1,columnspan=5,sticky="w")

        ttk.Button(top,text="Add",command=self.add).grid(row=0,column=6,rowspan=2,padx=8)

        # listbox display
        mid = ttk.Frame(self,padding=(8,0)); mid.pack(fill="both",expand=True)
        self.listbox = tk.Listbox(mid,font=("Consolas",10),height=18)
        self.listbox.pack(side="left",fill="both",expand=True)
        sb = ttk.Scrollbar(mid,orient="vertical",command=self.listbox.yview)
        self.listbox.config(yscrollcommand=sb.set); sb.pack(side="right",fill="y")

        # actions
        btm = ttk.Frame(self,padding=6); btm.pack(fill="x")
        ttk.Button(btm,text="Category Totals",command=self.show_totals).pack(side="left",padx=4)
        ttk.Button(btm,text="Monthly Summary",command=self.show_month).pack(side="left",padx=4)
        ttk.Button(btm,text="Search",command=self.search).pack(side="left",padx=4)
        ttk.Button(btm,text="Check Limits",command=self.check_limits).pack(side="left",padx=4)
        ttk.Button(btm,text="Export",command=self.export_report).pack(side="right",padx=4)
        ttk.Button(btm,text="Delete Selected",command=self.delete).pack(side="right",padx=4)

    def _refresh(self, arr=None):
        self.listbox.delete(0,tk.END)
        for e in (arr or sorted(self.items, key=lambda x:x.get("date",""), reverse=True)):
            self.listbox.insert(tk.END, fmt_item(e))

    # ----- actions -----
    def add(self):
        d = (self.date.get().strip() or datetime.today().strftime("%Y-%m-%d"))
        a = self.amount.get().strip(); cat = self.cat.get().strip() or "General"; desc = self.desc.get().strip()
        try:
            datetime.strptime(d,"%Y-%m-%d"); a_val = float(a)
        except Exception:
            messagebox.showerror("Bad input","Use YYYY-MM-DD and numeric amount."); return
        it = {"id":str(uuid.uuid4())[:8],"date":d,"amount":a_val,"category":cat,"description":desc}
        self.items.append(it); save_items(self.items); self.amount.set(""); self.desc.set(""); self._refresh()

    def delete(self):
        sel = self.listbox.curselection()
        if not sel: messagebox.showinfo("Delete","Select an entry"); return
        line = self.listbox.get(sel[0])
        eid = line.rsplit("|",1)[-1].strip()
        self.items = [i for i in self.items if i["id"]!=eid]; save_items(self.items); self._refresh()

    def show_totals(self):
        t = totals_by_category(self.items)
        if not t: messagebox.showinfo("Totals","No expenses yet."); return
        txt = "\n".join(f"{k:15} : ₹{v:.2f}" for k,v in sorted(t.items(), key=lambda x:-x[1]))
        messagebox.showinfo("Category Totals", txt)

    def show_month(self):
        ym = simpledialog.askstring("Month","Enter YYYY-MM (blank=current):")
        if not ym: ym = datetime.today().strftime("%Y-%m")
        try: datetime.strptime(ym+"-01","%Y-%m-%d")
        except Exception: messagebox.showerror("Bad","Use YYYY-MM"); return
        s = month_summary(self.items, ym)
        if s["count"]==0: messagebox.showinfo("Monthly",f"No expenses for {ym}"); return
        lines=[f"Month {ym}: Total ₹{s['total']:.2f} ({s['count']} items)", "", "By category:"]
        for k,v in sorted(s["by_cat"].items(), key=lambda x:-x[1]): lines.append(f"  {k:15} : ₹{v:.2f}")
        self._show_text("Monthly Summary", "\n".join(lines))

    def search(self):
        kw = simpledialog.askstring("Keyword","Keyword (desc/category) — leave blank to skip:")
        dr = simpledialog.askstring("Date range","start,end as YYYY-MM-DD,YYYY-MM-DD — blank to skip:")
        start=end=None
        if dr:
            try:
                a,b = [x.strip() for x in dr.split(",")]
                start = datetime.strptime(a,"%Y-%m-%d").date()
                end = datetime.strptime(b,"%Y-%m-%d").date()
            except Exception:
                messagebox.showwarning("Range","Ignoring date filter"); start=end=None
        res = search_items(self.items, kw, start, end)
        if not res: messagebox.showinfo("Search","No matches"); return
        self._refresh(res)

    def check_limits(self):
        dl = simpledialog.askfloat("Daily limit","Enter daily limit (Cancel to skip):")
        wl = simpledialog.askfloat("Weekly limit","Enter weekly limit (Cancel to skip):")
        warnings=[]; today=datetime.today().date()
        if dl is not None:
            day_sum = sum(float(e["amount"]) for e in self.items if e.get("date")==today.strftime("%Y-%m-%d"))
            if day_sum>dl: warnings.append(f"Today ₹{day_sum:.2f} > daily ₹{dl:.2f}")
        if wl is not None:
            y,w,_=today.isocalendar(); ws=0
            for e in self.items:
                try:
                    d=datetime.strptime(e["date"],"%Y-%m-%d").date(); yy,ww,_=d.isocalendar()
                    if yy==y and ww==w: ws+=float(e["amount"])
                except: pass
            if ws>wl: warnings.append(f"This week ₹{ws:.2f} > weekly ₹{wl:.2f}")
        if warnings: messagebox.showwarning("Limits", "\n".join(warnings))
        else: messagebox.showinfo("Limits","No limit warnings")

    def export_report(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="report.txt")
        if not path: return
        lines=[f"Expense Report\nGenerated: {datetime.now().isoformat()}\n", "-"*40 + "\n"]
        total = sum(float(e["amount"]) for e in self.items)
        lines.append(f"Total: ₹{total:.2f} (items: {len(self.items)})\n" + "-"*40 + "\n")
        for e in sorted(self.items, key=lambda x:x.get("date","")):
            lines.append(f"{e['date']} | ₹{float(e['amount']):.2f} | {e['category']} | {e['description']}\n")
        with open(path,"w",encoding="utf-8") as f: f.writelines(lines)
        messagebox.showinfo("Exported", f"Report written to {path}")

    def _show_text(self,title,text):
        w=tk.Toplevel(self); w.title(title); w.geometry("700x420")
        t=tk.Text(w,wrap="word"); t.insert("1.0",text); t.config(state="disabled"); t.pack(fill="both",expand=True)

if __name__=="__main__":
    App().mainloop()
