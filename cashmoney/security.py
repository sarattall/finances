
class Security(object):

    def __init__(self, name):
        super(Security, self).__init__()
        self._name = name

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other):
        return self._name == other._name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Security(%s)" %(self._name)


USD = Security("USD")

class Amount(object):

    def __init__(self, security, amount):
        super(Amount, self).__init__()
        self._security = security
        self._amount = amount

    def __eq__(self, other):
        return self._security == other._security and self._amount == other._amount

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._security, self._amount))

    def __add__(self, other_amount):
        if self._security != other_amount._security:
            raise ValueError("{} can't be added to {}".format(other_amount, self))

        return Amount(self._security, self._amount + other_amount._amount)


