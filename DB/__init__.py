import os
from google.cloud import datastore

# export GOOGLE_APPLICATION_CREDENTIALS="assignment2-21973-f1f7c792ead9.json"
os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
#GOOGLE_APPLICATION_CREDENTIALS="..\assignment2-21973-f1f7c792ead9.json"
client = datastore.Client("prime-rainfall-340817") # os.getenv("DATASTORE_CLIENT")