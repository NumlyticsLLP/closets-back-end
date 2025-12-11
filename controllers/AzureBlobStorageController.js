const AzureBlobStorageService = require('../services/AzureBlobStorageService');

class AzureBlobStorageController {

    static async CreateStoreAccessPolicy(req, res) {
        try {
            await AzureBlobStorageService.CreateStoreagePolicy();
            res.status(200).send("Store access policy applied!");
        } catch (error) {
            res.status(500).send("Unable to create store access policy!");
        }
    }

    static async GenerateAzureBlobStorageToken(req, res) {
        try {
            const token = await AzureBlobStorageService.GenerateSASToken(req, res);
            res.status(200).send(token);
        } catch (error) {
            res.status(500).send(error.message);
        }
    }
}

module.exports = AzureBlobStorageController;