/*
 * Faux server data until we get the backend going.
 */
var gSuggestedTags = {trustworthy: {popularity: 9},
                      dependable: {popularity: 6},
                      creative: {popularity: 2},
                      proactive: {popularity: 5},
                      altruistic: {popularity: 7}};

var gGivenTags = {trustworthy: {strength: 5},
                  proactive: {strength: 9},
                  altruistic: {strength: 1},
                  custom: {strength: 9}};

// Converts from a numerical weight to a font size as a percentage.
var gFontSizes = {1: '50%',
                  2: '63%',
                  3: '75%',
                  4: '88%',
                  5: '100%',
                  6: '125%',
                  7: '150%',
                  8: '175%',
                  9: '200%'};

// Checks if a confidence value is valid
function isValidConfidence(val) {
    return (val >= 1) &&
           (val <= 9) &&
           (val % 2 == 1);
}

// Converts from weights to descriptions of weights
function getConfidenceDescription(person, tag, confidence) {

  // Make the tag green
  tag = '<span style="color:green">' + tag + '</span>';

  // Give the appropriate message
  if (confidence == 1)
    return 'I guess you could say that ' + person + ' is ' + tag + '...';
  if (confidence == 3)
    return person + ' seems ' + tag + '.';
  if (confidence == 5)
    return person + ' is ' + tag + '.';
  if (confidence == 7)
    return person + ' is definitely ' + tag + '.';
  if (confidence == 9)
    return person + ' is one of the most ' + tag + ' people I know.';

  // Not reached
  console.assert(0);
}

/*
 * Tag container.
 */
function Tag(name, weight, type) {
  this.name = name;
  this.weight = weight;
  this.type = type;

  // Differences between given tags and suggested tags
  var fontSize = gFontSizes[(type == 'given') ? this.weight : 5];
  var spacer = (type == 'given') ? ' ' : '<br>';

  // Make our DOM element
  this.elem = $('<span></span>').addClass('tag')
                                .addClass(this.type)
                                .addClass('hiddentag')
                                .css('font-size', fontSize)
                                .draggable({revert: true,
                                            revertDuration: 200})
                                .prop('tagname', this.name)
                                .html(this.name + spacer);

  // If it's a given tag, link it to the slider
  if (this.type == 'given')
    this.elem.hover(givenOver, givenLeave);

  // Insert it
  $('#' + this.type + 'tags').append(this.elem);
}

Tag.prototype.setDisplayed = function(display) {

  // Our class indicator is the opposite of display, unfortunately.
  var hide = !display;

  // No-op if we're already in the right state
  if (this.elem.hasClass('hiddentag') == hide)
    return;

  // Toggle
  this.elem.toggleClass('hiddentag');
}

Tag.prototype.setWeight = function(weight) {
  this.weight = weight;
  var fontSize = gFontSizes[(this.type == 'given') ? this.weight : 5];
  this.elem.css('font-size', fontSize);
}

