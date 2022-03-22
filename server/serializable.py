from typing import List


class Serializable:
    def public_json(self) -> dict:
        raise NotImplemented()

    def private_json(self) -> dict:
        return self.public_json()


def serialize_list(lst: List[Serializable]) -> List[dict]:
    return list(map(
        lambda element: element.public_json(),
        lst
    ))
