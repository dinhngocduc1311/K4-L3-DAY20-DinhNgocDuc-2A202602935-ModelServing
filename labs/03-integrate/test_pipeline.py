"""Small regression checks for the optional embedding path and context evidence."""
from __future__ import annotations

import importlib.util
import pathlib
import sys
import unittest
from unittest.mock import patch


PATH = pathlib.Path(__file__).with_name("pipeline.py")
SPEC = importlib.util.spec_from_file_location("rag_pipeline", PATH)
pipeline = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = pipeline
SPEC.loader.exec_module(pipeline)


class PipelineTest(unittest.TestCase):
    def test_explicit_bad_embedding_endpoint_fails(self) -> None:
        response = unittest.mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"data": []}
        with patch.object(pipeline.httpx, "post", return_value=response), \
             patch.object(pipeline.labkit, "die", side_effect=RuntimeError("bad embedding")):
            with self.assertRaisesRegex(RuntimeError, "bad embedding"):
                pipeline.embed(["query"], "http://localhost:8081")

    def test_answer_preserves_retrieved_text(self) -> None:
        doc = pipeline.Doc("doc-1", "retrieved text", 1.0)
        with patch.object(pipeline, "retrieve", return_value=([doc], {"embed": 0, "retrieve": 0}, "stub")), \
             patch.object(pipeline, "call_llm", return_value=("answer", 1.0, {})):
            result = pipeline.answer("question", "http://localhost:8080", None)
        self.assertEqual(result["contexts"][0]["text"], "retrieved text")


if __name__ == "__main__":
    unittest.main()
