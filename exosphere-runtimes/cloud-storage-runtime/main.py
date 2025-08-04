from dotenv import load_dotenv
from exospherehost import Runtime
from nodes.list_s3_files import ListS3FilesNode

# Load environment variables from .env file
# EXOSPHERE_STATE_MANAGER_URI is the URI of the state manager
# EXOSPHERE_API_KEY is the key of the runtime
load_dotenv()

Runtime(
    name="cloud-storage-runtime",
    namespace="exospherehost",
    nodes=[ListS3FilesNode]
).start()