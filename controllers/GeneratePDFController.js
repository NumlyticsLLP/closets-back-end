const PDFService = require('../services/PDFService');
const DocuSealService = require('../services/DocuSealService');

class GeneratePDFController {
    /*
    static async GeneratePDF(req,res) {
        const htmlPDF = new PuppeteerHTMLPDF();

        htmlPDF.setOptions({ format: "A4", headless: true });
        const templateHtml = await htmlPDF.readFile(path.join(process.cwd() + "/views/agreement.html"), "utf8");

        var template = handlebars.compile(templateHtml);
        const data = {
            job_id: req.body.jobId,
            client_name: req.body.clientName
        };
        var html = template(data);
        // try {
        //     const pdfBuffer = await htmlPDF.create(html);
        //     const filePath = `./../temp/sample.pdf`;
        //     const file = await htmlPDF.writeFile(pdfBuffer, filePath);
        //     //res.send("https://research.google.com/pubs/archive/44678.pdf");
            

        //   } catch (error) {
        //     console.log("PuppeteerHTMLPDF error", error);
        //   }
        //res.send("https://research.google.com/pubs/archive/44678.pdf");
        return res.send(html);
      
    }
    */

    static async SaveFilter(req,res) {
        const body = req.body;
        const result = await PDFService.SaveFilter(body);
        res.send(result);
    }
 
    static async GetAllJobId(req, res) {
        const userId = req.query.userid;
        const role = req.query.role;
        const result = await PDFService.GetAllJobID(userId, role);
        res.send(result);
    }

    static async GetJobDetailById(req, res) {
        const result = await PDFService.GetJobDetailByID(req.query.jobid);
        res.send(result);
    }


    static async GetJobIds(req, res) {
        const result = await PDFService.GetJobIDs(req.query.jobid);
        res.send(result);
    }

    static async UpdateJobIdContent(req, res) {
        const result = await PDFService.updateJobIdContent(req.body);
        res.send(result);
    }

    static async CheckIfJobContentExists(req, res) {
        const result = await PDFService.CheckIfJobContentExists(req.query.jobid);
        res.send(result);
    }

    static async UpdateParentJsonContent(req, res) {
        const result = await PDFService.UpdateParentJsonContent(req.body);
        res.send(result);
    }

    static async GetChildJsonContent(req, res) {
        const result = await PDFService.GetChildJsonContent(req.query.jobid);
        res.send(result);
    }

    static async GetChildJobDetailById(req, res) {
        const result = await PDFService.GetChildJobDetailByID(req.query.jobid);
        res.send(result);
    }

    static async DeleteChildJobID(req, res) {
        const result = await PDFService.DeleteChildJobID(req.query.jobid);
        res.send(result);
    }

    static async DocusealWebHookResponse(req, res) {
        const result = await PDFService.UpdateWebHookResponse(req.body);
        return res.sendStatus(200);
    }

static async GetDesignerByJobId(req, res) {
  try {
    const { jobid } = req.query;

    const designer = await PDFService.GetDesignerByJobId(jobid);

    res.json({ designer });
  } catch (err) {
    console.error("Error fetching designer:", err.message);
    res.status(500).json({ error: err.message });
  }
}
    
}

module.exports = GeneratePDFController
