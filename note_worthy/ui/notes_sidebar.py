from pathlib import Path
from pprint import pprint
from pydantic import BaseModel, Field, field_validator


from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QInputDialog,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
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
from note_worthy.services.notes_sidebar_service import NotesService



class NotesSide(QWidget):
    note_selected = Signal(str)

    def __init__(self, base_path=None, parent=None):
        super().__init__(parent)
        self.base_path = base_path
        self._service = NotesService()
        self._build_ui()

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
        # editor to display note content
        self.editor = QTextEdit()
        self.editor.setReadOnly(True)
        layout.addWidget(self.editor)
        # --- connections ---
        self.add_notebook_btn.clicked.connect(self._on_add_notebook)
        self.add_note_btn.clicked.connect(self._on_add_note)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.customContextMenuRequested.connect(self._on_context_menu)

        # load existing notebooks and notes from the database
        res = self._service.get_notebooks()  # ← you implement this to populate the tree  
        # print(f"Notebooks data returned from service: {res}")  # Debug print
        if res is not None:
            for nb in res["notebooks"]:
                nb_item = QTreeWidgetItem(self.tree, [nb["name"]])
                nb_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "notebook", "name": nb_item.text(0), "id": nb["id"]})
                for note in nb.get("notes", []):
                    note_item = QTreeWidgetItem([note["title"]])
                    # store content in the item's user data so we can show it without extra DB calls
                    note_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "note", "id": note["id"], "name": note["title"], "content": note.get("content", "")})
                    nb_item.addChild(note_item)
        
      # data format
    #   { 'notebooks': [ { 'id': 2,
    #                'name': 'Updated Test Notebook',
    #                'notes': [ { 'content': 'This is a test note.',
    #                             'created_at': '2026-06-05 16:54:42',
    #                             'id': 1,
    #                             'title': 'Test Note',
    #                             'updated_at': '2026-06-05 16:54:42'}]},
    #              {'id': 6, 'name': 'black', 'notes': []},
    #              {'id': 8, 'name': 'book', 'notes': []},
    #              {'id': 1, 'name': 'book 1', 'notes': []},
    #              {'id': 11, 'name': 'book oc c', 'notes': []},
    #              {'id': 3, 'name': 'chud', 'notes': []},
    #              {'id': 9, 'name': 'lakfdl', 'notes': []},
    #              { 'id': 5,
    #                'name': 'my book',
    #                'notes': [ { 'content': "don't throw rocks at the throne if "
    #                                        "you can't wear the crown",
    #                             'created_at': '2026-06-18 22:50:10',
    #                             'id': 5,
    #                             'title': 'some thoughts',
    #                             'updated_at': '2026-06-18 22:50:10'}]},
    #              { 'id': 7,
    #                'name': 'physics',
    #                'notes': [ { 'content': 'f = ma',
    #                             'created_at': '2026-06-18 22:42:20',
    #                             'id': 2,
    #                             'title': 'equation 1',
    #                             'updated_at': '2026-06-18 22:42:20'},
    #                           { 'content': 'f = ma',
    #                             'created_at': '2026-06-18 22:43:18',
    #                             'id': 3,
    #                             'title': 'equation 1',
    #                             'updated_at': '2026-06-18 22:43:18'},
    #                           { 'content': 'f = ma',
    #                             'created_at': '2026-06-18 22:45:29',
    #                             'id': 4,
    #                             'title': 'equation 1',
    #                             'updated_at': '2026-06-18 22:45:29'}]},
    #              {'id': 10, 'name': 'problem', 'notes': []},
    #              {'id': 4, 'name': 'something', 'notes': []}]}
    # ------------------------------------------------------------------ #
    #  Toolbar actions                                                     #
    # ------------------------------------------------------------------ #

    def _on_add_notebook(self):
        name, ok = QInputDialog.getText(self, "New Notebook", "Notebook name:")
        if not (ok and name.strip()):
            return

        notebook_id = self._service.create_notebook(name.strip())
        print(f"Notebook Data returned from service: {notebook_id}")  # Debug print
        if notebook_id is None:
            return

        item = QTreeWidgetItem(self.tree, [name.strip()])
        item.setData(0, Qt.ItemDataRole.UserRole, {"type": "notebook", "id": notebook_id["message"]["notebook_id"], "name": name.strip()})
        self.tree.addTopLevelItem(item)

    def _on_add_note(self):
        notebook_item = self._selected_notebook()
        if notebook_item is None:
            return

        title, ok = QInputDialog.getText(self, "New Note", "Note title:")
        if not (ok and title.strip()):
            return

        notebook_id = notebook_item.data(0, Qt.ItemDataRole.UserRole)["id"]
        note_id = None
        print(f"Notebook data: {notebook_item.data(0, Qt.ItemDataRole.UserRole)}")  # Debug print
        print(f"Notebook ID: {notebook_item.data(0, Qt.ItemDataRole.UserRole)['id']}") # Debug print
        print(f"ID of the notebook: {notebook_id}")  # Debug print
        # note_id     = self._service.add_note(notebook_id, title.strip())
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
            self._service.rename_notebook(meta["id"], new_name.strip())   # ← you implement
        else:
            self._service.rename_note(meta["id"], new_name.strip())        # ← you implement

        item.setText(0, new_name.strip())

    def _delete_notebook(self, item):
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        self._service.delete_notebook(meta["id"])                          # ← you implement
        self.tree.invisibleRootItem().removeChild(item)

    def _delete_note(self, item):
        meta   = item.data(0, Qt.ItemDataRole.UserRole)
        parent = item.parent()
        self._service.delete_note(meta["id"])                              # ← you implement
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

    # def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
    #     """Show the content of a clicked note in the editor (or clear for notebooks)."""
    #     meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
    #     if meta.get("type") == "note":
    #         content = meta.get("content", "")
    #         self.editor.setPlainText(content)
    #     else:
    #         # clicked a notebook; clear the editor or optionally show notebook summary
    #         self.editor.clear()

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if meta.get("type") == "note":
            content = meta.get("content", "")
            self.editor.setPlainText(content)
            pprint(f"Note content: {content}")  # Debug print   
            # emit for the main editor
            self.note_selected.emit(str(content))
        else:
            self.editor.clear()

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