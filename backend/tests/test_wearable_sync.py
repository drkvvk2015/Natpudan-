from app.services.wearable_sync import WearableSync


def test_import_wearable_data_handles_db_error_and_rolls_back():
    class FakeDB:
        def __init__(self):
            self.rollback_called = False

        def add(self, _):
            raise RuntimeError("db add failed")

        def commit(self):
            raise AssertionError("commit should not be called")

        def rollback(self):
            self.rollback_called = True

    sync = WearableSync()
    db = FakeDB()

    import asyncio
    result = asyncio.run(
        sync.import_wearable_data(
            db=db,
            patient_intake_id=1,
            device_type="fitbit",
            data_entries=[{"data_category": "heart_rate", "value": 70}],
        )
    )

    assert result["success"] is False
    assert db.rollback_called is True
