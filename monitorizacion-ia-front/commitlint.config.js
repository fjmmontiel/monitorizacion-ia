const path = require('path');

const glob = require('glob');

const PACKAGE_JSON = 'package.json';

const getPackages = context => {
  return Promise.resolve()
    .then(() => {
      const ctx = context || {};
      const cwd = ctx.cwd || process.cwd();

      const { workspaces } = require(path.join(cwd, PACKAGE_JSON));
      const wsGlobs = workspaces.flatMap(ws => {
        const packagePath = path.posix.join(ws, PACKAGE_JSON);
        return glob.sync(packagePath, { cwd, ignore: ['**/node_modules/**'] });
      });

      return wsGlobs.map(pJson => require(path.join(cwd, pJson)));
    })
    .then(packages => {
      return packages
        .map(pkg => pkg.name)
        .filter(Boolean)
        .map(name => (name.charAt(0) === '@' ? name.split('/')[1] : name));
    });
};

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'scope-enum': async ctx => {
      const packages = await getPackages(ctx);
      return [2, 'always', ['*', ...packages]];
    },
    'scope-empty': [2, 'never'],
    'header-max-length': [2, 'always', 150],
    'header-match-devops-pattern': [2, 'always'],
  },
  parserPreset: {
    parserOpts: {
      headerPattern: /^(?:([\S]*))?:*\s{0,1}(\w*)(?:\((.*)\))?: (.*)$/,
      headerCorrespondence: ['ticket', 'type', 'scope', 'subject'],
    },
  },
  plugins: [
    {
      rules: {
        'header-match-devops-pattern': parsed => {
          const { ticket } = parsed;

          const ticketRegex = /^\[[A-Z][A-Z_0-9]+-[0-9]+\]$/;
          const ticketMatch = ticketRegex.test(ticket);

          if (ticket === null || !ticketMatch) {
            return [
              false,
              "JIRA-ID must be informed in the start of message with format: '[JIRA_ID] type(scope): description'",
            ];
          }
          return [true, ''];
        },
      },
    },
  ],
};
