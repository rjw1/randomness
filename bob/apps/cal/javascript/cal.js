zimki.library.require('library','trimpath.js');

function calendar(){
var data = {};
data.entry = cal.search({});
return zimki.render.trimpath('cal.html', data );
}
zimki.publishPath("/", calendar);
