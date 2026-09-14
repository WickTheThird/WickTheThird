import sys
import unittest
from pathlib import Path
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import game  # noqa: E402


class MovementTests(unittest.TestCase):
    def test_valid_move_updates_the_position(self):
        state = {"x": 8, "y": 5, "moves": 0}

        with patch.object(game, "save_state"):
            result = game.move(state, "up")

        self.assertEqual({"x": 8, "y": 4, "moves": 1}, state)
        self.assertEqual("Wick moved up.", result)

    def test_wall_blocks_the_move(self):
        state = {"x": 1, "y": 1, "moves": 0}

        with patch.object(game, "save_state") as save:
            result = game.move(state, "left")

        self.assertEqual({"x": 1, "y": 1, "moves": 0}, state)
        self.assertEqual("A wall blocks the way left.", result)
        save.assert_not_called()

    def test_only_four_exact_directions_are_accepted(self):
        with self.assertRaises(ValueError):
            game.move({"x": 8, "y": 5, "moves": 0}, "up; echo nope")


if __name__ == "__main__":
    unittest.main()
