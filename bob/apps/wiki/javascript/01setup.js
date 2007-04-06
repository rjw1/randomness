// Create the classes we need if they don't already exist.
['Page'].forEach(function(c) {
  if (!this[c]) zimki.persist.create(c);
});