var gTags = {

  // Reloads the suggested tags from the server
  loadSuggested: function() {

    // Clear the old suggestions
    this.suggested = {};

    // TODO - Load JSON
    for (var name in gSuggestedTags)
      this.suggested[name] = new Tag(name,
                                     gSuggestedTags[name].popularity,
                                     'suggested');

    // Sort
    this.sortSuggested();
  },

  // Loads the current given tags from the server
  loadGiven: function() {

    // TODO - Load JSON
    for (var name in gGivenTags)
      this.given[name] = new Tag(name,
                                 gGivenTags[name].strength,
                                 'given');

    // Sort
    this.sortGiven();
  },

  // sorts the suggested tags by popularity
  sortSuggested: function() {
    $('.suggested').sortElements(function(a,b) {
      return -cmp(gTags.suggested[a.tagname].weight,
                  gTags.suggested[b.tagname].weight)
    });
  },

  // sorts the given tags alphabetically
  sortGiven: function() {
    $('.given').sortElements(function(a,b) {
      return cmp(a.tagname, b.tagname);
    });
  },

  // Iterates over all tags, displaying or hiding them as appropriate
  refreshDisplay: function() {

    // Display all non-given suggestions
    for (name in this.suggested) {
      if (name in this.given)
        this.suggested[name].setDisplayed(false);
      else
        this.suggested[name].setDisplayed(true);
     }

    // Display all givens
    for (name in this.given)
      this.given[name].setDisplayed(true);
  },

  // Add suggestions. They are not, by default, displayed.
  addSuggested: function(name, popularity) {

    // If the suggestion already exists, punt
    if (name in this.suggested)
      return;

    // Add the tag
    this.suggested[name] = new Tag(name, popularity, 'suggested');

    // Sort
    this.sortSuggested();
  },

  // Add givens
  addGiven: function(name) {

    // If we already have the tag, bail.
    if (name in this.given)
      return;

    // Add the tag
    this.given[name] = new Tag(name, 5, 'given');

    // Display it
    this.given[name].setDisplayed(true);

    // If this was a suggested tag, hide the suggestion
    if (name in this.suggested)
      this.suggested[name].setDisplayed(false);

    // Sort
    this.sortGiven();

    // Mark us as dirty
    this.givenDirty = true;
  },

  // Remove givens
  removeGiven: function(name) {

    // We shouldn't be able to remove a non-existent given.
    console.assert(this.given[name] !== undefined);

    // If we're removing a custom tag, make it a suggestion for the rest
    // of the session.
    this.addSuggested(name, this.given[name].weight);

    // Stop displaying it
    this.given[name].setDisplayed(false);

    // Remove it from the list
    delete this.given[name];

    // Display the suggestion
    this.suggested[name].setDisplayed(true);

    // Mark us as dirty
    this.givenDirty = true;
  },

  /*
   * Member variables.
   */

  // Suggested tags, indexed by name
  suggested: {},

  // Given tags, indexed by name
  given: {},

  // Have we modified the given tags since last sync?
  givenDirty: false
};

/*
 * Singleton mouseover popup menu handling code.
 *
 * This object functions on an addref/release mechanism. An element addrefs it
 * when it needs the popup, and releases it when it's done.
 *
 * Addrefs happen on tag mouseover, and also on mouseover of the popup menu
 * itself. If the menu overlaps another tag, there could potentially be another
 * element trying to addref the popup before the previous one is done. To handle
 * this, addref and release both take an 'owner tag' parameter that refers to the
 * tag currently using the service. If the service is in use and the owner
 * parameter doesn't match, the request is ignored.
 */
