from src.core.engines.ollama_adapter import OllamaAdapter


def test_hrm_model_selected_for_puzzle_tasks(tmp_path):
    adapter = OllamaAdapter("configs/policies.yaml")
    assert "hrm" in adapter.models, "HRM model configuration is missing"
    selected = adapter._select_model("text", "puzzle", latency_requirement=800)
    assert selected == "hrm"
