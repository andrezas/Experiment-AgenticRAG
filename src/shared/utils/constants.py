from pathlib import Path

# PATHS
ROOT_PATH = Path(__file__).resolve().parents[3]

# ROOT
RESOURCE_PATH = ROOT_PATH.joinpath("./resources")

MB = 1024 * 1024
DEFAULT_MULTIPART_CHUNK_SIZE = 50 * MB
DEFAULT_READ_CHUNK_SIZE = 8 * MB
