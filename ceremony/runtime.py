from ceremony import atoms, operators, rituals


def _decode(*codes):
    return "".join(chr(code) for code in codes)


def _vocables():
    return {
        "crown": _decode(119, 105, 110, 110, 101, 114),
        "thread": _decode(115, 101, 97, 109),
        "still": _decode(100, 114, 97, 119),
        "void": _decode(78, 111, 110, 101),
        "turn": _decode(110, 101, 120, 116),
        "hatch": _decode(111, 112, 101, 110),
    }


class Match:
    def __init__(self, first_spec, second_spec, chorus=True):
        self.chamber = rituals.Chamber()
        self.hands = {
            atoms.signs()[0]: operators.registry.materialize(atoms.signs()[0], first_spec),
            atoms.signs()[1]: operators.registry.materialize(atoms.signs()[1], second_spec),
        }
        self.chorus = chorus
        self.transcript = []

    def cycle(self):
        while True:
            snapshot = self.chamber.snapshot()
            if snapshot["sealed"]:
                return snapshot
            carrier = snapshot["phase"]
            hand = self.hands[carrier]
            raw = hand.pull(snapshot)
            packet = self.chamber.offer(raw, origin=type(hand).__name__)
            self.transcript.append(packet)
            if self.chorus:
                print()
                print(packet["glyph"])
                print(_murmur(packet["after"]))



def _murmur(snapshot):
    if snapshot["dominant"]:
        seam = ", ".join(atoms.thread_members(snapshot))
        return f"{_vocables()['crown']}={snapshot['dominant']} {_vocables()['thread']}={seam}"
    if snapshot["spent"]:
        return f"{_vocables()['crown']}={_vocables()['void']} {_vocables()['thread']}={_vocables()['still']}"
    return f"{_vocables()['turn']}={snapshot['phase']} {_vocables()['hatch']}={','.join(snapshot['vacancy'])}"



def run(first_spec="human", second_spec="human", chorus=True):
    match = Match(first_spec, second_spec, chorus=chorus)
    final = match.cycle()
    return {
        "match": match,
        "final": final,
        "glyph": atoms.exhibit(final),
        "utterance": _murmur(final),
        "dominant": final["dominant"],
        "spent": final["spent"],
        "ledger": tuple(match.chamber.ledger),
    }
