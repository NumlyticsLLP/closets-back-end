const { Sequelize } = require('sequelize');
require('dotenv').config();

const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASS, {
  host: process.env.DB_HOST,
  dialect: 'mysql',
  dialectModule: require('mysql2'),
  dialectOptions: {
    ssl: {
      rejectUnauthorized: false,  // Allows Azure SSL without CA file
    }
  },
  logging: false,
});

const db = {};
db.Sequelize = Sequelize;
db.sequelize = sequelize;

db.user = require('../model/User')(sequelize, Sequelize);
db.log = require('../model/Log')(sequelize, Sequelize);
db.formContent = require('../model/FormContent')(sequelize, Sequelize);

module.exports = db;
