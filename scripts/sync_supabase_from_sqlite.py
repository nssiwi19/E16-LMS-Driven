import argparse
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client


TABLES = [
    ("users", "id"),
    ("categories", "id"),
    ("system_settings", "id"),
    ("courses", "id"),
    ("audit_logs", "id"),
    ("lessons", "id"),
    ("enrollments", "id"),
    ("quizzes", "id"),
    ("questions", "id"),
    ("choices", "id"),
    ("quiz_attempts", "id"),
    ("quiz_answers", "id"),
    ("assignments", "id"),
    ("submissions", "id"),
    ("notifications", "id"),
    ("announcements", "id"),
    ("forum_threads", "id"),
    ("forum_replies", "id"),
    ("certificates", "id"),
    ("learning_logs", "log_id"),
]

TRUNCATE_ORDER = list(reversed(TABLES))
BOOLEAN_COLUMNS = {
    "users": {"is_active"},
    "courses": {"is_deleted"},
    "quizzes": {"is_published"},
    "choices": {"is_correct"},
    "quiz_attempts": {"passed"},
    "assignments": {"allow_file", "allow_text"},
    "notifications": {"is_read"},
    "announcements": {"is_pinned"},
    "forum_threads": {"is_pinned", "is_hidden"},
    "forum_replies": {"is_hidden"},
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Sync the configured local SQLite database into Supabase."
    )
    parser.add_argument("--apply", action="store_true", help="Actually delete and upsert data.")
    parser.add_argument("--batch-size", type=int, default=100, help="Rows per Supabase request.")
    parser.add_argument(
        "--skip-truncate",
        action="store_true",
        help="Upsert without deleting existing Supabase rows first.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="SQLite database path. Defaults to DATABASE_URL from .env.",
    )
    return parser.parse_args()


def sqlite_path(explicit_path=None):
    if explicit_path:
        return Path(explicit_path).resolve()

    db_url = os.environ.get("DATABASE_URL", "sqlite:///e16.db")
    if not db_url.startswith("sqlite:///"):
        raise RuntimeError(f"Only sqlite:/// DATABASE_URL is supported by this sync script: {db_url}")

    db_name = db_url.removeprefix("sqlite:///")
    candidates = [Path(db_name), Path("instance") / db_name]
    for path in candidates:
        if path.exists():
            return path.resolve()
    return candidates[-1].resolve()


def fetch_rows(conn, table):
    conn.row_factory = sqlite3.Row
    exists = conn.execute(
        "select 1 from sqlite_master where type = 'table' and name = ?", (table,)
    ).fetchone()
    if not exists:
        return []

    rows = []
    bool_cols = BOOLEAN_COLUMNS.get(table, set())
    for row in conn.execute(f"select * from {table}"):
        item = dict(row)
        for key, value in list(item.items()):
            if key in bool_cols and value is not None:
                item[key] = bool(value)
            elif isinstance(value, bytes):
                item[key] = value.decode("utf-8")
        rows.append(item)
    return rows


def count_supabase(client, table):
    response = client.table(table).select("*", count="exact").limit(0).execute()
    return response.count


def delete_all(client, table, pk):
    client.table(table).delete().neq(pk, "__e16_sync_sentinel__").execute()


def upsert_batch(client, table, rows, batch_size):
    for start in range(0, len(rows), batch_size):
        client.table(table).upsert(rows[start : start + batch_size]).execute()


def main():
    load_dotenv()
    args = parse_args()

    url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    key = service_role_key or os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY or SUPABASE_KEY.")
    if args.apply and not service_role_key:
        raise RuntimeError("Set SUPABASE_SERVICE_ROLE_KEY before running destructive sync with --apply.")

    db_path = sqlite_path(args.db)
    if not db_path.exists():
        raise RuntimeError(f"SQLite database not found: {db_path}")

    client = create_client(url, key)
    with sqlite3.connect(db_path) as conn:
        local_data = {table: fetch_rows(conn, table) for table, _ in TABLES}

    print(f"SQLite source: {db_path}")
    print(f"Mode: {'APPLY' if args.apply else 'DRY RUN'}")
    print("Preflight counts:")
    for table, _ in TABLES:
        try:
            remote_count = count_supabase(client, table)
            status = "ok"
        except Exception as exc:
            remote_count = "n/a"
            status = f"missing_or_blocked: {str(exc).splitlines()[0][:100]}"
        print(f"  {table}: local={len(local_data[table])} supabase={remote_count} {status}")

    if not args.apply:
        print("Dry run only. Run with --apply after scripts/supabase_schema.sql has been applied.")
        return

    started_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    print(f"Applying sync started_at={started_at}")

    if not args.skip_truncate:
        print("Deleting Supabase rows in FK-safe order...")
        for table, pk in TRUNCATE_ORDER:
            delete_all(client, table, pk)
            print(f"  deleted {table}")

    print("Upserting rows in FK-safe order...")
    for table, _ in TABLES:
        rows = local_data[table]
        if not rows:
            print(f"  skipped {table}: 0 rows")
            continue
        upsert_batch(client, table, rows, args.batch_size)
        print(f"  upserted {table}: {len(rows)} rows")

    print("Post-sync counts:")
    mismatch = False
    for table, _ in TABLES:
        remote_count = count_supabase(client, table)
        local_count = len(local_data[table])
        status = "ok" if remote_count == local_count else "mismatch"
        mismatch = mismatch or status == "mismatch"
        print(f"  {table}: local={local_count} supabase={remote_count} {status}")

    if mismatch:
        raise SystemExit("Sync finished with count mismatches.")
    print("Sync completed successfully.")


if __name__ == "__main__":
    main()
