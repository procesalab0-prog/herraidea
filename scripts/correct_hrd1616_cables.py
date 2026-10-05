"""Export seven evenly spaced cable rows from the original eight-row GLB.

Keep the supplied file as a reference. Remove each eighth cable and its four
terminals, then move rows 1–7 (including hardware) across the original height.
Positions are baked into meshes; the original translation animation is kept.
"""
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/projects/hrd-1616/hrd-1616-esquina.glb"
OUTPUT = SOURCE.with_name("hrd-1616-esquina-7-cables.glb")


def build():
    raw = SOURCE.read_bytes()
    length, kind = struct.unpack_from("<II", raw, 12)
    assert kind == 0x4E4F534A
    model = json.loads(raw[20:20 + length])
    binary_length, binary_kind = struct.unpack_from("<II", raw, 20 + length)
    assert binary_kind == 0x004E4942
    binary = bytearray(raw[28 + length:28 + length + binary_length])
    row_pattern = re.compile(r"^(?:Cable_[AB]|(?:Terminal|Ajuste)_[AB]_(?:Esquina|Extremo))_([1-8])$")
    removed = set()
    shifted = set()
    for index, node in enumerate(model["nodes"]):
        match = row_pattern.match(node.get("name", ""))
        if not match:
            continue
        row = int(match[1])
        if row == 8:
            removed.add(index)
            continue
        offset = (row - 1) * .015  # .09 m × 7 intervals becomes .105 m × 6.
        for primitive in model["meshes"][node["mesh"]]["primitives"]:
            accessor_index = primitive["attributes"]["POSITION"]
            assert accessor_index not in shifted, "Unexpected shared geometry"
            shifted.add(accessor_index)
            accessor = model["accessors"][accessor_index]
            assert accessor["componentType"] == 5126 and accessor["type"] == "VEC3"
            view = model["bufferViews"][accessor["bufferView"]]
            start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
            stride = view.get("byteStride", 12)
            for vertex in range(accessor["count"]):
                position = start + vertex * stride + 4
                y = struct.unpack_from("<f", binary, position)[0]
                struct.pack_into("<f", binary, position, y + offset)
            for bound in ("min", "max"):
                accessor[bound][1] += offset
    assert len(removed) == 10
    remap = {old: new for new, old in enumerate(i for i in range(len(model["nodes"])) if i not in removed)}
    model["nodes"] = [node for index, node in enumerate(model["nodes"]) if index not in removed]
    for scene in model["scenes"]:
        scene["nodes"] = [remap[index] for index in scene["nodes"] if index not in removed]
    for node in model["nodes"]:
        if "children" in node:
            node["children"] = [remap[index] for index in node["children"] if index not in removed]
    for animation in model.get("animations", []):
        animation["channels"] = [channel for channel in animation["channels"] if channel["target"]["node"] not in removed]
        for channel in animation["channels"]:
            channel["target"]["node"] = remap[channel["target"]["node"]]
    encoded = json.dumps(model, separators=(",", ":"), ensure_ascii=False).encode()
    encoded += b" " * (-len(encoded) % 4)
    total = 12 + 8 + len(encoded) + 8 + len(binary)
    OUTPUT.write_bytes(struct.pack("<III", 0x46546C67, 2, total) +
                      struct.pack("<II", len(encoded), 0x4E4F534A) + encoded +
                      struct.pack("<II", len(binary), 0x004E4942) + binary)
    print(f"{OUTPUT.name}: {len(model['nodes'])} components, 7 cables per side")


if __name__ == "__main__":
    build()
