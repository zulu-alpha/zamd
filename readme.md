# Mod updater for Arma 3

Packaged to run in an Azure container instance in the same region as the file share to copy to.

## Configuration

### Environmental variables

* **MANIFEST_URL**: URL to raw JSON file describing mods (format: `{<Mod Line>: {<User friendly mod name>: <Steam Mod ID as string>, ...}, ...}`). Note that dependencies are automatically downloaded.
* **USERNAME**: Steam username that will be used to download mods. Not compatible with 2FA.
* **PASSWORD**: Steam password for the given username
* **STORAGE_ACCOUNT_NAME**: Azure storage account name. Ideally it should be in the same Azure region as this container is running in
* **STORAGE_ACCOUNT_KEY**: Key for the given Azure storage account name.
* **MODS_SHARE_NAME**: Name of the Azure shared directory that the mods will end up in.
* **KEYS_SHARE_NAME**: Name of the Azure shared directory that mod's keys will end up in.