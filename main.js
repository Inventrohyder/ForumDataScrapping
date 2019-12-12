const {Builder, By, Key, until} = require('selenium-webdriver');

class Scrapper {
    driver;
    credentialsFile;

    constructor(baseUrl, browser = 'safari', credentialsFile = '.credentials.json') {
        this.credentialsFile = credentialsFile;
        console.log('Opening Browser');
        this.driver = new Builder().forBrowser(browser).build();
        console.log('Navigating to', baseUrl);
        this.driver.get(baseUrl);
    }

    login_info() {
        const fs = require('fs');
        const credentialsFile = this.credentialsFile;

        fs.readFile(credentialsFile, (err, jsonString) => {
            if (err) {
                console.warn("Error reading file from disk");

                console.info('Getting user info');

                const properties = [
                    {
                        name: 'email',
                        validator: /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@minerva.kgi.edu$/,
                        warning: 'Email must be of the domain: minerva.kgi.edu'
                    },
                    {
                        name: 'password',
                        hidden: true
                    }
                ];

                const prompt = require('prompt');

                // Start the prompt
                prompt.start();

                // Get two properties from the user: email, password
                prompt.get(properties, function (err, result) {
                    if (err) {
                        console.warn(err);
                        return 1;
                    }
                    console.log('Command-line input received:');
                    console.log('  Email: ' + result.email);
                    console.log('  Password: ' + result.password);

                    const user = {
                        email: result.email,
                        password: result.password
                    };

                    const jsonString = JSON.stringify(user);

                    fs.writeFile(credentialsFile, jsonString, err => {
                        if (err) {
                            console.error('Error writing file', err)
                        } else {
                            console.log('Successfully wrote file')
                        }
                    });
                });
            }
            try {
                const user = JSON.parse(jsonString);
            } catch (SyntaxError) {
                // Do nothing if it is a Syntax Error, the file doesn't exist yet
            }

        });
    }
}

class ForumScrapper extends Scrapper {
    constructor() {
        super('https://seminar.minerva.kgi.edu');
        console.log('Logging you in');
        this.login();
    }

    login() {
        this.login_info();
    }
}


// (async function example() {
//     let driver = await new Builder().forBrowser('safari').build();
//     try {
//         await driver.get('http://www.google.com/ncr');
//         await driver.findElement(By.name('q')).sendKeys('webdriver', Key.RETURN);
//         await driver.wait(until.titleIs('webdriver - Google Search'), 1000);
//     } finally {
//         await driver.quit();
//     }
// })();


scrapper = new ForumScrapper('https://seminar.minerva.kgi.edu');
