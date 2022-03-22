from typing import List


class Serializable:
    def json(self) -> dict:
        raise NotImplemented()


def serialize_list(lst: List[Serializable]) -> List[dict]:
    return list(map(
        lambda element: element.json(),
        lst
    ))
