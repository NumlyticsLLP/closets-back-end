const { raw } = require("mysql2");
const db = require("../config/db");
const axios = require("axios");

const { where, Op, fn, col, literal } = require("sequelize");

require('dotenv').config();
const Log = db.log;
const FormContent = db.formContent;

class PDFService {
    static async SaveFilter(reqBody) {
      console.log(reqBody);
        const [form, created] = await Log.upsert({ logid: reqBody.logId, jobid: reqBody.jobId, userid: reqBody.designerId, jsoncontent: JSON.stringify(reqBody) });

        if(created) {
          const count = parseInt(reqBody.closetsFormCount);
          for(let i=1;i<=count;i++) {
            const response = await FormContent.create({ userid: reqBody.designerId, jobid: reqBody.jobId + "-" + i });
            if(response) console.log("Form created successfully " + reqBody.jobId + "-" + i);
        }
      } else {
           await FormContent.update({ userid: reqBody.designerId }, { where: { jobid: { [Op.like]: reqBody.jobId+'%' }, isdeleted: false } });
        }
      return form;
    }
 
    static async GetAllJobID(userID, role) {
      if(role === "user") {
        const jobids = await Log.findAll({ attributes: ['jobid', [fn('JSON_UNQUOTE', fn('JSON_EXTRACT', col('jsoncontent'), literal("'$.clientName'"))),'clientName']], raw : true, order: [['logid', 'DESC']], where : { userId: userID } });
        return jobids;
      } else {
        const jobids = await Log.findAll({ attributes: ['jobid', [fn('JSON_UNQUOTE', fn('JSON_EXTRACT', col('jsoncontent'), literal("'$.clientName'"))),'clientName']], raw : true, order: [['logid', 'DESC']] });
        return jobids;
      }
    }

    static async GetJobDetailByID(jobID) {
      const jobDetails = await Log.findOne({ where: { jobid : jobID }, 
        attributes: ['jsoncontent', 'logid', 'templateid', 'submissionid', 'webhookresponse'
        ] });
      return jobDetails;
    }

    static async GetJobIDs(jobID) {
      const jobIds = await FormContent.findAll({ where: { jobid : { [Op.startsWith]: jobID }, isdeleted: false }, attributes: ['jobid', [fn('JSON_UNQUOTE', fn('JSON_EXTRACT', col('jsoncontent'), literal("'$.projectname'"))),'projectName'] ]});
      return jobIds;
    }

    static async updateJobIdContent(reqBody) {
      const jobIds = await FormContent.update({  jsoncontent: JSON.stringify(reqBody) }, { where: { jobid: reqBody.jobId, isdeleted: false } });
      return jobIds;
    }

    static async CheckIfJobContentExists(jobId) {
      const results = await FormContent.findAll({ where: { jobid: { [Op.like]: jobId+'%' }, jsoncontent: null, isdeleted: false } });
      return results;
    }

    static async UpdateParentJsonContent(reqBody) {
      const results = await Log.update({  jsoncontent: JSON.stringify(reqBody) }, { where: { jobid: reqBody.jobId } });
      return results;
    }

    static async GetChildJsonContent(jobId) {
      const results = await FormContent.findAll({ where: { jobid: { [Op.like]: jobId+'%' }, isdeleted: false } });
      return results;
    }

    static async GetChildJobDetailByID(jobID) {
      const jobDetails = await FormContent.findOne({ where: { jobid : jobID, isdeleted: false } });
      return jobDetails;
    }

     static async DeleteChildJobID(jobID) {
      const jobDetails = await FormContent.update({ isdeleted: true },{ where: { jobid : jobID } });
      if(jobDetails) {
        const parentJobId = jobID.split('-')[0];
        const parentJson = await Log.findAll({ where: { jobid: parentJobId }, attributes: ['jsoncontent'] });
        const count = JSON.parse(parentJson[0].jsoncontent).closetsFormCount;
        await Log.update({jsoncontent: fn('JSON_SET',col('jsoncontent'), literal("'$.closetsFormCount'"),count - 1)}, { where: { jobid: parentJobId } });
      }
      return jobDetails;
    }

    static async GetChildJobIdCount(jobId) {
      const jobDetails = await FormContent.count({ where: { jobid: { [Op.like]: jobId+'%' } } });
      return jobDetails;
    }


    static async UpdateSubmissionID(submissionId, templateId, jobId) {
      const results = await Log.update({ submissionid: submissionId, templateid: templateId }, { where: { jobid: jobId } });
      return results;
    }

static async UpdateWebHookResponse(webHookResponse) {
  let submissionId = null;

  if (webHookResponse?.data?.submission_id) {
    submissionId = webHookResponse.data.submission_id;
  } else if (webHookResponse?.data?.submission?.id) {
    submissionId = webHookResponse.data.submission.id;
  } else if (Array.isArray(webHookResponse?.data?.submitters) && webHookResponse.data.submitters.length > 0) {
    submissionId = webHookResponse.data.submitters[0].submission_id;
  }

  const templateId = webHookResponse?.data?.template?.id ?? null;

  if (!submissionId || !templateId) {
    console.error("⚠️ Could not extract submissionId or templateId from webhook:", JSON.stringify(webHookResponse));
    // Instead of throwing, you might want to still save it for debugging:
    return await Log.update(
      { webhookresponse: JSON.stringify(webHookResponse) },
      { where: { jobid: webHookResponse?.data?.job_id ?? null } } // fallback if jobid is in payload
    );
  }

  return await Log.update(
    { webhookresponse: JSON.stringify(webHookResponse) },
    { where: { templateid: templateId, submissionid: submissionId } }
  );
}

    //static async GetDesignerNameByJobId(jobId) {
    //  // Get the log entry for the given job ID
    //  const logEntry = await db.log.findOne({ where: { jobid: jobId } });
    //  if (!logEntry) {
    //    throw new Error("Log entry not found for jobId: " + jobId);
    //  }
    //
    //  // Get the user based on the userid from the log
    //  const user = await db.user.findOne({ where: { userid: logEntry.userid } });
    //  if (!user) {
    //    throw new Error("User not found for userid: " + logEntry.userid);
    //  }
    //
    //  return user.designername;
    //}

    static async GetDesignerNameByJobId(jobId) {
  console.log("GetDesignerNameByJobId called with jobId:", jobId);

  // Get the log entry for the given job ID
  const logEntry = await db.log.findOne({ where: { jobid: jobId } });
  console.log("Fetched logEntry:", logEntry);

  if (!logEntry) {
    console.error("Log entry not found for jobId:", jobId);
    throw new Error("Log entry not found for jobId: " + jobId);
  }

  // Get the user based on the userid from the log
const parsed = JSON.parse(logEntry.jsoncontent);

const user = await db.user.findOne({ 
  where: { userid: parsed.designerId } 
});

console.log("Fetched user:", user);

if (!user) {
  console.error("User not found for userid:", parsed.designerId);
  throw new Error("User not found for userid: " + parsed.designerId);
}

  console.log("Returning designer name:", user.designername);
  return user.designername;
}



}

module.exports = PDFService;
