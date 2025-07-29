from pathlib import Path


source_path = Path("obs4REF_source_id")

necessary_source = [
    "20cr-v2.json",
    "aviso-1-0.json",
    "c3s-gto-ecv-9-0.json",
    "ceres-ebaf-4-2.json",
    "cmap-v1902.json",
    "era-5.json",
    "firecci-v5-1.json",
    "fluxnet2015-1-0.json",
    "gpcp-2-3.json",
    "gpcp-sg-2-3.json",
    "hadcrut5-0-2-0.json",
    "hadisst-1-1.json",
    "hwsd-2-0.json",
    "iap-1-2.json",
    "jra25.json",
    "lai4g-1-2.json",
    "lora-1-1.json",
    "noaa-ncei-lai-4-0.json",
    "noaa-ncei-lai-5-0.json",
    "tropflux-1-0.json",
    "wecann-1-0.json",
    "woa2023.json",
]

all_source = [str(p.stem) + ".json" for p in source_path.glob("*.json")]
source_to_remove = list(set(all_source) - set(necessary_source))
print(source_to_remove)
print(f"{len(all_source)}_{len(necessary_source)}_{len(source_to_remove)}")


for p in source_path.glob("*.json"):
    if str(p.stem) + ".json" in source_to_remove:
        p.unlink()
