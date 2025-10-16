const express = require('express');
const hbs = require('express-handlebars');
const loginRoutes = require('./routes/login');
const pdfRoutes = require('./routes/pdf');
const azureBlb = require('./routes/azureblb');
const path = require('path');
const cors = require("cors");
require('dotenv').config();
const swaggerUI = require('swagger-ui-express');
const swaggerSpec = require('./swagger');
const swaggerjsonFilePath = require("./swagger.json");

const app =  express();

if (!process.env.PORT) {
    console.error('Error: PORT environment variable is not defined.');
    process.exit(1);
  }
  const PORT = process.env.PORT;
//const HOST = process.env.HOST || '0.0.0.0';
//const PORT = process.env.PORT || 3001;
//const PORT = 3001;

app.use(cors());

 // Serve Swagger documentation


app.engine('handlebars', hbs.engine());

//to use for images in generate pdf
app.use('/temp', express.static('temp'));

app.set('views', path.join(__dirname, 'views'));

// parse requests of content-type - application/json
//app.use(express.json());

// parse requests of content-type - application/x-www-form-urlencoded
//app.use(express.urlencoded({ extended: true }));


app.use(express.json({ limit: "26mb" })); // default is only ~1mb
app.use(express.urlencoded({ limit: "26mb", extended: true }));
 

app.use('/api/user', loginRoutes);
app.use('/api/pdf', pdfRoutes);
app.use('/api/azureblb', azureBlb);
app.use('/api-docs', swaggerUI.serve, swaggerUI.setup(swaggerjsonFilePath));

app.get('/', (req, res) => {
    res.send('Welcome to my Node.js application!');
});

app.listen(PORT, () => {
    console.log(`Server running on PORT:${PORT}`)
});

//for testing locally on mobile
//app.listen(PORT,  '0.0.0.0', () => {
//    console.log(`Server running on PORT:${PORT}`)
//});

process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
  });
  
  process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection:', reason);
  });
  