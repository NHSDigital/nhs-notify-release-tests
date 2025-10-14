import helpers.bash

def test_mesh():
    helpers.bash.bash_command("scripts/get_mesh_cli.sh")
    poll_mailbox = helpers.bash.bash_command("mesh_retrieve 'NHS Notify UAT' -p")
    assert "No messages available." in poll_mailbox
