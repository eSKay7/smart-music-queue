import sqlite3

DB_PATH = "smart_queue.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS song_interactions (
                playlist_id TEXT NOT NULL,
                song_id INTEGER NOT NULL,
                early_skipped INTEGER DEFAULT 0,
                added INTEGER DEFAULT 0,
                played INTEGER DEFAULT 0,
                removed INTEGER DEFAULT 0,
                PRIMARY KEY (playlist_id, song_id)
    )
    """)

    '''
    Code to print song interactions
    '''
    # cur.execute("""
    # SELECT * FROM song_interactions;
    #             """)
    # rows = cur.fetchall()

    # for row in rows:
    #     print(row)
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()