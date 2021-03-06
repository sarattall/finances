from pynance.flow import Flow
from pynance.models import Account, Lot
from intervals import IntInterval

class PipeException(Exception):
    pass

class Pipe(object):
    # TODO(Sarat): Finish spec-ing this class

    def __init__(self, name, flow, costbasis_fetcher=None, source_account=None, dest_account=None):
        super(Pipe, self).__init__()
        self._name = name
        assert source_account == None or isinstance(source_account, Account)
        assert dest_account == None or isinstance(dest_account, Account)
        assert costbasis_fetcher == None or hasattr(costbasis_fetcher, '__call__')
        self._source_account = source_account
        self._dest_account = dest_account
        self._flow = flow
        self._costbasis_fetcher = costbasis_fetcher

        self._blackouts = []
        self._last_flushed_t = None
        self._flow_enabled = False
        self._last_stopped_t = None

    @property
    def name(self):
        return self._name

    def start_flow(self, t):
        """
        Only flow after the specified t will actually be transferred from the source account to dest.
        """
        if self._flow_enabled:
            raise PipeException("Flow already started")

        if t < self._last_flushed_t:
            raise PipeException("Time travel not supported yet")

        if not self._last_stopped_t == None:
            self._blackouts.append(IntInterval.closed_open(self._last_stopped_t, t))

        self._last_flushed_t = t
        self._flow_enabled = True

    def stop_flow(self, t):
        """
        Only flow after the specified t will actually be transferred from the source account to dest.
        """
        if not self._flow_enabled:
            raise PipeException("Flow already stopped")

        if t < self._last_flushed_t:
            raise PipeException("Can't stop flow retroactively after flushed")

        self._flow_enabled = False
        self._last_stopped_t = t

    def _is_blacked_out(self, t):
        for blackout_interval in self._blackouts:
            if t in blackout_interval:
                return True

        return False

    def peek(self, t):
        """
        Returns a list of tuples, where each pair is of the format (<t>, <amount>, <costbasis_amount>). Each tuple
        corresponds to a transfer point.
        """
        rng = xrange(self._last_flushed_t, t)
        if not self._flow_enabled:
            rng = xrange(self._last_flushed_t, min(t, self._last_stopped_t))

        pairs = []

        for tt in rng:
            if self._is_blacked_out(tt):
                continue

            amount = self._flow[tt]
            if amount:
                costbasis_amount = self._costbasis_fetcher(tt) if self._costbasis_fetcher else 0
                pairs.append((tt, amount, costbasis_amount))

        return pairs

    def flush(self, t):
        """
        Will flush any of the flow from self._last_flushed_t to the specified t
        """
        for tt, amount, costbasis_amount in self.peek(t):
            self._transfer(amount, tt, costbasis_amount)

        if t > self._last_flushed_t:
            self._last_flushed_t = t

    def _transfer(self, amount, t, costbasis_amount):
        """
        Transfers the specified amount from the source account to the destination account.
        """
        #TODO(Sarat): Add locking.

        if self._source_account:
            self._source_account.remove(amount.security, amount.amount, t, Lot.WITHDRAW_MODE_FIFO)

        if self._dest_account:
            self._dest_account.add(Lot.Spot(amount.security, costbasis_amount, t), amount.amount, t)


class InputPipe(Pipe):

    def __init__(self, name, flow, account, costbasis_fetcher=None):
        super(InputPipe, self).__init__(name, flow, costbasis_fetcher, None, account)


class OutputPipe(Pipe):

    def __init__(self, name, flow, account):
        super(OutputPipe, self).__init__(name, flow, None, account, None)

