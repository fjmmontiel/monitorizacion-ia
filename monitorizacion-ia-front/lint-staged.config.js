const micromatch = require('micromatch');
module.exports = {
  '*.{js,jsx,ts,tsx}': allFiles => {
    const sourceFolderFiles = micromatch(allFiles, ['**/src/**/*.{js,jsx,ts,tsx}']);
    return [`eslint --fix -- -- ${sourceFolderFiles.join(' ')}`];
  },
};
