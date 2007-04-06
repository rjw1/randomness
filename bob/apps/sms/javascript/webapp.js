// define a function for handling the index page of our webapp
function handleIndex(args) {
  var tmplArgs = {
    date: new Date(),   // Date string to display
    root: zimki.root    // Our Zimki root directory
  };
  
  return zimki.render.tal('index.tal', tmplArgs );
}

// publish our function at '/'
zimki.publishPath('/', handleIndex);

