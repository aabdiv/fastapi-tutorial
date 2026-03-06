from app.calculations import add, BankAccount, InsufficientFunds
import pytest

@pytest.fixture
def zero_bank_account():
    return BankAccount()


# @pytest.mark.parametrize("deposit, withdrew, expected", [
#     (100, 50, 50),
#     (200, 0, 190),
#     (10, 100, Exception),
# ])
# def test_bank_account(zero_bank_account, deposit, withdrew, expected):
#     zero_bank_account.deposit(deposit)
#     if isinstance(expected, type) and issubclass(expected, Exception):
#         with pytest.raises(expected):
#             zero_bank_account.withdraw(withdrew)
#     else:
#         zero_bank_account.withdraw(withdrew)
#         assert zero_bank_account.balance == expected