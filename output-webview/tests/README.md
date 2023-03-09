# Testing structure

Tests are run with Robot Framework.

The basic infrastructure is that tests are first built to the `dist-test` folder
and then run with Robot Framework.

Tests are compiled with `yarn build-test`. 

-- the `webpack.config.js` contains the configuration needed to compile both 
sources along with the test files.

After tests are built, robotframework is used to open the browser in the
generated index and then makes the running using Playwright as needed.

