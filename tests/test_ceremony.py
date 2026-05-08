import unittest

from ceremony import atoms, operators
from ceremony.runtime import run
from ceremony.rituals import Chamber


class CeremonyTests(unittest.TestCase):
    def test_scripted_dominance(self):
        result = run("script:1,2,3", "script:4,5", chorus=False)

        self.assertEqual(result["dominant"], atoms.signs()[0])
        self.assertFalse(result["spent"])
        self.assertEqual(len(result["ledger"]), 5)
        self.assertIn(result["dominant"], result["utterance"])

    def test_full_consumption(self):
        result = run("script:1,3,4,8,6", "script:2,5,7,9", chorus=False)

        self.assertIsNone(result["dominant"])
        self.assertTrue(result["spent"])
        self.assertEqual(len(result["ledger"]), 9)
        self.assertIn("=", result["utterance"])

    def test_duplicate_move_rejected(self):
        chamber = Chamber()
        chamber.offer("1", origin="test")

        with self.assertRaises(ValueError):
            chamber.offer("1", origin="test")

    def test_hinge_oracle_opens_on_five(self):
        hand = operators.registry.materialize(atoms.signs()[0], "oracle:hinge")

        self.assertEqual(hand.pull(Chamber().snapshot()), "5")

    def test_sigil_faces_are_not_plain_marks(self):
        self.assertEqual(atoms.signs(), ("𓏴", "𝜎"))

    def test_projection_is_tiled(self):
        chamber = Chamber()
        chamber.offer("1", origin="test")
        chamber.offer("2", origin="test")
        glyph = atoms.exhibit(chamber.snapshot())

        self.assertIn("╳", glyph)
        self.assertIn("╭─╮", glyph)

    def test_script_hand_exhaustion_raises(self):
        hand = operators.registry.materialize(atoms.signs()[0], "script:1")

        self.assertEqual(hand.pull(Chamber().snapshot()), "1")
        with self.assertRaises(RuntimeError):
            hand.pull(Chamber().snapshot())


if __name__ == "__main__":
    unittest.main()
