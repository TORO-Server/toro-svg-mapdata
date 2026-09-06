import json
import xml.etree.ElementTree as ET
from pathlib import Path

from svgpathtools import parse_path


SVG_FILE = Path("./../alldata.svg")
OUTPUT_FILE = Path("./output.json")

INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
INKSCAPE = "{http://www.inkscape.org/namespaces/inkscape}"


def get_label(element):
    """Inkscapeのlabelを取得"""
    return element.get(f"{{{INKSCAPE_NS}}}label")


def get_path_length(element):
    """SVG pathの長さをSVG座標系の単位で取得"""
    d = element.get("d")

    if not d:
        return 0.0

    path = parse_path(d)
    return path.length()


def find_railway_layer(root):
    """inkscape:label='鉄道' の要素を探す"""
    for element in root.iter():
        if get_label(element) == "鉄道":
            return element

    raise ValueError("inkscape:label='鉄道' の要素が見つかりません")


def find_reference_length(root):
    """
    SVG全体から inkscape:label="500m" のpathを探す
    """
    for element in root.iter():
        if get_label(element) == "500m":
            d = element.get("d")

            if not d:
                raise ValueError(
                    "label='500m' の要素に d 属性がありません"
                )

            length = parse_path(d).length()

            if length <= 0:
                raise ValueError(
                    "label='500m' のパス長が0です"
                )

            return length

    raise ValueError(
        "inkscape:label='500m' の要素が見つかりません"
    )


def is_layer(element):
    """階層2のlayerか判定"""
    return element.get(
        f"{{{INKSCAPE_NS}}}groupmode"
    ) == "layer"


def calculate():
    tree = ET.parse(SVG_FILE)
    root = tree.getroot()

    # 階層1
    railway = find_railway_layer(root)

    # 基準となるSVG上の長さ
    reference_svg_length = find_reference_length(root)

    # 1 SVG unitが何mに相当するか
    meter_per_svg_unit = 500.0 / reference_svg_length

    result = {}

    # 階層2
    for layer in railway:
        if not is_layer(layer):
            continue

        layer_name = get_label(layer) or "(名前なし)"

        total_svg_length = 0.0
        paths = []

        # 階層3
        for element in layer.iter():
            if element.tag.endswith("path"):
                length = get_path_length(element)

                total_svg_length += length

                paths.append({
                    "id": element.get("id"),
                    "svg_length": length,
                    "length_m": length * meter_per_svg_unit,
                    "label": element.get(INKSCAPE + "label"),
                })

        result[layer_name] = {
            "length_m": total_svg_length * meter_per_svg_unit,
            "paths": paths,
        }

    return {
        "reference": {
            "label": "500m",
            "svg_length": reference_svg_length,
            "meters_per_svg_unit": meter_per_svg_unit,
        },
        "layers": result,
    }


def main():
    result = calculate()

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n出力: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
