import os
import unittest
from unittest.mock import patch

import labkit


class GpuDeviceTest(unittest.TestCase):
    def test_autodetect_and_override(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(
            labkit, "visible_devices", return_value=["Vulkan0: Intel GPU"]
        ):
            self.assertEqual(labkit.gpu_device(), "Vulkan0")
        with patch.dict(os.environ, {"LAB_GPU_DEVICE": "Vulkan1"}):
            self.assertEqual(labkit.gpu_device(), "Vulkan1")


if __name__ == "__main__":
    unittest.main()
