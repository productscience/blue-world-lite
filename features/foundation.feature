Feature: Foundation

  Scenario: Visit dashboard when not signed in
     When I navigate to /static/foundation/index.html
     Then I see "Welcome to Foundation for Sites" within "h1"

  Scenario: Visit dashboard when not signed in
     When I navigate to /static/foundation/assets/css/app.css
     Then I see "Foundation for Sites by ZURB" within "body"
