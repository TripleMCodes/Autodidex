import json
import logging
from pathlib import Path

from autodidex_cache import DictionaryCache
from dash_board_db import Dashboard


class StoreService:
    """
    Manages the PolyMart store: item loading, purchases, and badge trades.

    Corresponds to the original PolyMart class.
    """

    def __init__(self, bank_service):
        self._bank      = bank_service
        self._dashboard = Dashboard()
        self._cache     = DictionaryCache()

        self._store_items: dict = {}   # name → lumen cost
        self._trade_items: dict = {}   # badge name → lumen reward

        self._items_file  = Path(__file__).parent.parent.parent / "dashboard files/store_items.json"
        self._badges_file = Path(__file__).parent.parent.parent / "dashboard files/game_badges.json"

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def load_store_items(self):
        """Populate store_items and trade_items from the JSON file."""
        with open(self._items_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._store_items = dict(data[0])
        self._trade_items = dict(data[1])
        logging.debug(f"StoreService: store={self._store_items}, trade={self._trade_items}")

    def get_display_items(self) -> list[str]:
        """Return formatted strings for populating a QComboBox."""
        items = [f"{k} : {v} lumens" for k, v in self._store_items.items()]
        items += [f"{k} : {v}" for k, v in self._trade_items.items()]
        return items

    def is_tradeable(self, item_label: str) -> bool:
        """Return True if the selected combo label corresponds to a trade item."""
        try:
            with open(self._badges_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            trade_badges: list = data["badges"]
        except FileNotFoundError:
            raise ValueError("game_badges.json not found.")

        item_name = item_label.partition(":")[0].strip()
        return item_name in trade_badges

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------
    def purchase(self, item_label: str) -> str:
        """
        Attempt to buy or trade the item identified by *item_label*
        (the raw combo-box text).  Returns a human-readable result string.
        """
        raw_name  = item_label.partition(":")[0].strip().lower()

        # ---- try purchase ----
        for key, value in self._store_items.items():
            if raw_name == key.strip().lower():
                cost = int(value)
                if self._bank.wallet >= cost:
                    msg = self._bank.spend_lumens(cost)
                    return msg.get("message", "Purchase complete.")
                return f"💸 Transaction failed — not enough lumens to purchase '{raw_name}'."

        # ---- try trade ----
        for key, value in self._trade_items.items():
            if raw_name == key.strip().lower():
                trade_reward = int(value)
                cached_badges = self._cache.get("badges") or []
                if raw_name.title() not in cached_badges:
                    return f"Transaction failed — you don't have '{raw_name.title()}' yet."
                if self._dashboard.remove_badge(raw_name.title()):
                    self._bank.wallet = trade_reward
                    self._cache.set("badges", self._dashboard.get_all_badges())
                    return f"Transaction complete — traded '{raw_name}' for {trade_reward} lumens."
                return "An error occurred. Please try again."

        return "❌ Item not found in PolyMart."
