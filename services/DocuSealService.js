const axios = require("axios");
require('dotenv').config();

const DOCUSEAL_API = process.env.DOCUSEAM_API_ENDPOINT;
const DOCUSEAL_KEY = process.env.DOCUSEAL_API_KEY;

class DocuSealService {
    
  static async UploadTemplateToDocuSeal(documents) {
    const response = await axios.post(
      `${DOCUSEAL_API}/templates/pdf`,
      documents,
      {
        headers: {
          "X-Auth-Token": DOCUSEAL_KEY,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      }
    );
    return response;
  }

  static async SendRequestForSignDocument(signRequest) {
  console.log("📦 Payload being sent to DocuSeal:", JSON.stringify(signRequest, null, 2));

  const response = await axios.post(
    `${DOCUSEAL_API}/submissions`,
    signRequest,
    {
      headers: {
        "X-Auth-Token": DOCUSEAL_KEY,
        "Content-Type": "application/json",
      },
    }
  );
  return response;
}

  static async AlreadyCreatePDFOrNot(pdfId) {
    const response = await axios.post(
      `${DOCUSEAL_API}/submitters/${pdfId}`,
      signRequest,
      {
        headers: {
          "X-Auth-Token": DOCUSEAL_KEY,
          "Content-Type": "application/json",
        },
      }
    );
    return response;
  }

  static async UpdateTemplate(template) {
  const response = await axios.post(
    `${DOCUSEAL_API}/templates/pdf`,
    template,
    {
      headers: {
        "X-Auth-Token": DOCUSEAL_KEY,
        "Content-Type": "application/json",
      },
    }
  );
  return response;
}
  
};

module.exports = DocuSealService;
