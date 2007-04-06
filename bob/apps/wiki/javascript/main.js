zimki.library.require('library', 'wiky.js');     // wiki markup language
zimki.library.require('library', 'trimpath.js'); // server-side templating


function wiki(args, path, match) {
  
  var pagename = match[0] || 'HomePage'; // a default page name

  // get the page object
  var page = getPage( pagename, args.revision );

  if (args.history) {
    var pages = Page.search({ name:pagename }, { order_by:'revision:numeric' });
    return zimki.render.trimpath('history.html', { name:pagename, pages:pages });

  } else if (args.save) {
    page = savePage( pagename, args.content );

  } else if (args.edit || !page) {
    // either editing an existing page, or creating a new one.
    return zimki.render.trimpath('edit.html', { name:pagename, page:page });

  }

  return zimki.render.trimpath('page.html', { page:page });

}

Page.prototype.html = function() {
  return Wiky.toHtml( this.content );

}

zimki.publishPath('all.html', function() {
  var pages = {};
  var all = Page.search();
  for (p in all) {
    if (!pages[ all[p] ] || all[p].creation_date > pages[ all[p] ])
      pages[ all[p].name ] = all[p];
  }
  return zimki.render.trimpath('all.html', { pages:pages });
});

zimki.publishPath('login.html', login);

function login() {
return zimki.render.trimpath('login.html');
}
// a simple login function
function runLogin( args ) {
  zimki.session.login( args.username, args.password );
  return zimki.redirect(zimki.root + "/");
}
zimki.publishPath('/login', runLogin );


zimki.publishPath(/(\w*)/, wiki);


function savePage( name, content ) {

  var pages = Page.search({ name:name }, { order_by:'-revision:numeric' });

  // the next revision is the higest revision so far plus 1, or 1.
  var revision = pages[0] ? pages[0].revision + 1 : 1;
  revision = parseInt( revision ) || 1; // sanity

  data = { name:name, content:content, revision:revision };
  
  if (this['new_page_timeout'])
    data.expires = zimki.sprintf("+%dm", this['new_page_timeout']);

  return Page.create(data);

}

function getPage( name, revision ) {
  if (revision) {
    return Page.get({ name:name, revision:revision });
  }
  var pages = Page.search({ name:name }, { order_by:'-revision:numeric' });
  return pages[0];
}


