from pathlib import Path

CONFIG_PATH = Path(__file__).parent.joinpath("config")


def _safe_read(path: Path) -> str:
    with path.open("r") as f:
        return f.read()


def load_formats():
    css = _safe_read(CONFIG_PATH.joinpath("css.txt"))
    recall_front = _safe_read(CONFIG_PATH.joinpath("recall_front.txt"))
    recall_back = _safe_read(CONFIG_PATH.joinpath("recall_back.txt"))
    recon_front = _safe_read(CONFIG_PATH.joinpath("recon_front.txt"))
    recon_back = _safe_read(CONFIG_PATH.joinpath("recon_back.txt"))
    return {
        "css": css,
        "recall_front": recall_front,
        "recall_back": recall_back,
        "recon_front": recon_front,
        "recon_back": recon_back,
    }


def load_template():
    formats = load_formats()
    return {
        "inOrderFields": [
            "Expression",
            "PartOfSpeech",
            "Spelling",
            "Pitch",
            "Frequency",
            "Meanings",
            "Examples",
        ],
        "css": formats["css"],
        "cardTemplates": [
            {
                "Name": "Recognition",
                "Front": formats["recon_front"],
                "Back": formats["recon_back"],
            },
            {
                "Name": "Recall",
                "Front": formats["recall_front"],
                "Back": formats["recall_back"],
            },
        ],
    }
