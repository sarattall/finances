from pynance import Pipe, InputPipe, OutputPipe, PeriodicFlow
from pynance.models import Amount, USD, INR, Lot, BankAccount
from nose.tools import assert_equals, assert_not_equals

class TestPipes:

    def setup(self):
        pass

    def teardown(self):
        pass

    def _assert_amount(self, banks, amounts, t):
        for bank, amount in zip(banks, amounts):
            assert_equals(bank.balance(t), amount)

    def test_costbasis_fetcher(self):
        t = 0
        amount = Amount(10, INR)
        flow = PeriodicFlow(name="testFlow", period=10, stime=5, etime=45, amount=amount)
        account = BankAccount('Bank', 100, 0, t)
        pipe = InputPipe(name="testPipe", flow=flow, account=account, costbasis_fetcher=lambda tt: Amount(tt*2, USD))
        pipe.start_flow(t)

        expected_peek = [
                (5, Amount(10, INR), Amount(5*2, USD)),
                (15, Amount(10, INR), Amount(15*2, USD)),
                (25, Amount(10, INR), Amount(25*2, USD)),
                (35, Amount(10, INR), Amount(35*2, USD)),
            ]
        assert_equals(pipe.peek(100), expected_peek)


    def test_output_pipe(self):
        t = 0
        amount = Amount(10, USD)
        flow = PeriodicFlow(name="testFlow", period=10, stime=5, etime=45, amount=amount)
        account = BankAccount('Bank', 100, 20, t-1)
        pipe = OutputPipe(name="testPipe", flow=flow, account=account)
        assert_equals(account.balance(t), 20)

        pipe.start_flow(t)

        # Test that nothing gets tranfered for for T + 1 --> t + 5
        for i in range(1, 6):
            pipe.flush(t+i)
            assert_equals(account.balance(t+i), 20)
            assert_equals(account.balance(t+i+1), 20)

        # Flush until T+6, and verify that a transfer happens!
        pipe.flush(t+6)
        assert_equals(account.balance(t+6), 10)
        assert_equals(account.balance(t+7), 10)

        # Flush until T+16, and verify that a transfer happens!
        pipe.flush(t+16)
        assert_equals(account.balance(t+16), 0)
        assert_equals(account.balance(t+17), 0)

    def test_input_pipe(self):
        t = 0
        amount = Amount(10, USD)
        flow = PeriodicFlow(name="testFlow", period=10, stime=5, etime=45, amount=amount)
        account = BankAccount('Bank', 100, 0, t)
        pipe = InputPipe(name="testPipe", flow=flow, account=account)
        assert_equals(account.balance(t), 0)

        pipe.start_flow(t)

        # Test that nothing gets tranfered for for T + 1 --> t + 5
        for i in range(1, 6):
            pipe.flush(t+i)
            assert_equals(account.balance(t+i), 0)
            assert_equals(account.balance(t+i+1), 0)

        # Flush until T+6, and verify that a transfer happens!
        pipe.flush(t+6)
        assert_equals(account.balance(t+6), 10)
        assert_equals(account.balance(t+7), 10)

        # Flush until T+16, and verify that a transfer happens!
        pipe.flush(t+16)
        assert_equals(account.balance(t+16), 20)
        assert_equals(account.balance(t+17), 20)

    def test_basic_functionality(self):
        t = 0
        amount = Amount(10, USD)
        flow = PeriodicFlow(name="testFlow", period=10, stime=5, etime=45, amount=amount)
        bank_a = BankAccount('Bank A', 100, 30, t)
        bank_b = BankAccount('Bank B', 100, 0, t)

        pipe = Pipe(name="testPipe", flow=flow, source_account=bank_a, dest_account=bank_b)

        pipe.start_flow(t)

        # Test that nothing gets tranfered for for T + 1 --> t + 5
        for i in range(1, 6):
            pipe.flush(t+i)
            self._assert_amount((bank_a, bank_b), (30, 0), t+i)
            self._assert_amount((bank_a, bank_b), (30, 0), t+i+1)

        # Flush until T+6, and verify that a transfer happens!
        pipe.flush(t+6)
        self._assert_amount((bank_a, bank_b), (20, 10), t+6)
        self._assert_amount((bank_a, bank_b), (20, 10), t+7)

        # Flushing again shouldn't do anything
        pipe.flush(t+6)
        pipe.flush(t+6)
        pipe.flush(t+5)
        self._assert_amount((bank_a, bank_b), (20, 10), t+7)
        self._assert_amount((bank_a, bank_b), (20, 10), t+8)

        # Test that nothing gets tranfered for for T + 7 --> t + 15
        for i in range(7, 16):
            pipe.flush(t+i)
            self._assert_amount((bank_a, bank_b), (20, 10), t+i)
            self._assert_amount((bank_a, bank_b), (20, 10), t+i+1)

        # Flush until T+16, and verify that a transfer happens!
        pipe.flush(t+16)
        self._assert_amount((bank_a, bank_b), (20, 10), t+15)
        self._assert_amount((bank_a, bank_b), (10, 20), t+16)
        self._assert_amount((bank_a, bank_b), (10, 20), t+17)

        # Create a gap from T + 16 --> T + 34, so any transfers in this range would be discarded!
        pipe.stop_flow(t+17) 
        pipe.start_flow(t+35)

        # Test that nothing gets tranfered for for T + 17 --> t + 34
        for i in range(17, 35):
            pipe.flush(t+i)
            self._assert_amount((bank_a, bank_b), (10, 20), t+i)
            self._assert_amount((bank_a, bank_b), (10, 20), t+i+1)

        # Flush until T+36, and verify that a transfer happens!
        pipe.flush(t+36)
        self._assert_amount((bank_a, bank_b), (10, 20), t+35)
        self._assert_amount((bank_a, bank_b), (0, 30), t+36)
        self._assert_amount((bank_a, bank_b), (0, 30), t+37)

