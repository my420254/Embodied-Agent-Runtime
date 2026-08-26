from config import settings


def _use_config(monkeypatch, config):
    monkeypatch.setattr(settings, "_ACTIVE_APP_CONFIG", config)
    monkeypatch.setattr(settings, "_ACTIVE_CONFIG_FILE", "<test>")


def test_model_config_allows_module_overrides(monkeypatch):
    _use_config(
        monkeypatch,
        {
            "model": {
                "api_base": "http://global/v1",
                "api_key": "global-key",
                "model_name": "global-model",
                "timeout": 120,
                "modules": {
                    "planning": {
                        "api_base": "http://planning/v1",
                        "api_key": "planning-key",
                        "model_name": "planning-model",
                        "temperature": 0.2,
                        "max_tokens": 4096,
                        "timeout": 180,
                    }
                },
            }
        },
    )

    config = settings.get_model_config("planning")

    assert config["base_url"] == "http://planning/v1"
    assert config["api_key"] == "planning-key"
    assert config["model"] == "planning-model"
    assert config["temperature"] == 0.2
    assert config["max_tokens"] == 4096
    assert config["timeout"] == 180


def test_model_config_module_env_overrides_global_env(monkeypatch):
    monkeypatch.setenv("LANGGRAPH_JSZN_API_BASE", "http://env-global/v1")
    monkeypatch.setenv("LANGGRAPH_JSZN_API_KEY", "env-global-key")
    monkeypatch.setenv("LANGGRAPH_JSZN_API_MODEL", "env-global-model")
    monkeypatch.setenv("LANGGRAPH_JSZN_PLANNING_API_BASE", "http://env-planning/v1")
    monkeypatch.setenv("LANGGRAPH_JSZN_PLANNING_API_KEY", "env-planning-key")
    monkeypatch.setenv("LANGGRAPH_JSZN_PLANNING_API_MODEL", "env-planning-model")
    _use_config(
        monkeypatch,
        {
            "model": {
                "api_base": "http://global/v1",
                "api_key": "global-key",
                "model_name": "global-model",
                "modules": {
                    "planning": {
                        "api_base": "http://planning/v1",
                        "api_key": "planning-key",
                        "model_name": "planning-model",
                    }
                },
            }
        },
    )

    config = settings.get_model_config("planning")

    assert config["base_url"] == "http://env-planning/v1"
    assert config["api_key"] == "env-planning-key"
    assert config["model"] == "env-planning-model"


def test_model_config_module_config_overrides_global_env(monkeypatch):
    monkeypatch.setenv("LANGGRAPH_JSZN_API_BASE", "http://env-global/v1")
    monkeypatch.setenv("LANGGRAPH_JSZN_API_KEY", "env-global-key")
    monkeypatch.setenv("LANGGRAPH_JSZN_API_MODEL", "env-global-model")
    _use_config(
        monkeypatch,
        {
            "model": {
                "api_base": "http://global/v1",
                "api_key": "global-key",
                "model_name": "global-model",
                "modules": {
                    "planning": {
                        "api_base": "http://planning/v1",
                        "api_key": "planning-key",
                        "model_name": "planning-model",
                    }
                },
            }
        },
    )

    config = settings.get_model_config("planning")

    assert config["base_url"] == "http://planning/v1"
    assert config["api_key"] == "planning-key"
    assert config["model"] == "planning-model"
