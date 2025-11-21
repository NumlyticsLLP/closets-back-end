const express = require('express');
const AzureBlobStorageController = require('../controllers/AzureBlobStorageController');

const routes = express.Router();

/** get: http://localhost:3001/api/azureblb 
 */
routes.get('/createsap',(req,res) => {
    AzureBlobStorageController.CreateStoreAccessPolicy(req, res);
});

/** get: http://localhost:3001/api/azureblb 
 */
routes.get('/sastoken',(req,res) => {
    AzureBlobStorageController.GenerateAzureBlobStorageToken(req, res);
});

module.exports = routes;