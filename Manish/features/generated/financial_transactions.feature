@financial
Feature: Financial Transactions
  As a banking web app
  I want to validate financial transactions
  So that they comply with system rules

  @transaction
  Scenario Outline: Validate a financial transaction
    Given a transaction of type "<Transaction Type>" with amount <Amount> in <Source Currency> to <Destination Currency>
    When the transaction is processed
    Then the result should be "<Expected Result>"

    Examples:
      | Transaction Type  | Amount | Source Currency | Destination Currency | Expected Result |
      | Wire Transfer | 2000 | USD | EUR | Success |
      | ACH | 50 | USD | USD | Success |
      | ATM Withdrawal | 400 | JPY | JPY | Success |
      | Cross-Border | 1000 | USD | EUR | Failure |
      | Wire Transfer | 60000 | USD | JPY | Failure |
      | Wire Transfer | 2000 | USD | JPY | Hold |
