"""
Example script demonstrating how to use the Gmail MCP tools directly in Python.
Make sure you have run '.venv/bin/python auth.py' once before running this.
"""

from tools import search_emails, read_email, send_email, trash_email, list_labels


def main():
    print("=== 1. Listing Available Gmail Labels ===")
    labels = list_labels()
    print(f"Found {len(labels)} labels:")
    for l in labels[:5]:
        print(f" - [{l['type']}] {l['name']} (ID: {l['id']})")

    print("\n=== 2. Searching Recent Emails (is:unread) ===")
    results = search_emails(query="is:unread", max_results=3)
    if not results:
        print("No unread emails found, searching latest 3 inbox messages instead...")
        results = search_emails(query="in:inbox", max_results=3)

    for msg in results:
        print(f"\nMessage ID: {msg['id']}")
        print(f"Subject:    {msg['subject']}")
        print(f"From:       {msg['from']}")
        print(f"Date:       {msg['date']}")
        print(f"Snippet:    {msg['snippet']}")

    # If messages were found, read the first one
    if results:
        first_id = results[0]["id"]
        print(f"\n=== 3. Reading Full Email: {first_id} ===")
        email_content = read_email(first_id)
        print(f"Subject: {email_content['subject']}")
        print(f"Body Preview:\n{email_content['body'][:300]}...")

    # Demonstrating how send and trash work (commented out by default to avoid accidental sends/deletes)
    print("\n=== 4. Example: How to Send an Email ===")
    print("""
    # To send an email:
    # send_email(
    #     to='recipient@example.com',
    #     subject='Test email from Gmail MCP',
    #     body='Hello! This email was sent via Gmail MCP.'
    # )
    """)

    print("=== 5. Example: How to Move an Email to Trash ===")
    print("""
    # To move a message to trash by its message ID:
    # trash_email(message_id='YOUR_MESSAGE_ID')
    """)


if __name__ == "__main__":
    main()
