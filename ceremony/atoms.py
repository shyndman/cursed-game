import functools
import itertools


def _ash():
    return tuple(() for _ in range(len("ceremony!")))


def _side():
    return sum(len(str(len(_ash()))) for _ in "wax")


def _dust():
    return tuple(chr(code) for code in range(ord("a"), ord("a") + len(_ash())))


def _powers():
    return tuple(_side()**index for index in range(len(_ash())))


def _drift():
    sap = tuple(sum(item) for item in ((1, 3), (1, 1), (2, 4), (), (3, 5), (1,), (1, 2), (2, 3), (3, 4)))
    return tuple((item + offset - offset) for offset, item in enumerate(sap))


def aliases():
    return {str(face + 1): _dust()[slot] for face, slot in enumerate(_drift())}


def at():
    return {gate: index for index, gate in enumerate(_dust())}


def labels():
    return {slot: str(_drift().index(slot) + 1) for slot in range(len(_ash()))}


def _charm(seed, target):
    charm = seed
    for turn in (7, 11, 5, 3):
        charm = ((charm * turn) ^ (charm >> 1) ^ (target << (turn % 4))) & 0x1FFFF
    return chr(charm ^ ((charm ^ target) & 0x1FFFF))


def signs():
    return (_charm(0x6D2B, 0x133F4), _charm(0x2F19, 0x1D70E))


def _values():
    return {None: 0, signs()[0]: 1, signs()[1]: 2}


def _rev_values():
    return {value: mark for mark, value in _values().items()}


def _scrub(raw):
    return "".join(ch for ch in str(raw).strip().lower() if ch not in ",;:/| ")


def _fold(items):
    return tuple(tuple(items[start : start + _side()]) for start in range(0, len(items), _side()))


def _trit(weight, slot):
    return (weight // _powers()[slot]) % _side()


def _bit(slot):
    return 1 << (len(_ash()) - slot - 1)


def _unveil(seed):
    dust = _fold(tuple(range(len(_ash()))))
    paths = tuple(
        itertools.chain(
            dust,
            zip(*dust),
            (
                tuple(dust[index][index] for index in range(_side())),
                tuple(dust[index][~index] for index in range(_side())),
            ),
        )
    )
    return tuple(sum(_bit(knot) for knot in path) ^ seed ^ seed for path in paths)


def _route_masks():
    return _unveil(sum(ord(mark[-1]) for mark in signs()) & 0x1FF)


def gate_from_anything(raw):
    token = _scrub(raw)
    if token in aliases():
        return aliases()[token]
    if token in at():
        return token
    raise ValueError(f"unblessed locus: {raw!r}")


@functools.lru_cache(maxsize=4096)
def settle(ledger):
    weight = 0
    shadows = {mark: 0 for mark in signs()}
    residue = []

    for ordinal, carrier, gate, vapor in ledger:
        slot = at()[gate]
        value = _values()[carrier]
        weight += value * _powers()[slot]
        shadows[carrier] |= _bit(slot)
        residue.append(vapor)

    dominant = None
    thread = None
    for carrier, shadow in shadows.items():
        for route in _route_masks():
            if shadow & route == route:
                dominant = carrier
                thread = route
                break
        if dominant:
            break

    register = tuple(_trit(weight, slot) for slot in range(len(_ash())))
    vacancy = tuple(_dust()[slot] for slot, value in enumerate(register) if value == 0)
    phase = None if dominant or not vacancy else signs()[len(ledger) % len(signs())]
    faces = [_rev_values()[value] or labels()[slot] for slot, value in enumerate(register)]

    return {
        "ledger": ledger,
        "weight": weight,
        "register": register,
        "shadows": shadows,
        "mesh": _fold(faces),
        "dominant": dominant,
        "thread": thread,
        "vacancy": vacancy,
        "phase": phase,
        "sealed": dominant is not None or not vacancy,
        "spent": dominant is None and not vacancy,
        "residue": tuple(residue),
        "inked": tuple(_dust()[slot] for slot, value in enumerate(register) if value),
    }


def _tile(face):
    if face == signs()[0]:
        return ("╲ ╱", " ╳ ", "╱ ╲")
    if face == signs()[1]:
        return ("╭─╮", "│ │", "╰─╯")
    return ("   ", f" {face} ", "   ")


def exhibit(snapshot):
    faces = tuple(itertools.chain.from_iterable(snapshot["mesh"]))
    canvas = [[" " for _ in range(17)] for _ in range(11)]
    for row in (3, 7):
        for col in range(17):
            canvas[row][col] = "─"
    for col in (5, 11):
        for row in range(11):
            canvas[row][col] = "│"
    for row, col in itertools.product((3, 7), (5, 11)):
        canvas[row][col] = "┼"
    for slot, tile in enumerate(map(_tile, faces)):
        top = (slot // _side()) * 4
        left = (slot % _side()) * 6
        for y, stripe in enumerate(tile):
            for x, char in enumerate(stripe):
                if char != " ":
                    canvas[top + y][left + x] = char
    return "\n".join("".join(line).rstrip() for line in canvas)


def thread_members(snapshot):
    route = snapshot["thread"]
    if route is None:
        return ()
    return tuple(
        _dust()[slot]
        for slot, bit in enumerate((_bit(index) for index in range(len(_ash()))))
        if route & bit
    )


def stamp(ordinal, carrier, gate):
    return "{}:{}:{}:{}".format(
        ordinal,
        carrier.lower(),
        gate,
        ".".join(itertools.islice(itertools.cycle((gate, carrier.lower(), str(ordinal))), 6)),
    )
