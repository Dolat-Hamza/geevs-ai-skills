// Quality limits from QUALITY.md section 2. Spread into the project's flat config.
import sonarjs from "eslint-plugin-sonarjs";

export default [
  {
    plugins: { sonarjs },
    rules: {
      "sonarjs/cognitive-complexity": ["error", 15],
      complexity: ["error", 10],
      "max-lines-per-function": ["error", { max: 30, skipBlankLines: true, skipComments: true }],
      "max-lines": ["error", { max: 400, skipBlankLines: true, skipComments: true }],
      "max-depth": ["error", 3],
      "max-params": ["error", 4],
      "no-warning-comments": ["warn", { terms: ["todo", "fixme"], location: "start" }],
    },
  },
];
