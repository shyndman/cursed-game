import collections
import itertools

from ceremony import atoms


WHEELS = collections.OrderedDict(
    (
        ("hinge", ("5", "1", "3", "7", "9", "2", "4", "6", "8")),
        ("rim", ("1", "3", "7", "9", "5", "2", "4", "6", "8")),
    )
)
CHOIRS = (
    ("a", "e", "i"),
    ("c", "e", "g"),
    ("a", "c", "g", "i"),
)


class Vessel:
    def __init__(self, carrier, payload, humors, draw):
        self.carrier = carrier
        self.payload = payload
        self.humors = humors
        self._draw = draw

    def pull(self, snapshot):
        return self._draw(self, snapshot)


class Registry:
    def __init__(self):
        codex = collections.OrderedDict(
            (
                ("human", (_prime_human, _draw_human)),
                ("script", (_prime_script, _draw_script)),
                ("oracle", (_prime_oracle, _draw_oracle)),
            )
        )
        self.forge = {
            species: _distill_species(species, primer, draw)
            for species, (primer, draw) in codex.items()
        }

    def materialize(self, carrier, spec):
        species, _, payload = (spec or "human").partition(":")
        if species not in self.forge:
            raise ValueError(f"unknown hand species: {species}")
        return self.forge[species](carrier, payload)



def _distill_species(species, primer, draw):
    title = "".join(piece.capitalize() for piece in f"{species} residue".split())

    def __init__(self, carrier, payload=""):
        Vessel.__init__(self, carrier, payload, primer(carrier, payload), draw)

    return type(title, (Vessel,), {"__init__": __init__})



def _prime_human(carrier, payload):
    return {
        "prompt": f"[{carrier}] emit a locus: ",
        "payload": payload or "stdin",
    }



def _draw_human(vessel, snapshot):
    del snapshot
    return input(vessel.humors["prompt"])



def _prime_script(carrier, payload):
    queue = collections.deque(
        token for token in (piece.strip() for piece in payload.split(",")) if token
    )
    sentinel = object()

    def siphon():
        return queue.popleft() if queue else sentinel

    return {
        "queue": queue,
        "stream": iter(siphon, sentinel),
        "fuse": f"script exhausted for {carrier}",
    }



def _draw_script(vessel, snapshot):
    del snapshot
    try:
        return next(vessel.humors["stream"])
    except StopIteration as exc:
        raise RuntimeError(vessel.humors["fuse"]) from exc



def _prime_oracle(carrier, payload):
    del carrier
    route = payload or "hinge"
    if route not in MOUTHS:
        raise ValueError(f"unknown oracle liturgy: {route}")
    return {"route": route}



def _draw_oracle(vessel, snapshot):
    return MOUTHS[vessel.humors["route"]](vessel.carrier, snapshot)



def _vacant_numbers(snapshot):
    return tuple(str(atoms.AT[gate] + 1) for gate in snapshot["vacancy"])



def _choose(sequence, snapshot):
    vacancy = _vacant_numbers(snapshot)
    try:
        return next(candidate for candidate in sequence if candidate in vacancy)
    except StopIteration as exc:
        raise RuntimeError("oracle found no move") from exc



def _hinge(carrier, snapshot):
    del carrier
    return _choose(WHEELS["hinge"], snapshot)



def _rim(carrier, snapshot):
    del carrier
    return _choose(WHEELS["rim"], snapshot)



def _braid(carrier, snapshot):
    if snapshot["shadows"][carrier] == 0:
        return _choose(("5", "1", "9", "3", "7"), snapshot)
    residue = (
        str(atoms.AT[gate] + 1)
        for gate in itertools.chain.from_iterable(CHOIRS)
        if gate in snapshot["vacancy"]
    )
    return _choose(residue, snapshot)


MOUTHS = {
    "hinge": _hinge,
    "rim": _rim,
    "braid": _braid,
}


registry = Registry()
