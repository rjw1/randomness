
var Preview = {};
Preview.keyPressHandler = function(e) {
  var previewPane = document.getElementById("preview");
  var html = Wiky.toHtml(this.value);
  previewPane.innerHTML = html;
};

Preview.onLoadHandler = function(e) {
  var elem = document.getElementById("toPreview");
  if (!elem) throw new Error("could not find text area");
  elem.addEventListener("keyup", Preview.keyPressHandler, true );
};

window.addEventListener('load', Preview.onLoadHandler, true );