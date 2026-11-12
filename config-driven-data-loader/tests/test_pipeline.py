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


def test_pipeline_creates_missing_output_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("config").mkdir(); Path("data/input").mkdir(parents=True)
    Path("config/customers.yaml").write_text(Path(__file__).parents[1].joinpath("config/customers.yaml").read_text())
    with open("data/input/customers.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["customer_id","customer_name","email"]); w.writeheader(); w.writerow({"customer_id":1,"customer_name":"A","email":"a@example.com"})

    result = run_pipeline("config/customers.yaml", "data/output/warehouse.db")

    assert result["loaded"] == 1
    assert Path("data/output/warehouse.db").exists()


def test_rejects_malformed_records_and_duplicate_keys(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("config").mkdir(); Path("data/input").mkdir(parents=True)
    Path("config/customers.yaml").write_text(Path(__file__).parents[1].joinpath("config/customers.yaml").read_text())
    with open("data/input/customers.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["customer_id","customer_name","email"])
        w.writeheader()
        w.writerow({"customer_id":1,"customer_name":"A","email":"a@example.com"})
        w.writerow({"customer_id":2,"customer_name":"B","email":""})
        w.writerow({"customer_id":3,"customer_name":"C","email":"not-an-email"})
        w.writerow({"customer_id":1,"customer_name":"Dup","email":"dup@example.com"})

    result = run_pipeline("config/customers.yaml", "test.db")

    assert result["loaded"] == 1
    assert result["rejected"] == 3


def test_rejects_empty_batch_and_invalid_foreign_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("config").mkdir(); Path("data/input").mkdir(parents=True)
    Path("config/customers.yaml").write_text(Path(__file__).parents[1].joinpath("config/customers.yaml").read_text())
    Path("config/orders.yaml").write_text(Path(__file__).parents[1].joinpath("config/orders.yaml").read_text())

    with open("data/input/customers.csv","w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["customer_id","customer_name","email"])
        w.writeheader()

    empty_result = run_pipeline("config/customers.yaml", "customers.db")
    assert empty_result["loaded"] == 0
    assert empty_result["rejected"] == 0

    with open("data/input/orders.json","w",encoding="utf-8") as f:
        json.dump([{"order_id":1,"customer_id":999,"amount":-5,"order_date":"2026-01-02T00:00:00+00:00"}], f)

    invalid_result = run_pipeline("config/orders.yaml", "orders.db")
    assert invalid_result["loaded"] == 0
    assert invalid_result["rejected"] == 1
