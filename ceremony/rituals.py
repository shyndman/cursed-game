from ceremony import atoms


class EchoArchive:
    def __init__(self):
        self.frames = []

    def witness(self, chamber, event, snapshot):
        self.frames.append(
            {
                "event": event,
                "weight": snapshot["weight"],
                "glyph": atoms.exhibit(snapshot),
                "dominant": snapshot["dominant"],
            }
        )


class PulseSiphon:
    def __init__(self):
        self.stream = []

    def witness(self, chamber, event, snapshot):
        self.stream.append(
            {
                "length": len(chamber.ledger),
                "inked": len(snapshot["inked"]),
                "vapor": event[-1],
                "phase": snapshot["phase"],
            }
        )


class Relay:
    def __init__(self, chamber, stages):
        self.chamber = chamber
        self.stages = tuple(stages)

    def carry(self, packet):
        for stage in self.stages:
            packet = stage(self.chamber, packet)
        return packet


class Chamber:
    def __init__(self):
        self.ledger = []
        self.echoes = [EchoArchive(), PulseSiphon()]
        self.relay = Relay(
            self,
            (
                _prime_packet,
                _lex_token,
                _resolve_gate,
                _first_veto,
                _second_veto,
                _inscribe,
                _reveal,
            ),
        )

    def snapshot(self):
        return atoms.settle(tuple(tuple(event) for event in self.ledger))

    def offer(self, raw, origin="anonymous"):
        return self.relay.carry({"raw": raw, "origin": origin, "trace": [], "event": None})



def _prime_packet(chamber, packet):
    packet["trace"].append("prime")
    packet["before"] = chamber.snapshot()
    packet["carrier"] = packet["before"]["phase"]
    return packet



def _lex_token(chamber, packet):
    del chamber
    packet["trace"].append("lex")
    packet["token"] = atoms.gate_from_anything(packet["raw"])
    return packet



def _resolve_gate(chamber, packet):
    del chamber
    packet["trace"].append("gate")
    packet["gate"] = packet["token"]
    packet["slot"] = atoms.at()[packet["gate"]]
    return packet



def _first_veto(chamber, packet):
    del chamber
    packet["trace"].append("veto:surface")
    state = packet["before"]
    if state["phase"] is None:
        raise RuntimeError("the lattice has already converged")
    if packet["gate"] not in state["vacancy"]:
        raise ValueError(f"sealed locus: {packet['raw']!r}")
    if state["register"][packet["slot"]] != 0:
        raise ValueError(f"duplicate occupation by omen: {packet['raw']!r}")
    return packet



def _second_veto(chamber, packet):
    del chamber
    packet["trace"].append("veto:deep")
    state = packet["before"]
    ternary_digit = (state["weight"] // (3 ** packet["slot"])) % 3
    if ternary_digit:
        raise ValueError(f"duplicate occupation by arithmetic: {packet['raw']!r}")
    return packet



def _inscribe(chamber, packet):
    packet["trace"].append("inscribe")
    ordinal = len(chamber.ledger)
    event = (
        ordinal,
        packet["carrier"],
        packet["gate"],
        atoms.stamp(ordinal, packet["carrier"], packet["gate"]),
    )
    chamber.ledger.append(event)
    packet["event"] = event
    return packet



def _reveal(chamber, packet):
    packet["trace"].append("reveal")
    packet["after"] = chamber.snapshot()
    for witness in chamber.echoes:
        witness.witness(chamber, packet["event"], packet["after"])
    packet["glyph"] = atoms.exhibit(packet["after"])
    return packet
