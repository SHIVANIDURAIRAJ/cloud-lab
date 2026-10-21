import dropbox
TOKEN = "your_dropbox_access_token"  # Replace with your Dropbox access token
dbx = dropbox.Dropbox(TOKEN)
with open("sample.txt", "rb") as f:
    dbx.files_upload(
        f.read(),
        "/sample.txt",
        mode=dropbox.files.WriteMode.overwrite
    )
print("File uploaded successfully to Dropbox!")
