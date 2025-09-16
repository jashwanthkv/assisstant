from services.Firebase_memory import store_message

USER_ID = "test_user"

def seed():
    conversation = [
        ("user", "currently i am learning about trees in DSA"),
        ("user", "perfect tree has all internal nodes filled and all leafs are at last level"),
    ]

    for role, content in conversation:
        store_message(USER_ID, role, content)
        print(f"Stored: {role} → {content}")

if __name__ == "__main__":
    seed()
