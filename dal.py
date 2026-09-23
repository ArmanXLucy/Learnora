from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, now, today


# ------------------------------------------------------------------ users --
def create_user(name, age, profession, phone, username, email, location, password,
                 security_question=None, security_answer=None):
    conn = get_db()
    pw_hash = generate_password_hash(password)
    answer_hash = generate_password_hash(security_answer.strip().lower()) if security_answer else None
    cur = conn.execute(
        "INSERT INTO users (name, age, profession, phone, username, email, location, password_hash, "
        "security_question, security_answer_hash, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, age, profession, phone, username, email, location, pw_hash,
         security_question, answer_hash, now()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id



def get_user_by_firebase_uid(firebase_uid):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE firebase_uid = ?", (firebase_uid,)).fetchone()
    conn.close()
    return row


def get_user_by_email(email):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
    conn.close()
    return row


def create_firebase_user(name, age, profession, phone, username, email, location, firebase_uid):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO users (name, age, profession, phone, username, email, location, password_hash, firebase_uid, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, age, profession, phone, username, email, location, "", firebase_uid, now()),
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def attach_firebase_uid(user_id, firebase_uid):
    conn = get_db()
    conn.execute("UPDATE users SET firebase_uid=? WHERE id=?", (firebase_uid, user_id))
    conn.commit()
    conn.close()

def get_user_by_username(username):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def get_user_by_id(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def check_user_password(user_row, password):
    return check_password_hash(user_row["password_hash"], password)


def check_security_answer(user_row, answer):
    if not user_row["security_answer_hash"]:
        return False
    return check_password_hash(user_row["security_answer_hash"], answer.strip().lower())


def update_password(user_id, new_password):
    conn = get_db()
    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (generate_password_hash(new_password), user_id),
    )
    conn.commit()
    conn.close()


def get_or_create_preferences(user_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        conn.execute("INSERT INTO user_preferences (user_id) VALUES (?)", (user_id,))
        conn.commit()
        row = conn.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def update_avatar(user_id, avatar_path):
    conn = get_db()
    conn.execute("UPDATE users SET avatar_path=? WHERE id=?", (avatar_path, user_id))
    conn.commit()
    conn.close()


def update_security_details(user_id, security_question, security_answer=None):
    conn = get_db()
    if security_answer:
        conn.execute(
            "UPDATE users SET security_question=?, security_answer_hash=? WHERE id=?",
            (security_question, generate_password_hash(security_answer.strip().lower()), user_id),
        )
    else:
        conn.execute("UPDATE users SET security_question=? WHERE id=?", (security_question, user_id))
    conn.commit()
    conn.close()


def update_profile(user_id, name, age, profession, phone, email, location):
    conn = get_db()
    conn.execute("UPDATE users SET name=?, age=?, profession=?, phone=?, email=?, location=? WHERE id=?",
                 (name, age, profession, phone, email, location, user_id))
    conn.commit()
    conn.close()


def update_learning_preferences(user_id, learning_goal, hours_per_week, learning_style, learning_focus):
    conn = get_db()
    conn.execute("INSERT INTO user_preferences (user_id) VALUES (?) ON CONFLICT(user_id) DO UPDATE SET learning_goal=excluded.learning_goal, hours_per_week=excluded.hours_per_week, learning_style=excluded.learning_style, learning_focus=excluded.learning_focus",
                 (user_id,))
    conn.execute("UPDATE user_preferences SET learning_goal=?, hours_per_week=?, learning_style=?, learning_focus=? WHERE user_id=?",
                 (learning_goal, hours_per_week, learning_style, learning_focus, user_id))
    conn.commit()
    conn.close()


def update_settings(user_id, theme, reminders, streak_alerts, product_updates, auto_next, show_completed):
    conn = get_db()
    conn.execute("INSERT INTO user_preferences (user_id) VALUES (?) ON CONFLICT(user_id) DO UPDATE SET theme=excluded.theme, reminders=excluded.reminders, streak_alerts=excluded.streak_alerts, product_updates=excluded.product_updates, auto_next=excluded.auto_next, show_completed=excluded.show_completed", (user_id,))
    conn.execute("UPDATE user_preferences SET theme=?, reminders=?, streak_alerts=?, product_updates=?, auto_next=?, show_completed=? WHERE user_id=?",
                 (theme, int(reminders), int(streak_alerts), int(product_updates), int(auto_next), int(show_completed), user_id))
    conn.commit()
    conn.close()


def create_support_ticket(user_id, topic, message):
    conn = get_db()
    conn.execute("INSERT INTO support_tickets (user_id, topic, message, created_at) VALUES (?, ?, ?, ?)",
                 (user_id, topic, message, now()))
    conn.commit()
    conn.close()


def get_all_users(exclude_admin=True):
    conn = get_db()
    if exclude_admin:
        rows = conn.execute("SELECT * FROM users WHERE is_admin = 0 ORDER BY created_at DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return rows


# ------------------------------------------------------------- enrollment --
def create_enrollment(user_id, skill_id, hours_per_week, syllabus_source="general", syllabus_name="", syllabus_summary="", roadmap_json="[]"):
    conn = get_db()
    conn.execute(
        "INSERT INTO enrollments (user_id, skill_id, started_at, hours_per_week, syllabus_source, syllabus_name, syllabus_summary, roadmap_json) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, skill_id, now(), hours_per_week, syllabus_source, syllabus_name, syllabus_summary, roadmap_json),
    )
    conn.commit()
    conn.close()


def update_enrollment_diagnostic(user_id, skill_id, diagnostic_json):
    conn = get_db()
    conn.execute("UPDATE enrollments SET diagnostic_json=? WHERE user_id=? AND skill_id=?", (diagnostic_json, user_id, skill_id))
    conn.commit()
    conn.close()


def update_enrollment_level(user_id, skill_id, level, score, reason=""):
    conn = get_db()
    conn.execute("UPDATE enrollments SET level=?, level_score=?, level_reason=? WHERE user_id=? AND skill_id=?",
                 (level, score, reason, user_id, skill_id))
    conn.commit()
    conn.close()


def update_enrollment_plan(user_id, skill_id, hours_per_week, syllabus_source, syllabus_name, syllabus_summary, roadmap_json):
    conn = get_db()
    conn.execute(
        "UPDATE enrollments SET hours_per_week=?, syllabus_source=?, syllabus_name=?, syllabus_summary=?, roadmap_json=?, diagnostic_json='[]', level='basic', level_score=0, level_reason='' WHERE user_id=? AND skill_id=?",
        (hours_per_week, syllabus_source, syllabus_name, syllabus_summary, roadmap_json, user_id, skill_id),
    )
    conn.commit()
    conn.close()


def clear_level_baseline(user_id, skill_id):
    conn = get_db()
    conn.execute("DELETE FROM topic_progress WHERE user_id=? AND skill_id=? AND source='level_baseline'", (user_id, skill_id))
    conn.commit()
    conn.close()


def get_enrollment(user_id, skill_id):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM enrollments WHERE user_id = ? AND skill_id = ?", (user_id, skill_id)
    ).fetchone()
    conn.close()
    return row


def get_enrollments_for_user(user_id):
    conn = get_db()
    rows = conn.execute("SELECT * FROM enrollments WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    return rows


# ---------------------------------------------------------- topic progress --
def delete_topic_progress_by_source(user_id, skill_id, source):
    conn = get_db()
    conn.execute(
        "DELETE FROM topic_progress WHERE user_id = ? AND skill_id = ? AND source = ?",
        (user_id, skill_id, source),
    )
    conn.commit()
    conn.close()


def add_topic_progress(user_id, skill_id, topic_id, mastered, quiz_score, source):
    conn = get_db()
    conn.execute(
        "INSERT INTO topic_progress (user_id, skill_id, topic_id, mastered, quiz_score, source, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, skill_id, topic_id, int(mastered), quiz_score, source, now()),
    )
    conn.commit()
    conn.close()


def get_topic_progress_row(user_id, skill_id, topic_id, source):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM topic_progress WHERE user_id = ? AND skill_id = ? AND topic_id = ? AND source = ?",
        (user_id, skill_id, topic_id, source),
    ).fetchone()
    conn.close()
    return row


def upsert_topic_progress(user_id, skill_id, topic_id, mastered, quiz_score, source):
    existing = get_topic_progress_row(user_id, skill_id, topic_id, source)
    conn = get_db()
    if existing:
        conn.execute(
            "UPDATE topic_progress SET mastered = ?, quiz_score = ?, updated_at = ? WHERE id = ?",
            (int(mastered), quiz_score, now(), existing["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO topic_progress (user_id, skill_id, topic_id, mastered, quiz_score, source, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, skill_id, topic_id, int(mastered), quiz_score, source, now()),
        )
    conn.commit()
    conn.close()


def get_mastered_set(user_id, skill_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT DISTINCT topic_id FROM topic_progress WHERE user_id = ? AND skill_id = ? AND mastered = 1",
        (user_id, skill_id),
    ).fetchall()
    conn.close()
    return set(r["topic_id"] for r in rows)


def get_all_topic_progress(user_id, skill_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM topic_progress WHERE user_id = ? AND skill_id = ? ORDER BY updated_at DESC",
        (user_id, skill_id),
    ).fetchall()
    conn.close()
    return rows


# -------------------------------------------------------------- streaks ----
def record_activity(user_id):
    """Mark today as an active day for this learner (idempotent)."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO activity_log (user_id, activity_date) VALUES (?, ?)",
            (user_id, today()),
        )
        conn.commit()
    finally:
        conn.close()


def get_streak_info(user_id):
    """Returns {current_streak, longest_streak, active_dates(last 84 days), total_active_days}."""
    conn = get_db()
    rows = conn.execute(
        "SELECT activity_date FROM activity_log WHERE user_id = ? ORDER BY activity_date DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    dates = set(r["activity_date"] for r in rows)
    if not dates:
        return {"current_streak": 0, "longest_streak": 0, "active_dates": [], "total_active_days": 0}

    date_objs = sorted((datetime.strptime(d, "%Y-%m-%d") for d in dates), reverse=True)

    # current streak: consecutive days ending today or yesterday
    current_streak = 0
    cursor = datetime.strptime(today(), "%Y-%m-%d")
    date_set = set(date_objs)
    # allow the streak to still count if today hasn't been logged yet but yesterday was
    if cursor not in date_set:
        cursor -= timedelta(days=1)
    while cursor in date_set:
        current_streak += 1
        cursor -= timedelta(days=1)

    # longest streak overall
    all_sorted = sorted(date_objs)
    longest_streak = 1
    run = 1
    for i in range(1, len(all_sorted)):
        if (all_sorted[i] - all_sorted[i - 1]).days == 1:
            run += 1
            longest_streak = max(longest_streak, run)
        else:
            run = 1

    last_84 = sorted(dates)[-84:]
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "active_dates": last_84,
        "total_active_days": len(dates),
    }
