const fs = require('fs');

(() => {
  const buildId = 'ver.app.' + Date.now().toString();

  fs.writeFileSync(__dirname + '/version', buildId);
})();