var gPopup = {

  // One-time initialization routine
  init: function() {

    // Initialize the slider
    $('#popup-slider').slider({
      min: 1,
      max: 9,
      step: 2,
      animate: true,
      slide: function(event, ui) {gPopup.setConfidence(ui.value); }
    });

    // Set up the hover handler of the popup
    $('#popup').hover(function(eobj) {
      if (gPopup.owner)
        gPopup.addref(gPopup.owner);
    }, function(eobj) {
      if (gPopup.owner)
        gPopup.release(gPopup.owner);
    });
  },

  // Set confidence for the current owner
  setConfidence: function(confidence) {

    // We should have an owner
    console.assert(this.owner);

    // The weight should be valid
    console.assert(isValidConfidence(confidence));

    // Update the UI
    var desc = getConfidenceDescription('Ellery', this.owner.name, confidence);
    $('#popup-text').html(desc);
    $('#popup-slider').slider('option', 'animate', false)
                      .slider('value', confidence)
                      .slider('option', 'animate', true);

    // Update the owner tag
    this.owner.setWeight(confidence);
  },

  // Signal use of the pane
  addref: function(owner) {

    // If we're in use by someone else, reject
    if (this.owner && this.owner != owner)
      return;

    // If there's a timeout waiting to make us ownerless, kill it
    if (this.timeoutID) {
      window.clearTimeout(this.timeoutID);
      this.timeoutID = null;
      console.assert(this.owner);
    }

    // If the popup is unowned, take ownership
    if (!this.owner) {
      this.owner = owner;
      this.display();
    }

    // Increment the refcount
    this.refcnt++;
  },

  // Release use of the pane
  release: function(owner) {

    // If we're in use by someone else, reject
    if (this.owner && this.owner != owner)
      return;

    // It might be possible for the addref to come when the service
    // is owned by someone else, but for that to go away by the time
    // of the release. If so, just discard the release.
    if (this.refcnt == 0) {
      console.assert(!this.owner);
      return;
    }

    // Decrement the refcount
    this.refcnt--;

    // If the refcount is zero, we go into the chopping block, but can still
    // be rescued.
    this.timeoutID = window.setTimeout('gPopup.timeoutCallback();', 500);
  },

  // Callback giving us some breathing room between the final release and the
  // moment when the popup goes back on the market.
  timeoutCallback: function() {

    // If the timeout wasn't canceled, the refcount should be zero
    console.assert(this.refcnt == 0);

    // Clean up after ourselves
    this.timeoutID = null;

    // Make us ownerless
    this.owner = null;

    // Hide the panel
    this.hide();
  },

  // Show the pane for a tag
  display: function() {

    // We should have an owner
    console.assert(this.owner);

    // Initialize the slider to the current weight
    this.setConfidence(this.owner.weight);

    // Move the slider to the offset of the tag
    var pos = this.owner.elem.offset();
    pos.top = pos.top + this.owner.elem.innerHeight();
    pos.left -= $('#popup').innerWidth() / 4;
    $('#popup').css(pos);

    // Make visible
    $('#popup').css('display', 'block');
  },

  // Hide the pane
  hide: function() {

    // Just set it to display:none
    $('#popup').css('display', 'none');
  },

  /*
   * Member variables.
   */
  owner: null,
  refcnt: 0,
  timeoutID: null
};


$('document').ready(function() {

  // Set up our tabs
  $('#data').tabs();

  // Set up our universal key handler
  $(document).bind('keydown', keyDown);

  // Set up the drop handlers
  $('#suggestedtags-container').droppable({
    accept: '.given',
    hoverClass: 'dragover',
    drop: function(event, ui) {

      // Get the tagname that was dropped
      var name = ui.draggable.prop('tagname');

      // Remove the tag
      gTags.removeGiven(name);
    }});

  $('#giventags-container').droppable({
    accept: '.suggested',
    hoverClass: 'dragover',
    drop: function(event, ui) {

      // Get the tagname that was dropped
      var name = ui.draggable.prop('tagname');

      // Add the tag
      gTags.addGiven(name);
    }});

  // Load the initial state
  gTags.loadSuggested();
  gTags.loadGiven();

  // Bootstrap the display
  gTags.refreshDisplay();

  // Init the popup
  gPopup.init();
});

function keyDown(evt) {

  // If we get an arrow, move the slider
  if (evt.which == '37') {
    if (gPopup.owner && isValidConfidence(gPopup.owner.weight - 2))
      gPopup.setConfidence(gPopup.owner.weight - 2);
    return false;
  }
  if (evt.which == '39') {
    if (gPopup.owner && isValidConfidence(gPopup.owner.weight + 2))
      gPopup.setConfidence(gPopup.owner.weight + 2);
    return false;
  }

  // If we get an escape, forward it to the parent window so that it can close us
  if (evt.which == '27') {
    window.parent.postMessage("escape", window.location.href);
    return false;
  }
}

// Standard comparison semantics
function cmp(a,b) {
  if (a < b)
    return -1;
  if (a == b)
    return 0;
  return 1;
}

// Hover callbacks for given tags
function givenOver(eobj) {
  gPopup.addref(gTags.given[eobj.target.tagname]);
}
function givenLeave(eobj) {
  gPopup.release(gTags.given[eobj.target.tagname]);
}
