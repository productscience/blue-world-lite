Feature: Billing dates
  Scenario: _setup
    Given I switch to the user browser
      And I navigate to /logout
      And I freeze time at <date>

  Scenario: Billing dates are correct
    Given "#billing-dates" has the following text with all whitespace removed:
      """
      Jul 2016 - 4 weeks
      Invoicing date: Sun 03 Jul 2016

        Wed 06 Jul 2016
        Wed 13 Jul 2016
        Wed 20 Jul 2016
        Wed 27 Jul 2016

      Aug 2016 - 5 weeks
      Invoicing date: Sun 31 Jul 2016

        Wed 03 Aug 2016
        Wed 10 Aug 2016
        Wed 17 Aug 2016
        Wed 24 Aug 2016
        Wed 31 Aug 2016

      Sep 2016 - 4 weeks
      Invoicing date: Sun 04 Sep 2016

        Wed 07 Sep 2016
        Wed 14 Sep 2016
        Wed 21 Sep 2016
        Wed 28 Sep 2016

      Oct 2016 - 4 weeks
      Invoicing date: Sun 02 Oct 2016

        Wed 05 Oct 2016
        Wed 12 Oct 2016
        Wed 19 Oct 2016
        Wed 26 Oct 2016

      Nov 2016 - 5 weeks
      Invoicing date: Sun 30 Oct 2016

        Wed 02 Nov 2016
        Wed 09 Nov 2016
        Wed 16 Nov 2016
        Wed 23 Nov 2016
        Wed 30 Nov 2016

      Dec 2016 - 4 weeks
      Invoicing date: Sun 04 Dec 2016

        Wed 07 Dec 2016
        Wed 14 Dec 2016
        Wed 21 Dec 2016
        Wed 28 Dec 2016

      Jan 2017 - 4 weeks
      Invoicing date: Sun 01 Jan 2017

        Wed 04 Jan 2017
        Wed 11 Jan 2017
        Wed 18 Jan 2017
        Wed 25 Jan 2017

      Feb 2017 - 4 weeks
      Invoicing date: Sun 29 Jan 2017

        Wed 01 Feb 2017
        Wed 08 Feb 2017
        Wed 15 Feb 2017
        Wed 22 Feb 2017

      Mar 2017 - 5 weeks
      Invoicing date: Sun 26 Feb 2017

        Wed 01 Mar 2017
        Wed 08 Mar 2017
        Wed 15 Mar 2017
        Wed 22 Mar 2017
        Wed 29 Mar 2017

      Apr 2017 - 4 weeks
      Invoicing date: Sun 02 Apr 2017

        Wed 05 Apr 2017
        Wed 12 Apr 2017
        Wed 19 Apr 2017
        Wed 26 Apr 2017

      May 2017 - 5 weeks
      Invoicing date: Sun 30 Apr 2017

        Wed 03 May 2017
        Wed 10 May 2017
        Wed 17 May 2017
        Wed 24 May 2017
        Wed 31 May 2017

      Jun 2017 - 4 weeks
      Invoicing date: Sun 04 Jun 2017

        Wed 07 Jun 2017
        Wed 14 Jun 2017
        Wed 21 Jun 2017
        Wed 28 Jun 2017
      """

  Scenario: _teardown
    Given I return to the current time
