# app/utils.py
import json, os

def load_sample_conversations(path):
    if os.path.exists(path):
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return []
