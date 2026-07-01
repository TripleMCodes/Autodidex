from pathlib import Path
from pprint import pprint

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from note_worthy.services.notes_sidebar_service import (
    Note,
    NoteBook,
    NewNoteBook,
    NewNote,
    RenameNoteBook,
    RenameNote,
    NotesService,
)


# ============================================================= #
#  Link-chip widget                                             #
# ============================================================= #

class _LinkChip(QFrame):
    """A small clickable label representing one linked note.

    Signals
    -------
    clicked(note_meta: dict)
        Emitted when the user left-clicks to navigate to the linked note.
    remove_requested(note_meta: dict)
        Emitted when the user right-clicks → "Remove link".
    """

    clicked          = Signal(dict)
    remove_requested = Signal(dict)

    def __init__(self, note_meta: dict, parent=None):
        super().__init__(parent)
        self._meta = note_meta  # keys: note_id, note_title, notebook_name, note_content

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(f"{note_meta['notebook_name']} › {note_meta['note_title']}")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)
        layout.setSpacing(4)

        icon = QLabel("🔗")
        icon.setFixedWidth(16)
        layout.addWidget(icon)

        label = QLabel(note_meta["note_title"])
        label.setWordWrap(False)
        layout.addWidget(label)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    # -- events ------------------------------------------------ #

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._meta)
        super().mousePressEvent(event)

    def _on_context_menu(self, pos):
        menu = QMenu(self)
        remove_action = menu.addAction("Remove link")
        chosen = menu.exec(self.mapToGlobal(pos))
        if chosen == remove_action:
            self.remove_requested.emit(self._meta)


# ============================================================= #
#  Link-picker dialog                                           #
# ============================================================= #

class _LinkPickerDialog(QDialog):
    """Modal dialog that lets the user pick any note to link to.

    Shows a tree identical to the sidebar (notebook → notes).
    Only notes that are *not* already linked (and not the current note)
    are selectable.
    """

    def __init__(self, all_notebooks: list[dict], current_note_id: int,
                 already_linked_ids: set[int], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Link to note…")
        self.setMinimumSize(320, 400)
        self._selected_meta: dict | None = None

        layout = QVBoxLayout(self)
        layout.setSpacing(6)

        hint = QLabel("Select a note to link:")
        layout.addWidget(hint)

        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        layout.addWidget(self._tree)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._populate(all_notebooks, current_note_id, already_linked_ids)
        self._tree.itemSelectionChanged.connect(self._on_selection)

    def _populate(self, notebooks, current_note_id, already_linked_ids):
        for nb in notebooks:
            nb_item = QTreeWidgetItem(self._tree, [nb["name"]])
            nb_item.setFlags(nb_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            for note in nb.get("notes", []):
                nid = note["id"]
                if nid == current_note_id or nid in already_linked_ids:
                    continue
                note_item = QTreeWidgetItem(nb_item, [note["title"]])
                note_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "note_id":       nid,
                    "note_title":    note["title"],
                    "note_content":  note.get("content", ""),
                    "notebook_id":   nb["id"],
                    "notebook_name": nb["name"],
                })
            if nb_item.childCount():
                nb_item.setExpanded(True)

    def _on_selection(self):
        items = self._tree.selectedItems()
        if items:
            meta = items[0].data(0, Qt.ItemDataRole.UserRole)
            self._selected_meta = meta

    def _on_accept(self):
        if self._selected_meta is None:
            QMessageBox.warning(self, "No note selected", "Please select a note first.")
            return
        self.accept()

    def selected_meta(self) -> dict | None:
        return self._selected_meta


# ============================================================= #
#  Main sidebar widget                                          #
# ============================================================= #

