from pathlib import Path
from pydantic import BaseModel, Field, field_validator

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QPushButton,
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
    RenameNote
)  
from note_worthy_db import NotesService 



class NotesSide(QWidget):

    def __init__(self, base_path=None, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self._build_ui()
        self._service = NotesService()

    # ------------------------------------------------------------------ #
    #  UI                                                                  #
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
        self.add_note_btn.setEnabled(False)          # needs a notebook selected

        toolbar.addWidget(self.add_notebook_btn)
        toolbar.addWidget(self.add_note_btn)
        layout.addLayout(toolbar)

        # --- tree ---
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        layout.addWidget(self.tree)

        # --- connections ---
        self.add_notebook_btn.clicked.connect(self._on_add_notebook)
        self.add_note_btn.clicked.connect(self._on_add_note)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

    # ------------------------------------------------------------------ #
    #  Toolbar actions                                                     #
    # ------------------------------------------------------------------ #

    def _on_add_notebook(self):
        name, ok = QInputDialog.getText(self, "New Notebook", "Notebook name:")
        if not (ok and name.strip()):
            return

        notebook_id = self._db_add_notebook(name.strip())   # ← you implement
        if notebook_id is None:
            return

        item = QTreeWidgetItem(self.tree, [name.strip()])
        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "notebook", "id": notebook_id})
        self.tree.addTopLevelItem(item)

    def _on_add_note(self):
        notebook_item = self._selected_notebook()
        if notebook_item is None:
            return

        title, ok = QInputDialog.getText(self, "New Note", "Note title:")
        if not (ok and title.strip()):
            return

        notebook_id = notebook_item.data(0, Qt.ItemDataRole.UserRole)["id"]
        note_id     = self._db_add_note(notebook_id, title.strip())   # ← you implement
        if note_id is None:
            return

        child = QTreeWidgetItem([title.strip()])
        child.setData(0, Qt.ItemDataRole.UserRole, {"type": "note", "id": note_id})
        notebook_item.addChild(child)
        notebook_item.setExpanded(True)

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
            rename_action = menu.addAction("Rename notebook")
            delete_action = menu.addAction("Delete notebook")
            chosen = menu.exec(self.tree.viewport().mapToGlobal(pos))

            if chosen == rename_action:
                self._rename_item(item, kind="notebook")
            elif chosen == delete_action:
                self._delete_notebook(item)

        elif itype == "note":
            rename_action = menu.addAction("Rename note")
            delete_action = menu.addAction("Delete note")
            chosen = menu.exec(self.tree.viewport().mapToGlobal(pos))

            if chosen == rename_action:
                self._rename_item(item, kind="note")
            elif chosen == delete_action:
                self._delete_note(item)

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
            self._db_rename_notebook(meta["id"], new_name.strip())   # ← you implement
        else:
            self._db_rename_note(meta["id"], new_name.strip())        # ← you implement

        item.setText(0, new_name.strip())

    def _delete_notebook(self, item):
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        self._db_delete_notebook(meta["id"])                          # ← you implement
        self.tree.invisibleRootItem().removeChild(item)

    def _delete_note(self, item):
        meta   = item.data(0, Qt.ItemDataRole.UserRole)
        parent = item.parent()
        self._db_delete_note(meta["id"])                              # ← you implement
        if parent:
            parent.removeChild(item)

    # ------------------------------------------------------------------ #
    #  Selection                                                           #
    # ------------------------------------------------------------------ #

    def _on_selection_changed(self):
        self.add_note_btn.setEnabled(self._selected_notebook() is not None)

    def _selected_notebook(self):
        """Return the notebook QTreeWidgetItem that is currently active."""
        items = self.tree.selectedItems()
        if not items:
            return None
        item = items[0]
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if meta.get("type") == "notebook":
            return item
        # if a note is selected, return its parent notebook
        parent = item.parent()
        if parent:
            return parent
        return None

    # ------------------------------------------------------------------ #
    #  DB stubs — fill these in                                            #
    # ------------------------------------------------------------------ #

    def _db_add_notebook(self, name: str):
        """Insert a new notebook row. Return its integer ID."""
        raise NotImplementedError

    def _db_add_note(self, notebook_id: int, title: str):
        """Insert a new note row. Return its integer ID."""
        raise NotImplementedError

    def _db_rename_notebook(self, notebook_id: int, new_name: str):
        raise NotImplementedError

    def _db_rename_note(self, note_id: int, new_name: str):
        raise NotImplementedError

    def _db_delete_notebook(self, notebook_id: int):
        raise NotImplementedError

    def _db_delete_note(self, note_id: int):
        raise NotImplementedError