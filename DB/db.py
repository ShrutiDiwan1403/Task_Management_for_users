import os
from google.cloud import datastore


os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
client = datastore.Client("alien-grove-346709")  # os.getenv("DATASTORE_CLIENT")