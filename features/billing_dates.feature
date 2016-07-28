Feature: Billing dates
  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I freeze time at 2016-07-12 16:00:00

  Scenario: Billing dates are correct
     When I navigate to /billing-dates
     Then "#billing-dates" has the following text with all whitespace removed:
      """
      July 2016 - 4 Wednesday collections
      Invoicing date: Sunday 3 July 2016

              Monday 4 July 2016 - Sunday 10 July 2016
              Wednesday collection: Wednesday 6 July 2016
              Thursday collection: Thursday 7 July 2016
              Deadline for changes: 3pm Sunday 3 July 2016

              Monday 11 July 2016 - Sunday 17 July 2016
              Wednesday collection: Wednesday 13 July 2016
              Thursday collection: Thursday 14 July 2016
              Deadline for changes: 3pm Sunday 10 July 2016

              Monday 18 July 2016 - Sunday 24 July 2016
              Wednesday collection: Wednesday 20 July 2016
              Thursday collection: Thursday 21 July 2016
              Deadline for changes: 3pm Sunday 17 July 2016

              Monday 25 July 2016 - Sunday 31 July 2016
              Wednesday collection: Wednesday 27 July 2016
              Thursday collection: Thursday 28 July 2016
              Deadline for changes: 3pm Sunday 24 July 2016

      August 2016 - 5 Wednesday collections
      Invoicing date: Sunday 31 July 2016

              Monday 1 August 2016 - Sunday 7 August 2016
              Wednesday collection: Wednesday 3 August 2016
              Thursday collection: Thursday 4 August 2016
              Deadline for changes: 3pm Sunday 31 July 2016

              Monday 8 August 2016 - Sunday 14 August 2016
              Wednesday collection: Wednesday 10 August 2016
              Thursday collection: Thursday 11 August 2016
              Deadline for changes: 3pm Sunday 7 August 2016

              Monday 15 August 2016 - Sunday 21 August 2016
              Wednesday collection: Wednesday 17 August 2016
              Thursday collection: Thursday 18 August 2016
              Deadline for changes: 3pm Sunday 14 August 2016

              Monday 22 August 2016 - Sunday 28 August 2016
              Wednesday collection: Wednesday 24 August 2016
              Thursday collection: Thursday 25 August 2016
              Deadline for changes: 3pm Sunday 21 August 2016

              Monday 29 August 2016 - Sunday 4 September 2016
              Wednesday collection: Wednesday 31 August 2016
              Thursday collection: Thursday 1 September 2016
              Deadline for changes: 3pm Sunday 28 August 2016

      September 2016 - 4 Wednesday collections
      Invoicing date: Sunday 4 September 2016

              Monday 5 September 2016 - Sunday 11 September 2016
              Wednesday collection: Wednesday 7 September 2016
              Thursday collection: Thursday 8 September 2016
              Deadline for changes: 3pm Sunday 4 September 2016

              Monday 12 September 2016 - Sunday 18 September 2016
              Wednesday collection: Wednesday 14 September 2016
              Thursday collection: Thursday 15 September 2016
              Deadline for changes: 3pm Sunday 11 September 2016

              Monday 19 September 2016 - Sunday 25 September 2016
              Wednesday collection: Wednesday 21 September 2016
              Thursday collection: Thursday 22 September 2016
              Deadline for changes: 3pm Sunday 18 September 2016

              Monday 26 September 2016 - Sunday 2 October 2016
              Wednesday collection: Wednesday 28 September 2016
              Thursday collection: Thursday 29 September 2016
              Deadline for changes: 3pm Sunday 25 September 2016

      October 2016 - 4 Wednesday collections
      Invoicing date: Sunday 2 October 2016

              Monday 3 October 2016 - Sunday 9 October 2016
              Wednesday collection: Wednesday 5 October 2016
              Thursday collection: Thursday 6 October 2016
              Deadline for changes: 3pm Sunday 2 October 2016

              Monday 10 October 2016 - Sunday 16 October 2016
              Wednesday collection: Wednesday 12 October 2016
              Thursday collection: Thursday 13 October 2016
              Deadline for changes: 3pm Sunday 9 October 2016

              Monday 17 October 2016 - Sunday 23 October 2016
              Wednesday collection: Wednesday 19 October 2016
              Thursday collection: Thursday 20 October 2016
              Deadline for changes: 3pm Sunday 16 October 2016

              Monday 24 October 2016 - Sunday 30 October 2016
              Wednesday collection: Wednesday 26 October 2016
              Thursday collection: Thursday 27 October 2016
              Deadline for changes: 3pm Sunday 23 October 2016

      November 2016 - 5 Wednesday collections
      Invoicing date: Sunday 30 October 2016

              Monday 31 October 2016 - Sunday 6 November 2016
              Wednesday collection: Wednesday 2 November 2016
              Thursday collection: Thursday 3 November 2016
              Deadline for changes: 3pm Sunday 30 October 2016

              Monday 7 November 2016 - Sunday 13 November 2016
              Wednesday collection: Wednesday 9 November 2016
              Thursday collection: Thursday 10 November 2016
              Deadline for changes: 3pm Sunday 6 November 2016

              Monday 14 November 2016 - Sunday 20 November 2016
              Wednesday collection: Wednesday 16 November 2016
              Thursday collection: Thursday 17 November 2016
              Deadline for changes: 3pm Sunday 13 November 2016

              Monday 21 November 2016 - Sunday 27 November 2016
              Wednesday collection: Wednesday 23 November 2016
              Thursday collection: Thursday 24 November 2016
              Deadline for changes: 3pm Sunday 20 November 2016

              Monday 28 November 2016 - Sunday 4 December 2016
              Wednesday collection: Wednesday 30 November 2016
              Thursday collection: Thursday 1 December 2016
              Deadline for changes: 3pm Sunday 27 November 2016

      December 2016 - 4 Wednesday collections
      Invoicing date: Sunday 4 December 2016

              Monday 5 December 2016 - Sunday 11 December 2016
              Wednesday collection: Wednesday 7 December 2016
              Thursday collection: Thursday 8 December 2016
              Deadline for changes: 3pm Sunday 4 December 2016

              Monday 12 December 2016 - Sunday 18 December 2016
              Wednesday collection: Wednesday 14 December 2016
              Thursday collection: Thursday 15 December 2016
              Deadline for changes: 3pm Sunday 11 December 2016

              Monday 19 December 2016 - Sunday 25 December 2016
              Wednesday collection: Wednesday 21 December 2016
              Thursday collection: Thursday 22 December 2016
              Deadline for changes: 3pm Sunday 18 December 2016

              Monday 26 December 2016 - Sunday 1 January 2017
              Wednesday collection: Wednesday 28 December 2016
              Thursday collection: Thursday 29 December 2016
              Deadline for changes: 3pm Sunday 25 December 2016

      January 2017 - 4 Wednesday collections
      Invoicing date: Sunday 1 January 2017

              Monday 2 January 2017 - Sunday 8 January 2017
              Wednesday collection: Wednesday 4 January 2017
              Thursday collection: Thursday 5 January 2017
              Deadline for changes: 3pm Sunday 1 January 2017

              Monday 9 January 2017 - Sunday 15 January 2017
              Wednesday collection: Wednesday 11 January 2017
              Thursday collection: Thursday 12 January 2017
              Deadline for changes: 3pm Sunday 8 January 2017

              Monday 16 January 2017 - Sunday 22 January 2017
              Wednesday collection: Wednesday 18 January 2017
              Thursday collection: Thursday 19 January 2017
              Deadline for changes: 3pm Sunday 15 January 2017

              Monday 23 January 2017 - Sunday 29 January 2017
              Wednesday collection: Wednesday 25 January 2017
              Thursday collection: Thursday 26 January 2017
              Deadline for changes: 3pm Sunday 22 January 2017

      February 2017 - 4 Wednesday collections
      Invoicing date: Sunday 29 January 2017

              Monday 30 January 2017 - Sunday 5 February 2017
              Wednesday collection: Wednesday 1 February 2017
              Thursday collection: Thursday 2 February 2017
              Deadline for changes: 3pm Sunday 29 January 2017

              Monday 6 February 2017 - Sunday 12 February 2017
              Wednesday collection: Wednesday 8 February 2017
              Thursday collection: Thursday 9 February 2017
              Deadline for changes: 3pm Sunday 5 February 2017

              Monday 13 February 2017 - Sunday 19 February 2017
              Wednesday collection: Wednesday 15 February 2017
              Thursday collection: Thursday 16 February 2017
              Deadline for changes: 3pm Sunday 12 February 2017

              Monday 20 February 2017 - Sunday 26 February 2017
              Wednesday collection: Wednesday 22 February 2017
              Thursday collection: Thursday 23 February 2017
              Deadline for changes: 3pm Sunday 19 February 2017

      March 2017 - 5 Wednesday collections
      Invoicing date: Sunday 26 February 2017

              Monday 27 February 2017 - Sunday 5 March 2017
              Wednesday collection: Wednesday 1 March 2017
              Thursday collection: Thursday 2 March 2017
              Deadline for changes: 3pm Sunday 26 February 2017

              Monday 6 March 2017 - Sunday 12 March 2017
              Wednesday collection: Wednesday 8 March 2017
              Thursday collection: Thursday 9 March 2017
              Deadline for changes: 3pm Sunday 5 March 2017

              Monday 13 March 2017 - Sunday 19 March 2017
              Wednesday collection: Wednesday 15 March 2017
              Thursday collection: Thursday 16 March 2017
              Deadline for changes: 3pm Sunday 12 March 2017

              Monday 20 March 2017 - Sunday 26 March 2017
              Wednesday collection: Wednesday 22 March 2017
              Thursday collection: Thursday 23 March 2017
              Deadline for changes: 3pm Sunday 19 March 2017

              Monday 27 March 2017 - Sunday 2 April 2017
              Wednesday collection: Wednesday 29 March 2017
              Thursday collection: Thursday 30 March 2017
              Deadline for changes: 3pm Sunday 26 March 2017

      April 2017 - 4 Wednesday collections
      Invoicing date: Sunday 2 April 2017

              Monday 3 April 2017 - Sunday 9 April 2017
              Wednesday collection: Wednesday 5 April 2017
              Thursday collection: Thursday 6 April 2017
              Deadline for changes: 3pm Sunday 2 April 2017

              Monday 10 April 2017 - Sunday 16 April 2017
              Wednesday collection: Wednesday 12 April 2017
              Thursday collection: Thursday 13 April 2017
              Deadline for changes: 3pm Sunday 9 April 2017

              Monday 17 April 2017 - Sunday 23 April 2017
              Wednesday collection: Wednesday 19 April 2017
              Thursday collection: Thursday 20 April 2017
              Deadline for changes: 3pm Sunday 16 April 2017

              Monday 24 April 2017 - Sunday 30 April 2017
              Wednesday collection: Wednesday 26 April 2017
              Thursday collection: Thursday 27 April 2017
              Deadline for changes: 3pm Sunday 23 April 2017

      May 2017 - 5 Wednesday collections
      Invoicing date: Sunday 30 April 2017

              Monday 1 May 2017 - Sunday 7 May 2017
              Wednesday collection: Wednesday 3 May 2017
              Thursday collection: Thursday 4 May 2017
              Deadline for changes: 3pm Sunday 30 April 2017

              Monday 8 May 2017 - Sunday 14 May 2017
              Wednesday collection: Wednesday 10 May 2017
              Thursday collection: Thursday 11 May 2017
              Deadline for changes: 3pm Sunday 7 May 2017

              Monday 15 May 2017 - Sunday 21 May 2017
              Wednesday collection: Wednesday 17 May 2017
              Thursday collection: Thursday 18 May 2017
              Deadline for changes: 3pm Sunday 14 May 2017

              Monday 22 May 2017 - Sunday 28 May 2017
              Wednesday collection: Wednesday 24 May 2017
              Thursday collection: Thursday 25 May 2017
              Deadline for changes: 3pm Sunday 21 May 2017

              Monday 29 May 2017 - Sunday 4 June 2017
              Wednesday collection: Wednesday 31 May 2017
              Thursday collection: Thursday 1 June 2017
              Deadline for changes: 3pm Sunday 28 May 2017

      June 2017 - 4 Wednesday collections
      Invoicing date: Sunday 4 June 2017

              Monday 5 June 2017 - Sunday 11 June 2017
              Wednesday collection: Wednesday 7 June 2017
              Thursday collection: Thursday 8 June 2017
              Deadline for changes: 3pm Sunday 4 June 2017

              Monday 12 June 2017 - Sunday 18 June 2017
              Wednesday collection: Wednesday 14 June 2017
              Thursday collection: Thursday 15 June 2017
              Deadline for changes: 3pm Sunday 11 June 2017

              Monday 19 June 2017 - Sunday 25 June 2017
              Wednesday collection: Wednesday 21 June 2017
              Thursday collection: Thursday 22 June 2017
              Deadline for changes: 3pm Sunday 18 June 2017

              Monday 26 June 2017 - Sunday 2 July 2017
              Wednesday collection: Wednesday 28 June 2017
              Thursday collection: Thursday 29 June 2017
              Deadline for changes: 3pm Sunday 25 June 2017
      """

  Scenario: _teardown
    Given I return to the current time
