#!/usr/bin/env node
// `npm i less nodewatch` needed in order to run this

var exec = require('child_process').exec;
var path = require('path');
var less = require('less');
var nodewatch = require('nodewatch');

var watch = path.join(__dirname, '..', 'themes', 'odi', 'static', 'less');

function compile (input, info) {
  var start = Date.now();
  var output = input.replace(/less/g, 'css');
  exec('`npm bin`/lessc '+input+' > '+output, function (err, stdout, stderr) {
    if (err) {
      console.log('An error occurred running the less command:');
      console.log(err.message);
    } else if (stderr || stdout) {
      console.log(stdout, stderr);
    } else {
      var duration = Date.now() - start;
      var file = input.replace(watch, '').substr(1);
      console.log('[%s] recompiled %s in %sms', Date.now(), file, duration);
    }
  });
}

console.log('Watching %s', watch);
nodewatch.add(watch).onChange(compile);
