"""SQLite synthetic hierarchical budget reservation ledger.

Only a local test model. Not a live billing system or production budget manager.
"""
from __future__ import annotations
import sqlite3
from pathlib import Path


class BudgetExceeded(Exception):
    pass


class BudgetConflict(Exception):
    pass


class BudgetLedger:
    def __init__(self, db_path: str | Path):
        self.db_path = str(db_path)
        with self._connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS accounts(
                account_id TEXT PRIMARY KEY, parent_id TEXT, limit_units INTEGER NOT NULL,
                spent INTEGER NOT NULL DEFAULT 0, reserved INTEGER NOT NULL DEFAULT 0,
                active INTEGER NOT NULL DEFAULT 1)""")
            db.execute("""CREATE TABLE IF NOT EXISTS reservations(
                account_id TEXT NOT NULL, idem_key TEXT NOT NULL, amount INTEGER NOT NULL,
                status TEXT NOT NULL, actual INTEGER, PRIMARY KEY(account_id, idem_key))""")

    def _connect(self):
        db=sqlite3.connect(self.db_path,timeout=15,isolation_level=None)
        db.execute("PRAGMA journal_mode=WAL")
        db.execute("PRAGMA synchronous=FULL")
        return db

    def create_account(self, account_id, parent_id, limit_units):
        if type(limit_units) is not int or limit_units <= 0:
            raise ValueError("limit must be a positive integer")
        with self._connect() as db:
            db.execute("INSERT INTO accounts(account_id,parent_id,limit_units) VALUES(?,?,?)",
                       (account_id,parent_id,limit_units))

    @staticmethod
    def _chain(db, account_id):
        chain=[]; seen=set(); current=account_id
        while current:
            if current in seen:
                raise BudgetConflict("cyclic account hierarchy")
            seen.add(current)
            row=db.execute("SELECT account_id,parent_id,limit_units,spent,reserved,active FROM accounts WHERE account_id=?",
                           (current,)).fetchone()
            if row is None:
                raise BudgetConflict("missing account in hierarchy")
            chain.append(row); current=row[1]
        return chain

    def reserve(self, account_id, key, amount):
        if amount <= 0:
            raise ValueError("reservation amount must be positive")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            existing=db.execute("SELECT amount,status FROM reservations WHERE account_id=? AND idem_key=?",
                                (account_id,key)).fetchone()
            if existing:
                if existing[0] != amount:
                    db.rollback(); raise BudgetConflict("idempotency key reused with different amount")
                db.commit()
                return existing[1]
            chain=self._chain(db,account_id)
            if any(not row[5] for row in chain):
                db.rollback(); raise BudgetConflict("account or ancestor revoked")
            if any(row[3]+row[4]+amount > row[2] for row in chain):
                db.rollback(); raise BudgetExceeded("hierarchical budget capacity exceeded")
            for row in chain:
                db.execute("UPDATE accounts SET reserved=reserved+? WHERE account_id=?",
                           (amount,row[0]))
            db.execute("INSERT INTO reservations(account_id,idem_key,amount,status) VALUES(?,?,?,'reserved')",
                       (account_id,key,amount))
            db.commit()
            return "reserved"

    def settle(self, account_id, key, actual):
        if actual < 0:
            raise ValueError("actual usage cannot be negative")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            reservation=db.execute("SELECT amount,status,actual FROM reservations WHERE account_id=? AND idem_key=?",
                                   (account_id,key)).fetchone()
            if reservation is None:
                db.rollback(); raise BudgetConflict("unknown reservation")
            amount,status,previous=reservation
            if status=="settled":
                if previous != actual:
                    db.rollback(); raise BudgetConflict("settlement replay changed actual amount")
                db.commit(); return "settled"
            if status!="reserved":
                db.rollback(); raise BudgetConflict("reservation not active")
            chain=self._chain(db,account_id)
            for row in chain:
                # Check if a late actual amount exceeds reserved headroom.
                if row[3]+(row[4]-amount)+actual > row[2]:
                    db.rollback(); raise BudgetExceeded("actual usage exceeds available budget")
            for row in chain:
                db.execute("UPDATE accounts SET reserved=reserved-?, spent=spent+? WHERE account_id=?",
                           (amount,actual,row[0]))
            db.execute("UPDATE reservations SET status='settled',actual=? WHERE account_id=? AND idem_key=?",
                       (actual,account_id,key))
            db.commit(); return "settled"

    def release(self, account_id, key):
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            r=db.execute("SELECT amount,status FROM reservations WHERE account_id=? AND idem_key=?",
                         (account_id,key)).fetchone()
            if r is None:
                db.rollback(); raise BudgetConflict("unknown reservation")
            amount,status=r
            if status=="released":
                db.commit(); return "released"
            if status!="reserved":
                db.rollback(); raise BudgetConflict("only active reservation can be released")
            chain=self._chain(db,account_id)
            for row in chain:
                db.execute("UPDATE accounts SET reserved=reserved-? WHERE account_id=?",
                           (amount,row[0]))
            db.execute("UPDATE reservations SET status='released' WHERE account_id=? AND idem_key=?",
                       (account_id,key))
            db.commit(); return "released"

    def revoke(self, account_id):
        with self._connect() as db:
            db.execute("UPDATE accounts SET active=0 WHERE account_id=?",(account_id,))

    def account(self, account_id):
        with self._connect() as db:
            row=db.execute("SELECT limit_units,spent,reserved,active FROM accounts WHERE account_id=?",
                           (account_id,)).fetchone()
            return {"limit":row[0],"spent":row[1],"reserved":row[2],"active":bool(row[3])}
