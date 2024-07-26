const Sequencer = require('@jest/test-sequencer').default;

class AlphabeticalSequencer extends Sequencer {
  sort(tests) {
    // Sort test paths alphabetically
    return tests.sort((a, b) => (a.path > b.path ? 1 : -1));
  }
}

module.exports = AlphabeticalSequencer;