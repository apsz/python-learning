#!/usr/bin/python3


import pickle


class AccountError(Exception): pass
class InvalidArgumentType(AccountError): pass
class InvalidFilename(AccountError): pass
class SaveError(AccountError): pass
class LoadError(AccountError): pass


class Transaction:
    """
    >>> t = Transaction(100, "2008-12-09")
    >>> t.amount, t.currency, t.usd_conversion_rate, t.usd
    (100, 'USD', 1, 100)
    >>> t = Transaction(250, "2009-03-12", "EUR", 1.53)
    >>> t.amount, t.currency, t.usd_conversion_rate, t.usd
    (250, 'EUR', 1.53, 382.5)
    """
    def __init__(self, amount, date, currency='USD',
                 usd_conv_rate=1, descr=None):
        self.__amount = amount
        self.__date = date
        self.__currency = currency
        self.__usd_conv_rate = usd_conv_rate
        self.__descr = descr

    @property
    def amount(self):
        return self.__amount

    @property
    def date(self):
        return self.__date

    @property
    def currency(self):
        return self.__currency

    @property
    def usd_conversion_rate(self):
        return self.__usd_conv_rate

    @property
    def description(self):
        return self.__descr

    @property
    def usd(self):
        return self.amount * self.usd_conversion_rate


class Account:
    """
    >>> import os
    >>> import tempfile
    >>> name = os.path.join(tempfile.gettempdir(), "account01")
    >>> account = Account(name, "Damage Inc.")
    >>> os.path.basename(account.account_number), account.account_name,
    ('account01', 'Damage Inc.')
    >>> account.balance, account.all_usd, len(account)
    (0.0, True, 0)
    >>> account.apply(Transaction(100, "2008-11-14"))
    >>> account.apply(Transaction(150, "2008-12-09"))
    >>> account.apply(Transaction(-95, "2009-01-22"))
    >>> account.balance, account.all_usd, len(account)
    (155.0, True, 3)
    >>> account.apply(Transaction(50, "2008-12-09", "EUR", 1.53))
    >>> account.balance, account.all_usd, len(account)
    (231.5, False, 4)
    >>> account.save()
    >>> newaccount = Account(name, "Damage Inc.")
    >>> newaccount.balance, newaccount.all_usd, len(newaccount)
    (0.0, True, 0)
    >>> newaccount.load()
    >>> newaccount.balance, newaccount.all_usd, len(newaccount)
    (231.5, False, 4)
    >>> try:
    ...     os.remove(name + ".acc")
    ... except EnvironmentError:
    ...     pass
    """

    def __init__(self, acc_no, acc_name):
        self.__acc_no = acc_no
        self.account_name = acc_name
        self.__list = []

    @property
    def account_number(self):
        return self.__acc_no

    @property
    def account_name(self):
        return self.__acc_name

    @account_name.setter
    def account_name(self, name):
        assert len(name) >= 4, ('account name must be at '
                                'least 4 characters long')
        self.__acc_name = name

    @property
    def balance(self):
        # if self.all_usd:
        #     return float(sum([transact.amount for transact in self.__list]))
        return float(sum([transact.usd for transact in self.__list]))

    @property
    def all_usd(self):
        return all([transact.currency == 'USD'
                    for transact in self.__list])

    def __len__(self):
        return len(self.__list)

    def apply(self, transaction):
        assert isinstance(transaction,
                          Transaction), 'Invalid argument class: {}'.format(
                          transaction.__class__.__name__)
        self.__list.append(transaction)

    def save(self):
        filename = '{}{}'.format(str(self.account_number), '.acc')

        fh = None
        try:
            fh = open(filename, 'wb')
            data = (self.account_number, self.account_name,
                    self.__list)
            pickle.dump(data, fh, pickle.HIGHEST_PROTOCOL)
        except (IOError, EnvironmentError,
                pickle.PicklingError) as save_err:
            raise SaveError(str(save_err))
        finally:
            if fh:
                fh.close()

    def load(self):
        filename = '{}{}'.format(str(self.account_number), '.acc')

        fh = None
        try:
            fh = open(filename, 'rb')
            (self.__account_number, self.account_name, self.__list) = pickle.load(fh)
        except (IOError, EnvironmentError,
                pickle.PicklingError) as load_err:
            raise LoadError(str(load_err))
        finally:
            if fh:
                fh.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()



