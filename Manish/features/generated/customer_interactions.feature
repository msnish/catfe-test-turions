@customer
Feature: Customer Interactions
  As a banking web app
  I want to monitor customer interactions
  So that I can ensure security and compliance

  @login
  Scenario Outline: Monitor customer login attempts
    Given a customer with <Login Attempts> login attempts
    When the login is processed
    Then the login result should be "<Login Result>"

    Examples:
      | Login Attempts | Login Result |
      | 2 | Success |
      | 4 | Failure |
      | 6 | Failure |
