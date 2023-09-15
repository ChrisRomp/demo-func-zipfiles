## demo-func-zipfiles

This Azure function demonstrates monitoring a blob store for new zip files, and will unzip them to a folder with the same name.

Expected configuration settings:

| Setting Name | Type | Description |
| - | - | - |
| `STORAGE_CONNECTION` | string | Connection string to the storage account. |
| `STORAGE_CONTAINER` | string | The container to monitor. |
| `UPLOAD_FOLDER` | string | The folder to monitor for new zip files. |
