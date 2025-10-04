from snapshot import export_daily_snapshot

if __name__ == "__main__":
    path = export_daily_snapshot()
    print(f"Snapshot exported to: {path}")
