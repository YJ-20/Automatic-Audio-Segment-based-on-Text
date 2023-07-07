import json
from ui import GUI

def read_json(jsonpath):
    data = None
    try:
        with open(jsonpath, "r") as f:
            data = json.load(f)
    except:
        print(f"[*] Can't read {jsonpath}")
        exit(-1)
    return data

def main():
    cfg = read_json("config.json")
    ui = GUI(cfg)

if __name__ == "__main__":
    main()