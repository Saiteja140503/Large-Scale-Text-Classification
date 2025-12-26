from typing import Dict, Any

def log_classification_async(table, item: Dict[str, Any]) -> None:
    """
    Asynchronous-style logging to DynamoDB.
    Fire-and-forget pattern - does not wait for response.
    """
    try:
        table.put_item(Item=item)
    except Exception as e:
        print(f"Logging error (non-blocking): {e}")
