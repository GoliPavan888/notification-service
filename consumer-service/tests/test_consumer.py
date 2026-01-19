from src.consumer import process_message, processed_message_ids


def test_idempotency():
    processed_message_ids.clear()

    process_message("msg-1", "Hello")
    process_message("msg-1", "Hello")

    assert len(processed_message_ids) == 1
