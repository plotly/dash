window.tested = ['load_first'];
var ramdaTest = document.getElementById('ramda-test');
if (ramdaTest) {
    ramdaTest.innerHTML = R.join(' ', R.concat(['hello'], ['world']).map(function(x) {
        return _.capitalize(x);
    }));
}
