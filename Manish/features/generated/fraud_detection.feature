@fraud
Feature: Fraud Detection
  As a banking web app
  I want to detect fraudulent transactions
  So that I can prevent financial losses

  @fraud_detection
  Scenario Outline: Detect fraudulent transactions
    Given a transaction to <Destination Account> with amount <Amount>
    When the transaction is analyzed for fraud
    Then the fraud detection result should be "<Fraud Result>"

    Examples:
      | Destination Account | Amount | Fraud Result |
      | ACC1002 | 2000 | Flag |
      | ACC1004 | 50 | Flag |
      | - | 400 | Flag |
      | ACC1002 | 1000 | Flag |
      | ACC1003 | 60000 | Flag |
      | ACC1003 | 2000 | Flag |
