import tempfile, threading, unittest
from pathlib import Path
from budget_model import BudgetLedger, BudgetExceeded, BudgetConflict


class BudgetLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.db=Path(self.tmp.name)/"ledger.sqlite"
        self.ledger=BudgetLedger(self.db)
        self.ledger.create_account("root",None,100)
        self.ledger.create_account("childA","root",100)
        self.ledger.create_account("childB","root",100)

    def tearDown(self): self.tmp.cleanup()

    def test_concurrent_sibling_reserves_cannot_overcommit_parent(self):
        barrier=threading.Barrier(2); results=[]
        def reserve(child,key):
            barrier.wait(timeout=5)
            try: results.append((child,self.ledger.reserve(child,key,70)))
            except BudgetExceeded: results.append((child,"denied"))
        ts=[threading.Thread(target=reserve,args=("childA","a")),
            threading.Thread(target=reserve,args=("childB","b"))]
        for t in ts:t.start()
        for t in ts:t.join(timeout=10)
        self.assertFalse(any(t.is_alive() for t in ts))
        self.assertEqual(sum(result=="reserved" for _,result in results),1)
        self.assertEqual(self.ledger.account("root")["reserved"],70)

    def test_reservation_idempotency_same_key_same_amount(self):
        self.assertEqual(self.ledger.reserve("childA","k",25),"reserved")
        self.assertEqual(self.ledger.reserve("childA","k",25),"reserved")
        self.assertEqual(self.ledger.account("root")["reserved"],25)
        with self.assertRaises(BudgetConflict): self.ledger.reserve("childA","k",26)

    def test_nested_child_cap_enforced(self):
        self.ledger.create_account("grandchild","childA",30)
        with self.assertRaises(BudgetExceeded): self.ledger.reserve("grandchild","k",31)

    def test_settlement_reconciles_reserved_to_actual(self):
        self.ledger.reserve("childA","k",40)
        self.ledger.settle("childA","k",28)
        self.assertEqual(self.ledger.account("root")["reserved"],0)
        self.assertEqual(self.ledger.account("root")["spent"],28)
        self.assertEqual(self.ledger.settle("childA","k",28),"settled")
        with self.assertRaises(BudgetConflict): self.ledger.settle("childA","k",29)

    def test_release_returns_parent_capacity(self):
        self.ledger.reserve("childA","k",80)
        self.ledger.release("childA","k")
        self.assertEqual(self.ledger.account("root")["reserved"],0)
        self.assertEqual(self.ledger.reserve("childB","next",80),"reserved")

    def test_revoked_ancestor_blocks_child_reserve(self):
        self.ledger.create_account("grandchild","childA",30)
        self.ledger.revoke("childA")
        with self.assertRaises(BudgetConflict): self.ledger.reserve("grandchild","k",5)

    def test_actual_charge_cannot_exceed_parent_limit(self):
        self.ledger.reserve("childA","k",60)
        self.ledger.reserve("childB","k",30)
        with self.assertRaises(BudgetExceeded): self.ledger.settle("childA","k",80)
        self.assertEqual(self.ledger.account("root")["reserved"],90)


if __name__=="__main__": unittest.main()
