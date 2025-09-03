from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Iterable, Optional

from loguru import logger
import psycopg
from psycopg.rows import dict_row


class TimescaleRepo:
    """Thin TimescaleDB repository focused on clarity and safety."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._conn: Optional[psycopg.Connection] = None

    def __enter__(self) -> "TimescaleRepo":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def connect(self) -> None:
        if self._conn is not None:
            return
        conn = psycopg.connect(self._dsn, autocommit=False)
        conn.row_factory = dict_row
        conn.execute("SET TIME ZONE 'UTC'")
        self._conn = conn
        logger.info("Connected to TimescaleDB")

    def close(self) -> None:
        if self._conn is not None:
            try:
                self._conn.close()
                logger.info("Closed TimescaleDB connection")
            finally:
                self._conn = None

    def _require_conn(self) -> psycopg.Connection:
        if self._conn is None:
            raise RuntimeError("TimescaleRepo.connect() must be called before use")
        return self._conn

    def upsert_klines(self, rows: Iterable[dict]) -> int:
        conn = self._require_conn()
        sql = (
            "INSERT INTO candlesticks (\n"
            "  ts, symbol, interval, open, high, low, close, volume, close_time,\n"
            "  quote_asset_volume, number_of_trades, taker_buy_base, taker_buy_quote\n"
            ") VALUES (\n"
            "  %(ts)s, %(symbol)s, %(interval)s, %(open)s, %(high)s, %(low)s, %(close)s, %(volume)s, %(close_time)s,\n"
            "  %(quote_asset_volume)s, %(number_of_trades)s, %(taker_buy_base)s, %(taker_buy_quote)s\n"
            ")\n"
            "ON CONFLICT (symbol, interval, ts) DO NOTHING")
        batch = list(rows)
        if not batch:
            return 0
        try:
            with conn.cursor() as cur:
                cur.executemany(sql, batch)
                inserted = cur.rowcount
            conn.commit()
            return inserted
        except Exception:
            conn.rollback()
            raise

    def fetch_ohlcv(
        self,
        symbol: str,
        interval: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        conn = self._require_conn()
        clauses = ["symbol=%s", "interval=%s"]
        params: list[object] = [symbol, interval]
        if start is not None:
            clauses.append("ts >= %s")
            params.append(start)
        if end is not None:
            clauses.append("ts <= %s")
            params.append(end)
        where = " AND ".join(clauses)

        sql = (
            "SELECT ts, symbol, interval, open, high, low, close, volume, close_time,\n"
            "       quote_asset_volume, number_of_trades, taker_buy_base, taker_buy_quote\n"
            f"FROM candlesticks WHERE {where} ORDER BY ts ASC")
        if limit is not None:
            sql += " LIMIT %s"
            params.append(limit)

        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall() or []
        return list(rows)

    def fetch_latest_n(self, symbol: str, interval: str, n: int) -> list[dict]:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute(
                ("SELECT ts, symbol, interval, open, high, low, close, volume, close_time,\n"
                 "       quote_asset_volume, number_of_trades, taker_buy_base, taker_buy_quote\n"
                 "FROM candlesticks\n"
                 "WHERE symbol=%s AND interval=%s\n"
                 "ORDER BY ts DESC\n"
                 "LIMIT %s"),
                (symbol, interval, n),
            )
            rows = cur.fetchall() or []
        rows.reverse()
        return rows

    def get_last_closed_ts(self, symbol: str, interval: str) -> Optional[datetime]:
        conn = self._require_conn()
        with conn.cursor() as cur:
            cur.execute(
                "SELECT last_closed_ts FROM sync_state WHERE symbol=%s AND interval=%s",
                (symbol, interval),
            )
            row = cur.fetchone()
        return row["last_closed_ts"] if row and row.get("last_closed_ts") else None

    def set_last_closed_ts(self, symbol: str, interval: str, ts: datetime) -> None:
        conn = self._require_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    ("INSERT INTO sync_state(symbol, interval, last_closed_ts)\n"
                     "VALUES (%s, %s, %s)\n"
                     "ON CONFLICT (symbol, interval) DO UPDATE\n"
                     "  SET last_closed_ts = EXCLUDED.last_closed_ts"),
                    (symbol, interval, ts),
                )
            conn.commit()
        except Exception:
            conn.rollback()
            raise


class AsyncTimescaleRepo:
    """Async facade that wraps TimescaleRepo and offloads work to threads."""

    def __init__(self, dsn: str):
        self._inner = TimescaleRepo(dsn)

    async def connect(self) -> None:
        await asyncio.to_thread(self._inner.connect)

    def close(self) -> None:
        self._inner.close()

    async def upsert_klines_async(self, rows: Iterable[dict]) -> int:
        return await asyncio.to_thread(self._inner.upsert_klines, rows)

    async def set_last_closed_ts_async(self, symbol: str, interval: str,
                                       ts: datetime) -> None:
        await asyncio.to_thread(self._inner.set_last_closed_ts, symbol, interval, ts)

    async def fetch_ohlcv_async(
        self,
        symbol: str,
        interval: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[dict]:
        return await asyncio.to_thread(self._inner.fetch_ohlcv, symbol, interval, start,
                                       end, limit)

    async def fetch_latest_n_async(self, symbol: str, interval: str,
                                   n: int) -> list[dict]:
        return await asyncio.to_thread(self._inner.fetch_latest_n, symbol, interval, n)

    async def get_last_closed_ts_async(self, symbol: str,
                                       interval: str) -> Optional[datetime]:
        return await asyncio.to_thread(self._inner.get_last_closed_ts, symbol, interval)
