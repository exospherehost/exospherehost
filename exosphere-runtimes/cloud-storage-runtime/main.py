from dotenv import load_dotenv
from exospherehost import Runtime
from nodes.list_s3_files import ListS3FilesNode
from nodes.download_s3_file import DownloadS3FileNode

# Load environment variables from .env file
# EXOSPHERE_STATE_MANAGER_URI is the URI of the state manager
# EXOSPHERE_API_KEY is the key of the runtime
load_dotenv()

# Note on node ordering:
# The order of node classes in the `nodes` list does not define execution sequence.
# Nodes are registered with the state manager; orchestration and dependencies are handled externally.
# `ListS3FilesNode` is listed before `DownloadS3FileNode` for readability only.
Runtime(
    name="cloud-storage-runtime",
    namespace="exospherehost",
    nodes=[ListS3FilesNode, DownloadS3FileNode]
).start()