from typing import Protocol


class IStorageAdapter(Protocol):
    def save(self, path: str, file_obj) -> str: ...
    def delete(self, path: str) -> None: ...


class LocalStorageAdapter:

    def save(self, path: str, file_obj) -> str:
        with open(path, 'wb') as f:
            f.write(file_obj.read())
            return path

def delete(self, path: str) -> None:
    import os
    if os.path.exists(path):
        os.remove(path)