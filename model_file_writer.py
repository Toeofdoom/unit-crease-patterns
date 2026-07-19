
import os
from pathlib import Path

import svg


class ModelFileWriter:
    def __init__(self, folder: Path, model_name: str):
        self._folder = folder
        self._model_name = model_name

        os.makedirs(self._folder, exist_ok=True)

    def write_svg(self, page: str, svg: svg.SVG):
        with open(self._folder / f"{self._model_name}_{page}.svg", 'w') as f:
            f.write(svg.as_str())