class NotesSide(QWidget):
    note_selected = Signal(str)

    def __init__(self, base_path=None, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self._service  = NotesService()

        # cache of all notebooks (refreshed on load)
        self._all_notebooks: list[dict] = []

        # currently viewed note id (None when no note is open)
        self._current_note_id: int | None = None

        self._build_ui()

    # ------------------------------------------------------------------ #
    #  UI construction                                                     #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- toolbar ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        self.add_notebook_btn = QPushButton("+ Notebook")
        self.add_note_btn     = QPushButton("+ Note")
        self.add_note_btn.setEnabled(False)
        toolbar.addWidget(self.add_notebook_btn)
        toolbar.addWidget(self.add_note_btn)
        layout.addLayout(toolbar)

        # --- tree ---
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.tree)

        # --- note editor ---
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        self.editor.setMinimumHeight(120)
        layout.addWidget(self.editor)

        # --- linked notes panel ---
        self._links_panel = self._build_links_panel()
        layout.addWidget(self._links_panel)
        self._links_panel.hide()   # hidden until a note is selected

        # --- connections ---
        self.add_notebook_btn.clicked.connect(self._on_add_notebook)
        self.add_note_btn.clicked.connect(self._on_add_note)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

        self._load_notes()

    def _build_links_panel(self) -> QWidget:
        """Build the collapsible panel that shows linked notes."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setContentsMargins(0, 4, 0, 0)
        vbox.setSpacing(4)

        # header row
        header_row = QHBoxLayout()
        header_label = QLabel("🔗 Linked notes")
        header_label.setStyleSheet("font-weight: bold;")
        self._link_note_btn = QPushButton("+ Link note")
        self._link_note_btn.setFixedHeight(35)
        self._link_note_btn.clicked.connect(self._on_link_note)
        header_row.addWidget(header_label)
        header_row.addStretch()
        header_row.addWidget(self._link_note_btn)
        vbox.addLayout(header_row)

        # scrollable chip area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(90)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._chips_container = QWidget()
        self._chips_layout    = QVBoxLayout(self._chips_container)
        self._chips_layout.setContentsMargins(2, 2, 2, 2)
        self._chips_layout.setSpacing(3)
        self._chips_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._no_links_label = QLabel("No linked notes yet.")
        self._no_links_label.setStyleSheet("color: gray; font-style: italic;")
        self._chips_layout.addWidget(self._no_links_label)

        scroll.setWidget(self._chips_container)
        vbox.addWidget(scroll)

        return container

    # ------------------------------------------------------------------ #
    #  Load / populate tree                                                #
    # ------------------------------------------------------------------ #

    def _load_notes(self):
        self.tree.clear()
        res = self._service.get_notebooks()
        if res is None:
            return
        self._all_notebooks = res.get("notebooks", [])
        for nb in self._all_notebooks:
            nb_item = QTreeWidgetItem(self.tree, [nb["name"]])
            nb_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "notebook", "name": nb["name"], "id": nb["id"]
            })
            for note in nb.get("notes", []):
                note_item = QTreeWidgetItem([note["title"]])
                note_item.setData(0, Qt.ItemDataRole.UserRole, {
                    "type":    "note",
                    "id":      note["id"],
                    "name":    note["title"],
                    "content": note.get("content", ""),
                })
                nb_item.addChild(note_item)

    # ------------------------------------------------------------------ #
    #  Toolbar actions                                                     #
    # ------------------------------------------------------------------ #

    def _on_add_notebook(self):
        name, ok = QInputDialog.getText(self, "New Notebook", "Notebook name:")
        if not (ok and name.strip()):
            return
        res = self._service.create_notebook(name.strip())
        if res is None:
            return
        item = QTreeWidgetItem(self.tree, [name.strip()])
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "notebook",
            "id":   res["message"]["notebook_id"],
            "name": name.strip(),
        })
        self.tree.addTopLevelItem(item)
        # keep cache in sync
        self._all_notebooks.append({"id": res["message"]["notebook_id"], "name": name.strip(), "notes": []})

    def _on_add_note(self):
        notebook_item = self._selected_notebook()
        if notebook_item is None:
            return
        title, ok = QInputDialog.getText(self, "New Note", "Note title:")
        if not (ok and title.strip()):
            return

        notebook_meta = notebook_item.data(0, Qt.ItemDataRole.UserRole) or {}
        notebook_name = notebook_meta.get("name")
        content = ""
        res = self._service.create_note(notebook_name, title.strip(), content)
        if res is None:
            return
        QMessageBox.information(self, "Note Added", "Note created successfully.")

        if res and hasattr(res, "note_id") and res.note_id:
            note_item = QTreeWidgetItem([title.strip()])
            note_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type":    "note",
                "id":      res.note_id,
                "name":    title.strip(),
                "content": content,
            })
            notebook_item.addChild(note_item)
            notebook_item.setExpanded(True)
            # keep cache in sync
            for nb in self._all_notebooks:
                if nb["id"] == notebook_meta.get("id"):
                    nb["notes"].append({"id": res.note_id, "title": title.strip(), "content": content})
                    break

    def _save_note(self, note: str):
        item        = self._selected_notebook()
        note_meta_w = self._selected_note()
        if item is None or note_meta_w is None:
            return
        notebook_meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        note_data     = note_meta_w.data(0, Qt.ItemDataRole.UserRole) or {}
        if notebook_meta.get("type") == "notebook" and note_data:
            notebook_id = int(notebook_meta.get("id"))
            note_id     = int(note_data.get("id"))
            res = self._service.update_note(notebook_id, note_id, note)
            if res:
                note_data["content"] = note
                note_meta_w.setData(0, Qt.ItemDataRole.UserRole, note_data)
            return res

    # ------------------------------------------------------------------ #
    #  Link actions                                                        #
    # ------------------------------------------------------------------ #

    def _on_link_note(self):
        """Open the picker and create a link to the chosen note."""
        if self._current_note_id is None:
            return

        already_linked = {
            chip_meta["note_id"]
            for chip_meta in self._current_link_metas()
        }

        dialog = _LinkPickerDialog(
            all_notebooks    = self._all_notebooks,
            current_note_id  = self._current_note_id,
            already_linked_ids = already_linked,
            parent           = self,
        )
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        target_meta = dialog.selected_meta()
        if target_meta is None:
            return

        res = self._service.link_notes(self._current_note_id, target_meta["note_id"])
        if "Failed" in res.get("message", ""):
            QMessageBox.warning(self, "Link failed", res["message"])
            return

        self._add_chip(target_meta)

    def _on_remove_link(self, target_meta: dict):
        """Remove a link when the user right-clicks a chip."""
        if self._current_note_id is None:
            return
        confirm = QMessageBox.question(
            self, "Remove link",
            f"Remove link to '{target_meta['note_title']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self._service.unlink_notes(self._current_note_id, target_meta["note_id"])
        self._refresh_links_panel()

    def _on_navigate_to_linked(self, target_meta: dict):
        """Jump to the linked note when a chip is clicked."""
        # Find the note item in the tree and select it
        root = self.tree.invisibleRootItem()
        for nb_idx in range(root.childCount()):
            nb_item = root.child(nb_idx)
            nb_meta = nb_item.data(0, Qt.ItemDataRole.UserRole) or {}
            if nb_meta.get("id") == target_meta["notebook_id"]:
                nb_item.setExpanded(True)
                for n_idx in range(nb_item.childCount()):
                    n_item = nb_item.child(n_idx)
                    n_meta = n_item.data(0, Qt.ItemDataRole.UserRole) or {}
                    if n_meta.get("id") == target_meta["note_id"]:
                        self.tree.setCurrentItem(n_item)
                        self._open_note(n_item)
                        return
        # Note not found in tree — shouldn't happen, but soft-fail
        QMessageBox.information(self, "Not found", "Couldn't locate that note in the tree.")

    # ------------------------------------------------------------------ #
    #  Links panel helpers                                                 #
    # ------------------------------------------------------------------ #

    def _refresh_links_panel(self):
        """Reload linked notes from DB and rebuild the chip list."""
        self._clear_chips()
        if self._current_note_id is None:
            self._links_panel.hide()
            return

        res = self._service.get_note_links(self._current_note_id)
        links = res.get("links", [])

        if links:
            self._no_links_label.hide()
            for link_meta in links:
                self._add_chip(link_meta)
        else:
            self._no_links_label.show()

        self._links_panel.show()

    def _add_chip(self, note_meta: dict):
        """Append a single link chip to the panel without a full refresh."""
        self._no_links_label.hide()
        chip = _LinkChip(note_meta, parent=self._chips_container)
        chip.clicked.connect(self._on_navigate_to_linked)
        chip.remove_requested.connect(self._on_remove_link)
        self._chips_layout.addWidget(chip)

    def _clear_chips(self):
        """Remove all chip widgets (not the no-links label)."""
        for i in reversed(range(self._chips_layout.count())):
            w = self._chips_layout.itemAt(i).widget()
            if w and w is not self._no_links_label:
                w.deleteLater()

    def _current_link_metas(self) -> list[dict]:
        """Return the note_meta dicts from every chip currently shown."""
        metas = []
        for i in range(self._chips_layout.count()):
            w = self._chips_layout.itemAt(i).widget()
            if isinstance(w, _LinkChip):
                metas.append(w._meta)
        return metas

    # ------------------------------------------------------------------ #
    #  Context menu                                                        #
    # ------------------------------------------------------------------ #

    def _on_context_menu(self, pos):
        item = self.tree.itemAt(pos)
        if item is None:
            return
        meta  = item.data(0, Qt.ItemDataRole.UserRole) or {}
        itype = meta.get("type")
        menu  = QMenu(self)

        if itype == "notebook":
            rename_action   = menu.addAction("Rename notebook")
            delete_action   = menu.addAction("Delete notebook")
            add_note_action = menu.addAction("Add note")
            chosen = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if chosen == rename_action:
                self._rename_item(item, kind="notebook")
            elif chosen == delete_action:
                self._delete_notebook(item)
            elif chosen == add_note_action:
                self._on_add_note()

        elif itype == "note":
            rename_action = menu.addAction("Rename note")
            delete_action = menu.addAction("Delete note")
            link_action   = menu.addAction("Link to another note…")
            chosen = menu.exec(self.tree.viewport().mapToGlobal(pos))
            if chosen == rename_action:
                self._rename_item(item, kind="note")
            elif chosen == delete_action:
                self._delete_note(item)
            elif chosen == link_action:
                # Make sure this note is selected so _current_note_id is set
                self.tree.setCurrentItem(item)
                self._open_note(item)
                self._on_link_note()

    # ------------------------------------------------------------------ #
    #  Rename / delete helpers                                             #
    # ------------------------------------------------------------------ #

    def _rename_item(self, item, kind: str):
        new_name, ok = QInputDialog.getText(
            self, f"Rename {kind}", "New name:", text=item.text(0)
        )
        if not (ok and new_name.strip()):
            return
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        if kind == "notebook":
            self._service.rename_notebook(meta["name"], new_name.strip())
        else:
            parent      = item.parent()
            parent_meta = parent.data(0, Qt.ItemDataRole.UserRole) if parent else {}
            self._service.rename_note(parent_meta.get("name"), meta["name"], new_name.strip())
        item.setText(0, new_name.strip())
        meta["name"] = new_name.strip()
        item.setData(0, Qt.ItemDataRole.UserRole, meta)

    def _delete_notebook(self, item):
        if QMessageBox.question(
            self, "Confirm", "Delete this notebook and all its notes?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            meta = item.data(0, Qt.ItemDataRole.UserRole)
            self._service.delete_notebook(meta["name"])
            self.tree.invisibleRootItem().removeChild(item)
            self._all_notebooks = [nb for nb in self._all_notebooks if nb["id"] != meta["id"]]

    def _delete_note(self, item):
        parent = item.parent()
        if not parent:
            return
        if QMessageBox.question(
            self, "Confirm", "Delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            meta        = item.data(0, Qt.ItemDataRole.UserRole)
            parent_meta = parent.data(0, Qt.ItemDataRole.UserRole)
            self._service.delete_note(parent_meta.get("name"), meta["name"])
            parent.removeChild(item)
            if self._current_note_id == meta.get("id"):
                self._current_note_id = None
                self.editor.clear()
                self._links_panel.hide()

    # ------------------------------------------------------------------ #
    #  Selection                                                           #
    # ------------------------------------------------------------------ #

    def _on_selection_changed(self):
        self.add_note_btn.setEnabled(self._selected_notebook() is not None)

    def _selected_notebook(self) -> QTreeWidgetItem | None:
        items = self.tree.selectedItems()
        if not items:
            return None
        item = items[0]
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if meta.get("type") == "notebook":
            return item
        parent = item.parent()
        return parent if parent else None

    def _selected_note(self) -> QTreeWidgetItem | None:
        items = self.tree.selectedItems()
        if not items:
            return None
        item = items[0]
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        return item if meta.get("type") == "note" else None

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if meta.get("type") == "note":
            self._open_note(item)
        else:
            self._current_note_id = None
            self.editor.clear()
            self._links_panel.hide()

    def _open_note(self, item: QTreeWidgetItem):
        """Show a note's content and its linked-notes panel."""
        meta    = item.data(0, Qt.ItemDataRole.UserRole) or {}
        content = meta.get("content", "")
        self._current_note_id = meta.get("id")
        self.editor.setPlainText(content)
        self.note_selected.emit(str(content))
        self._refresh_links_panel()