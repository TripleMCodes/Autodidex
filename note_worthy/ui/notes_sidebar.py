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
    QMessageBox,
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

        # # load existing notebooks and notes from the database
        # res = self._service.get_notebooks()  # ← you implement this to populate the tree  
        # # print(f"Notebooks data returned from service: {res}")  # Debug print
        # if res is not None:
        #     for nb in res["notebooks"]:
        #         nb_item = QTreeWidgetItem(self.tree, [nb["name"]])
        #         nb_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "notebook", "name": nb_item.text(0), "id": nb["id"]})
        #         for note in nb.get("notes", []):
        #             note_item = QTreeWidgetItem([note["title"]])
        #             # store content in the item's user data so we can show it without extra DB calls
        #             note_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "note", "id": note["id"], "name": note["title"], "content": note.get("content", "")})
        #             nb_item.addChild(note_item)

        self._load_notes()
        
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

    

    def _load_notes(self):
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

    def _on_add_note(self):
        notebook_item = self._selected_notebook()
        if notebook_item is None:
            return

        title, ok = QInputDialog.getText(self, "New Note", "Note title:")
        if not (ok and title.strip()):
            return

        # Get notebook name from the item's metadata
        notebook_meta = notebook_item.data(0, Qt.ItemDataRole.UserRole) or {}
        notebook_name = notebook_meta.get("name")
        print(f"Notebook data: {notebook_meta}")  # Debug print
        print(f"Notebook name: {notebook_name}")  # Debug print
        content = "" # empty note
        res = self._service.create_note(notebook_name, title.strip(), content)
        print(f"the response is {res}")
        if res is None:
            return
        
        # Add the new note directly to the tree without reloading
        if res and hasattr(res, 'note_id') and res.note_id:
            note_item = QTreeWidgetItem([title.strip()])
            note_item.setData(0, Qt.ItemDataRole.UserRole, {
                "type": "note",
                "id": res.note_id,
                "name": title.strip(),
                "content": content
            })
            notebook_item.addChild(note_item)
            notebook_item.setExpanded(True)
        
        QMessageBox(self, "Creation Status", res.message)

    def _save_note(self, note: str):
        item = self._selected_notebook()
        notebook_meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        note_meta = self._selected_note()
        note_data = note_meta.data(0, Qt.ItemDataRole.UserRole) or {}
        if notebook_meta.get("type") == "notebook":
            print(f"this is a note.")
            if note_data:
                print("note found")
                print(f"this is the note {note}")
                print(f"note id {note_data.get("id")}")
                print(f"notebook id {notebook_meta.get("id")}")
                notebook_id, note_id = int(notebook_meta.get("id")), int(note_data.get("id"))
                res = self._service.update_note(notebook_id, note_id, note)
                return res
            # print(f"note name {meta.get("title")} and id {meta.get("id")}")
            # parent = item.parent()
            # if parent:
            #     parent_meta = parent.data(0, Qt.ItemDataRole.UserRole)
            #     parent_notebook_name = parent_meta.get("name")
            #     print(f"the notebook name is {parent_notebook_name}")
            #     # self._service.rename_note(parent_notebook_name, meta["name"], new_name.strip())



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
            self._service.rename_notebook(meta["name"], new_name.strip())
        else:
            # For notes, need to get parent notebook name
            parent = item.parent()
            if parent:
                parent_meta = parent.data(0, Qt.ItemDataRole.UserRole)
                parent_notebook_name = parent_meta.get("name")
                self._service.rename_note(parent_notebook_name, meta["name"], new_name.strip())

        item.setText(0, new_name.strip())

    def _delete_notebook(self, item):
        meta = item.data(0, Qt.ItemDataRole.UserRole)
        self._service.delete_notebook(meta["name"])
        self.tree.invisibleRootItem().removeChild(item)

    def _delete_note(self, item):
        meta   = item.data(0, Qt.ItemDataRole.UserRole)
        parent = item.parent()
        if parent:
            parent_meta = parent.data(0, Qt.ItemDataRole.UserRole)
            parent_notebook_name = parent_meta.get("name")
            self._service.delete_note(parent_notebook_name, meta["name"])
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

    def _selected_note(self):
        """Return the note selected"""
        items = self.tree.selectedItems()
        if not items:
            return None
        item = items[0]
        meta = item.data(0, Qt.ItemDataRole.UserRole) or {}
        if meta.get("type") == "note":
            return item
        else:
            print("note not found")

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
        notebook = self._on_selected_notebook()

        # raise NotImplementedError

    def _db_add_note(self, notebook_id: int, title: str, content:str):
        """Insert a new note row. Return its integer ID."""
        res = self._service.create_note(notebook_id, title, content)
        QMessageBox.information(self, "Creation Status", res.message)


    def _db_rename_notebook(self, notebook_id: int, new_name: str):
        raise NotImplementedError

    def _db_rename_note(self, note_id: int, new_name: str):
        raise NotImplementedError

    def _db_delete_notebook(self, notebook_id: int):
        raise NotImplementedError

    def _db_delete_note(self, note_id: int):
        raise NotImplementedError