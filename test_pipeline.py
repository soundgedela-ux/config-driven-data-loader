import csv, json
from pathlib import Path
from src.pipeline import run_pipeline


def test_customer_load_and_rerun(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("config").mkdir(); Path("data/input").mkdir(parents=True)
    Path("config/customers.yaml").write_text(Path(__file__).parents[1].joinpath("config/customers.yaml").read_text())
    with open("data/input/customers.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["customer_id","customer_name","email"]); w.writeheader(); w.writerow({"customer_id":1,"customer_name":"A","email":"a@example.com"})
    first=run_pipeline("config/customers.yaml", "test.db")
    second=run_pipeline("config/customers.yaml", "test.db")
    import sqlite3
    con=sqlite3.connect("test.db")
    assert con.execute("select count(*) from customers").fetchone()[0] == 1
    assert first["loaded"] == second["loaded"] == 1
