const {
  BlobServiceClient,
  generateBlobSASQueryParameters,
  ContainerSASPermissions,
  StorageSharedKeyCredential,
} = require("@azure/storage-blob");

require("dotenv").config();

const blobStorageAccountName = process.env.BLOB_STORAGE_ACCOUNT_NAME;
const blobStorageAccountKey = process.env.BLOB_STORAGE_ACCOUNT_KEY;
const urlExpiryDay = process.env.URL_EXPIRY_DAY;
const blobStorageURL = process.env.BLOB_STORAGE_URL;
const blobContainerName = process.env.BLOB_CONTAINER_NAME;
const blobContainerUniquePolicyName = process.env.BLOB_CONTAINER_UNIQUE_POLICY_NAME;

class AzureBlobStorageService {

  //Below method call once at the time of creating the container and apply the policy
  static async CreateStoreagePolicy() {
    try {
      // Create credentials
      const sharedKeyCredential = new StorageSharedKeyCredential(
        blobStorageAccountName,
        blobStorageAccountKey
      );

      const blobServiceClient = new BlobServiceClient(
        `https://${blobStorageAccountName}.blob.core.windows.net`,
        sharedKeyCredential
      );

      const containerClient = blobServiceClient.getContainerClient(blobContainerName);

      const now = new Date();
      const startsOn = new Date(now.valueOf() - 5 * 60 * 1000); // 5 mins earlier
      const expiresOn = new Date(now.valueOf() + urlExpiryDay * 24 * 60 * 60 * 1000); // 90 days

      const uniqueName = atob(blobContainerUniquePolicyName);
      // Define access policy
      const signedIdentifiers = [
        {
          id: uniqueName, // policy name (must be unique in this container)
          accessPolicy: {
            startsOn,
            expiresOn,
            permissions: ContainerSASPermissions.parse("racw").toString(), // read + write
          },
        },
      ];

      // Apply the policy
      await containerClient.setAccessPolicy(undefined, signedIdentifiers);
      console.log("✅ Stored Access Policy 'mypolicy90days' created for container:", blobContainerName);
    }
    catch (error) {
      console.log("Unable to generate stored access policy", error.message);
    }
  }

  static async GenerateSASToken() {
    try {
      // Create credentials
      const sharedKeyCredential = new StorageSharedKeyCredential(
        blobStorageAccountName,
        blobStorageAccountKey
      );

      const containerName = blobContainerName;
      const uniqueName = atob(blobContainerUniquePolicyName);
      //Setting SAS Token Option
      const sasOptions = {
        containerName,
        identifier: uniqueName
      };

      //Generating token for URL
      const sasToken = generateBlobSASQueryParameters(
        sasOptions,
        sharedKeyCredential
      ).toString();

      const sasUrl = `https://${blobStorageAccountName}.blob.core.windows.net/${containerName}?${sasToken}`;
      return sasUrl;
    } catch (error) {
      throw new Error("Unable to generate a SAS Token", error.message);
    }
  }
}

module.exports = AzureBlobStorageService;