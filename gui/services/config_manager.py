import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config.json")

DEFAULT_CONFIG = {
    "theme": "Warm Peach",
    "user_avatar": "👤",
    "agent_avatar": "🤖"
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Ensure defaults exist for new keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_theme():
    config = load_config()
    return config.get("theme", "Warm Peach")

def set_theme(theme_name):
    config = load_config()
    config["theme"] = theme_name
    save_config(config)

def get_avatars():
    config = load_config()
    return {
        "user": config.get("user_avatar", "👤"),
        "agent": config.get("agent_avatar", "🤖")
    }

def set_user_avatar(avatar):
    config = load_config()
    config["user_avatar"] = avatar
    save_config(config)

def set_agent_avatar(avatar):
    config = load_config()
    config["agent_avatar"] = avatar
    save_config(config)
