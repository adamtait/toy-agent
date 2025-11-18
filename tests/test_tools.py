import unittest
import os
from src import tools

class TestTools(unittest.TestCase):

    def test_list_files(self):
        # Create a dummy directory structure
        os.makedirs("test_dir/subdir", exist_ok=True)
        with open("test_dir/file1.txt", "w") as f:
            f.write("hello")
        with open("test_dir/subdir/file2.txt", "w") as f:
            f.write("world")

        result = tools.list_files("test_dir")

        self.assertTrue(result["success"])
        self.assertEqual(result["count"], 2)
        self.assertIn("test_dir/file1.txt", result["files"])
        self.assertIn("test_dir/subdir/file2.txt", result["files"])

        # Clean up
        os.remove("test_dir/file1.txt")
        os.remove("test_dir/subdir/file2.txt")
        os.rmdir("test_dir/subdir")
        os.rmdir("test_dir")

if __name__ == '__main__':
    unittest.main()
