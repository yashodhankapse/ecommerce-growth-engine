from backend.database import get_connection


def save_upload(
    user_id,
    filename,
    stored_path,
    rows_count,
    columns_count
):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO uploads
            (
                user_id,
                filename,
                stored_path,
                rows_count,
                columns_count
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                filename,
                stored_path,
                rows_count,
                columns_count
            )
        )

        return cursor.lastrowid


def get_uploads(user_id=None):
    query = """
        SELECT
            uploads.*,
            users.name AS uploader_name,
            users.email AS uploader_email
        FROM uploads
        JOIN users ON users.id = uploads.user_id
    """

    params = ()

    if user_id is not None:
        query += " WHERE uploads.user_id = ?"
        params = (user_id,)

    query += " ORDER BY uploads.created_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

        return [dict(row) for row in rows]


def get_upload(upload_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM uploads WHERE id = ?",
            (upload_id,)
        ).fetchone()

        return dict(row) if row else None


def save_report(upload_id, analyst_id, title, summary):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO reports
            (upload_id, analyst_id, title, summary)
            VALUES (?, ?, ?, ?)
            """,
            (upload_id, analyst_id, title, summary)
        )

        return cursor.lastrowid


def get_reports():
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT
                reports.*,
                users.name AS analyst_name,
                uploads.filename
            FROM reports
            JOIN users ON users.id = reports.analyst_id
            JOIN uploads ON uploads.id = reports.upload_id
            ORDER BY reports.created_at DESC
        """).fetchall()

        return [dict(row) for row in rows]