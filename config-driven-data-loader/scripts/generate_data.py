import argparse, csv, json, random
from pathlib import Path
from datetime import date, timedelta

p = argparse.ArgumentParser()
p.add_argument("--customers", type=int, default=100)
p.add_argument("--orders", type=int, default=500)
p.add_argument("--seed", type=int, default=42)
a = p.parse_args(); random.seed(a.seed)
base = Path("data/input"); base.mkdir(parents=True, exist_ok=True)
customers = [{"customer_id": i, "customer_name": f"Customer {i}", "email": f"customer{i}@example.com"} for i in range(1, a.customers+1)]
with (base/"customers.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=["customer_id","customer_name","email"]); w.writeheader(); w.writerows(customers)
orders=[]
for i in range(1, a.orders+1):
    orders.append({"order_id":i,"customer_id":random.randint(1,max(1,a.customers)),"amount":round(random.uniform(1,500),2),"order_date":(date(2026,1,1)+timedelta(days=random.randrange(300))).isoformat()+"T00:00:00+00:00"})
(base/"orders.json").write_text(json.dumps(orders, indent=2), encoding="utf-8")
print(f"Generated {len(customers)} customers and {len(orders)} orders")
