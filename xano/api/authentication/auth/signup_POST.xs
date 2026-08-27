// Signup and retrieve an authentication token
query "auth/signup" verb=POST {
  api_group = "Authentication"

  input {
    text name?
    email email? filters=trim|lower
    text password?
  }

  stack {
    // Check if a user record with that email exists
    db.get "" {
      field_name = "email"
      field_value = $input.email
    } as $user
  
    // Verify that the email being used to sign up is unique
    precondition ($user == null) {
      error_type = "accessdenied"
      error = "This account is already in use."
    }
  
    // Create a new user record
    db.add "" {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        nome      : $input.name
        email     : $input.email
        senha     : $input.password
        papel_id  : "member"
      }
    } as $user
  
    // Create an authentiction token
    security.create_auth_token {
      table = ""
      extras = {}
      expiration = 86400
      id = $user.id
    } as $authToken
  
    // Create an event log for signup
    function.run "Getting Started Template/create_event_log" {
      input = {
        user_id   : $user.id
        account_id: 0
        action    : "signup"
        metadata  : $user
      }
    } as $event_log
  }

  response = {authToken: $authToken, user_id: $user.id}
  tags = ["xano:quick-start"]
  guid = "rUG4j5xdPgFjFGPIKXqnl6q3lKo"
}