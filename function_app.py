import azure.functions as func
from azure.storage.blob import BlobServiceClient
import logging
import os
import zipfile
import shutil

app = func.FunctionApp()

storage_container = os.environ["STORAGE_CONTAINER"]
upload_folder = os.environ["UPLOAD_FOLDER"]
monitor_path = f"{storage_container}/{upload_folder}/{{zip_file}}.zip"

logging.info(f"Monitoring: {monitor_path}")

@app.blob_trigger(arg_name="myblob", path=monitor_path, connection="STORAGE_CONNECTION")
def new_blob_trigger(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    # Create a blob storage client
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["STORAGE_CONNECTION"])

    # Some strings
    blob_filename = myblob.name.replace(f"{storage_container}/{upload_folder}/", "")
    blob_foldername = blob_filename.lower().replace(".zip", "")

    # Download myblob
    blob_client = blob_service_client.get_blob_client(container=storage_container, blob=f"{upload_folder}/{blob_filename}")
    download_stream = blob_client.download_blob()
    with open(f"/tmp/{blob_filename}", "wb") as my_blob:
        my_blob.write(download_stream.readall())

    # Unzip the file
    with zipfile.ZipFile(f"/tmp/{blob_filename}", "r") as zip_ref:
        zip_ref.extractall(f"/tmp/{blob_foldername}")

    # Upload the unzipped files to the "unzipped" container
    container_client = blob_service_client.get_container_client(storage_container)
    for file in os.listdir(f"/tmp/{blob_foldername}"):
        with open(f"/tmp/{blob_foldername}/{file}", "rb") as data:
            upload_filename = f"{blob_foldername}/{file}"
            container_client.upload_blob(name=upload_filename, data=data)

    # Delete the original zip file
    blob_client.delete_blob()

    # Clean up local files
    os.remove(f"/tmp/{blob_filename}")
    shutil.rmtree(f"/tmp/{blob_foldername}")
