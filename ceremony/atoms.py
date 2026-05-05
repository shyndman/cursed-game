import functools
import itertools
import math


RING = "abcdefghi"
ALIASES = {str(index + 1): gate for index, gate in enumerate(RING)}
AT = {gate: index for index, gate in enumerate(RING)}
LABELS = {index: str(index + 1) for index in range(len(RING))}
SIGNS = tuple(chr(code) for code in (88, 79))
VALUES = {None: 0, SIGNS[0]: 1, SIGNS[1]: 2}
REV_VALUES = {value: mark for mark, value in VALUES.items()}
SPAN = math.isqrt(len(RING))


def _scrub(raw):
    return "".join(ch for ch in str(raw).strip().lower() if ch not in ",;:/| ")


def _fold(items):
    return tuple(tuple(items[start : start + SPAN]) for start in range(0, len(items), SPAN))


def _weight(cells):
    return sum(value * (3 ** slot) for slot, value in enumerate(cells))


def _bit(slot):
    return 1 << (len(RING) - slot - 1)


def _routes():
    mesh = _fold(tuple(range(len(RING))))
    return tuple(
        tuple(path)
        for path in itertools.chain(
            mesh,
            zip(*mesh),
            (
                tuple(mesh[index][index] for index in range(SPAN)),
                tuple(mesh[index][SPAN - index - 1] for index in range(SPAN)),
            ),
        )
    )


ROUTES = _routes()
ROUTE_MASKS = tuple(sum(_bit(slot) for slot in route) for route in ROUTES)


def gate_from_anything(raw):
    token = _scrub(raw)
    if token in ALIASES:
        return ALIASES[token]
    if token in AT:
        return token
    raise ValueError(f"unblessed locus: {raw!r}")


@functools.lru_cache(maxsize=4096)
def settle(ledger):
    register = [0] * len(RING)
    shadows = {mark: 0 for mark in SIGNS}
    residue = []

    for ordinal, carrier, gate, vapor in ledger:
        slot = AT[gate]
        value = VALUES[carrier]
        register[slot] = value
        shadows[carrier] |= _bit(slot)
        residue.append(vapor)

    dominant = None
    thread = None
    for carrier, shadow in shadows.items():
        for route in ROUTE_MASKS:
            if shadow & route == route:
                dominant = carrier
                thread = route
                break
        if dominant:
            break

    vacancy = tuple(RING[slot] for slot, value in enumerate(register) if value == 0)
    phase = None if dominant or not vacancy else SIGNS[len(ledger) % len(SIGNS)]
    faces = [REV_VALUES[value] or LABELS[slot] for slot, value in enumerate(register)]

    return {
        "ledger": ledger,
        "weight": _weight(register),
        "register": tuple(register),
        "shadows": shadows,
        "mesh": _fold(faces),
        "dominant": dominant,
        "thread": thread,
        "vacancy": vacancy,
        "phase": phase,
        "sealed": dominant is not None or not vacancy,
        "spent": dominant is None and not vacancy,
        "residue": tuple(residue),
        "inked": tuple(RING[slot] for slot, value in enumerate(register) if value),
    }


def exhibit(snapshot):
    bands = [" {} ".format(" | ".join(triad)) for triad in snapshot["mesh"]]
    return ("\n" + "+".join("---" for _ in range(SPAN)) + "\n").join(bands)


def thread_members(snapshot):
    route = snapshot["thread"]
    if route is None:
        return ()
    return tuple(
        RING[slot]
        for slot, bit in enumerate((_bit(index) for index in range(len(RING))))
        if route & bit
    )


def stamp(ordinal, carrier, gate):
    return "{}:{}:{}:{}".format(
        ordinal,
        carrier.lower(),
        gate,
        ".".join(itertools.islice(itertools.cycle((gate, carrier.lower(), str(ordinal))), 6)),
    )
