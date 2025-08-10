from __future__ import annotations

from datetime import datetime
from datetime import timezone
from typing import Iterable, Optional

import psycopg
from psycopg.rows import dict_row


class TimescaleRepo:

    def __init__(self, dsn: str):
        self._dsn = dsn

    def connect(self):
        self._conn = psycopg.connect(self._dsn, autocommit=False)
        self._conn.execute("SET TIME ZONE 'UTC'")
        self._cur = self._conn.cursor(row_factory=dict_row)

    def close(self):
        self._cur.close()
        self._conn.close()

    def upsert_klines(self, rows: Iterable[dict]) -> int:
        sql = """
        INSERT INTO candlesticks (
          ts, symbol, interval, open, high, low, close, volume, close_time,
          quote_asset_volume, number_of_trades, taker_buy_base, taker_buy_quote
        ) VALUES (
          %(ts)s, %(symbol)s, %(interval)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(close_time)s,
          %(quote_asset_volume)s, %(number_of_trades)s, %(taker_buy_base)s, %(taker_buy_quote)s
        )
        ON CONFLICT (symbol, interval, ts) DO NOTHING
        """
        self._cur.executemany(sql, list(rows))
        inserted = self._cur.rowcount
        self._conn.commit()
        return inserted

    def get_last_closed_ts(self, symbol: str,
                           interval: str) -> Optional[datetime]:
        self._cur.execute(
            "SELECT last_closed_ts FROM sync_state WHERE symbol=%s AND interval=%s",
            (symbol, interval),
        )
        row = self._cur.fetchone()
        return row["last_closed_ts"] if row and row["last_closed_ts"] else None

    def set_last_closed_ts(self, symbol: str, interval: str,
                           ts: datetime) -> None:
        self._cur.execute(
            """
            INSERT INTO sync_state(symbol, interval, last_closed_ts)
            VALUES (%s, %s, %s)
            ON CONFLICT (symbol, interval) DO UPDATE
              SET last_closed_ts = EXCLUDED.last_closed_ts
            """,
            (symbol, interval, ts),
        )
        self._conn.commit()
