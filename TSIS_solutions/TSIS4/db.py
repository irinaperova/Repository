import json
from pathlib import Path
from datetime import datetime

try:
    import psycopg2
except Exception:
    psycopg2 = None

from config import DB_CONFIG

BASE = Path(__file__).resolve().parent
FALLBACK = BASE / 'local_scores.json'

class Database:
    def __init__(self):
        self.conn = None
        if psycopg2:
            try:
                self.conn = psycopg2.connect(**DB_CONFIG)
                self.conn.autocommit = True
                self.init_schema()
            except Exception as e:
                print('PostgreSQL unavailable, using JSON fallback:', e)
                self.conn = None
        if not FALLBACK.exists():
            FALLBACK.write_text('[]')

    def init_schema(self):
        with self.conn.cursor() as cur:
            cur.execute((BASE / 'schema.sql').read_text())

    def get_player_id(self, username):
        if not self.conn: return None
        with self.conn.cursor() as cur:
            cur.execute('INSERT INTO players(username) VALUES(%s) ON CONFLICT(username) DO NOTHING', (username,))
            cur.execute('SELECT id FROM players WHERE username=%s', (username,))
            return cur.fetchone()[0]

    def save_result(self, username, score, level):
        username = username or 'Player'
        if self.conn:
            pid = self.get_player_id(username)
            with self.conn.cursor() as cur:
                cur.execute('INSERT INTO game_sessions(player_id, score, level_reached) VALUES(%s,%s,%s)', (pid, int(score), int(level)))
            return
        data = json.loads(FALLBACK.read_text())
        data.append({'username': username, 'score': int(score), 'level': int(level), 'played_at': datetime.now().strftime('%Y-%m-%d %H:%M')})
        data.sort(key=lambda x: x['score'], reverse=True)
        FALLBACK.write_text(json.dumps(data[:50], indent=2))

    def top10(self):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute('''
                    SELECT p.username, g.score, g.level_reached, to_char(g.played_at, 'YYYY-MM-DD HH24:MI')
                    FROM game_sessions g JOIN players p ON p.id=g.player_id
                    ORDER BY g.score DESC, g.played_at ASC LIMIT 10
                ''')
                return cur.fetchall()
        return [(x['username'], x['score'], x['level'], x['played_at']) for x in json.loads(FALLBACK.read_text())[:10]]

    def personal_best(self, username):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute('''SELECT COALESCE(MAX(g.score),0) FROM game_sessions g JOIN players p ON p.id=g.player_id WHERE p.username=%s''', (username,))
                return cur.fetchone()[0]
        scores = [x['score'] for x in json.loads(FALLBACK.read_text()) if x['username'] == username]
        return max(scores) if scores else 0
