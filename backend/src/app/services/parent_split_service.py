class ParentSplitService:

    PARENT_SIZE = 2500
    OVERLAP = 300

    def split(self, text: str) -> list[str]:
        parents = []

        start = 0

        while start < len(text):
            end = start + self.PARENT_SIZE

            parent = text[start:end].strip()

            if parent:
                parents.append(parent)

            start += (
                self.PARENT_SIZE - self.OVERLAP
            )

            if len(text[start:end].strip()) < 200:
                break

        return parents


_parent_split = None


def get_parent_split_service():
    global _parent_split

    if _parent_split is None:
        _parent_split = ParentSplitService()

    return _parent_split