// Result object definition
function Result(service, handle) {
  this.service = service;
  this.handle = handle;
}
Result.prototype.toString = function() {
  return this.service + ':' + this.handle;
}

// Tracker for search results
var gResults = {

  /*
   * Interface.
   */

  // Add a search result
  addResult: function(service, handle, forQuery) {

    // If this result is coming in for something that's
    // no longer the current query, ignore it.
    if (forQuery != this.currentQuery)
      return;

    // Add the result to our list
    this.results.push(new Result(service, handle));

    // Sort the list
    this.results.sort(resultCompare);

    // Redraw
    this.draw();
  },

  // Sets us up to track a new query
  setQuery: function(newQuery) {

    // Update the query
    this.currentQuery = newQuery;

    // Clear the old results
    this.results = [];

    // Redraw
    this.draw();
  },

  // Repopulates the results box
  draw: function() {

    // Clear the existing result box
    $('#resultbox').empty();

    // If there are no results, just give instructions
    if (this.currentQuery == '') {
      $('#resultbox').html('start typing a username or email address...');
      return;
    }

    // Generate and append the divs
    for (var i in this.results) {

      // Current result
      var r = this.results[i];

      // Photo
      var picURL = '/static/blankprofile-square.jpg';
      if (r.service == 'facebook') {
        picURL = 'https://graph.facebook.com/' +
                 r.handle + '/picture?type=square';
      }
      var picElem = $('<img>').attr('src', picURL)
                              .addClass('result-pic');

      // Handle
      var handleElem =
        $('<span></span>').html(r.handle)
                          .addClass('result-handle');

      // Service
      var serviceElem =
        $('<span></span>').html(r.service)
                          .addClass('result-service');

      // Append the div
      $('<div></div>').prop('service', r.service)
                      .prop('handle', r.handle)
                      .addClass('result')
                      .click(resultClicked)
                      .append(picElem)
                      .append(handleElem)
                      .append(serviceElem)
                      .mouseover(function() {gResults.select(this); })
                      .appendTo('#resultbox');
    }

    // Handle first and last elements
    $('.result:first').addClass('ui-corner-top');
    $('.result:last').addClass('ui-corner-bottom');

    // Apply our style
    this.restyle();
  },

  // Resets all ephemeral style data
  restyle: function() {

     // Remove the 'selected' class from everyone.
     $('.result').removeClass('result-selected');

     // Apply our selection if it's in-bounds
     if (this.selectedIndex >= 0 && this.selectedIndex < this.results.length) {
       $('.result').eq(this.selectedIndex).addClass('result-selected');
     }
  },

  select: function(elem) {

    // Update our index
    this.selectedIndex = -1;

    // Find the element
    var key = new Result(elem.service, elem.handle);
    for (var i = 0; i < this.results.length; ++i) {
      if (this.results[i].toString() == key.toString()) {
        this.selectedIndex = i;
        break;
      }
    }

    // Update the visuals
    this.restyle();
  },

  // React to up/down arrows
  bumpSelected: function(amount) {

    // If nothing is already selected
    if (this.selectedIndex == -1)
      this.selectedIndex = (amount == 1) ? 0 : this.results.length - 1;

    // If something is already selected
    else {
      this.selectedIndex += amount;
      if (this.selectedIndex == -1)
       this.selectedIndex = this.results.length - 1;
      this.selectedIndex %= this.results.length;
    }

    // Update the visuals
    this.restyle();
  },

  // Opens a query for the selected element
  go: function() {

    // Current result
    if (this.selectedIndex == -1)
      return;
    var r = this.results[this.selectedIndex];

    // If there's already a queryframe, remove it
    closeQuery();

    // Make the URL
    var url = window.location.href.replace(/\/*$/,"") + '/query?';
    url += 'handle=' + r.handle + '&service=' + r.service;

    // Add a new queryframe
    $('<iframe src="' + url + '"></iframe>')
        .prop('id', 'queryframe')
        .appendTo('body');
  },

  reset: function() {

    // Reset all the data
    this.currentQuery = '';
    this.results = [];
    this.selectedIndex = -1;

    // Redraw
    this.draw();
  },

  /*
   * Internal members.
   */

  // The query we're tracking results for
  currentQuery: '',

  // The current results
  results: [],

  // The currently selected index
  selectedIndex: -1,
};

// Comparator to sort results. Right now we just prioritize facebook since it's
// the only thing we do deep validation on.
function resultCompare(a, b) {
  if (a.service == 'facebook')
    return -1;
  if (b.service == 'facebook')
    return 1;
  else
    return a.service > b.service;
}

$(document).ready(function() {

    // Set up the results box
    gResults.draw();

    // Register handlers
    $('#searchbox').focus(searchboxFocused);
    $('#searchbox').blur(searchboxBlurred);
    $('#searchbox').keyup(searchboxChanged);

    // We bind our menu manipulation code in two places. We need it in the
    // text box to prevent the default action, and we need it on the document
    // in case the text box isn't focused.
    $('#searchbox').bind('keydown', keyDown);
    $(document).bind('keydown', keyDown);

    // Listen for child iframes to send us escape
    $(window).bind('message', function() {closeQuery();});

    // When we have a queryframe, clicking anywhere outside the
    // iframe should remove it.
    $('body').click(function() {closeQuery();});

    // Prevent click events from bubbling up from centercontent,
    // because otherwise our queryframe is instantly removed when
    // we click to open it.
    $('#centercontent').bind('click', false);
  });

function searchboxFocused() {

  // Make it unhidden
  $('#resultbox').removeClass('hiddenbox');

  // Kick off the change machinery for corner cases like
  // refreshing the page with text in the box.
  searchboxChanged();
}

function searchboxBlurred() {
  if ($('#searchbox').prop('value') == '')
    $('#resultbox').addClass('hiddenbox');
}

function searchboxChanged() {

  // Get the new query
  var query = $('#searchbox').prop('value');

  // If it hasn't changed, we're done.
  if (query == gResults.currentQuery)
    return;

  // Set the new query
  gResults.setQuery(query);

  // TODO: If the name contains spaces, we should do searches
  if (query.indexOf(' ') >= 0)
    return;

  // If the name contains an @, add an email result
  if (query.indexOf('@') >= 0)
    gResults.addResult('email', query, query);

  // Otherwise, add accounts we can't check
  else {
    gResults.addResult('couchsurfing', query, query);
    gResults.addResult('twitter', query, query);
  }

  // Try a facebook search
  var queryURL = 'https://graph.facebook.com/' + query + '?callback=?';
  $.getJSON(queryURL, function(json) {

      // Sometimes facebook just sends us 'false'.
      if (!json)
        return;

      // If we don't have a first name, a last name, or a gender, it's probably
      // not a person.
      if (!(json.first_name || json.last_name || json.gender))
        return;

      // We've got a person. Add the result to the list.
      gResults.addResult('facebook', query, query);
    });
}

// Result manipulation keydown handler
//
// If we capture a key here, we want to prevent the default action.
function keyDown(evt) {

  // Up arrow
  if (evt.which == '38') {
    gResults.bumpSelected(-1);
    return false;
  }

  // Down arrow
  if (evt.which == '40') {
    gResults.bumpSelected(1);
    return false;
  }

  // Enter
  if (evt.which == '13') {
    gResults.go();
    return false;
  }

  // Escape
  if (evt.which == '27') {

    // If there's an open query, close it
    if ($('#queryframe').length != 0)
      closeQuery();

    // Otherwise, reset
    else
      resetPage();

    return false;
  }
}

// Click handler for result items
function resultClicked() {
  
  // The result is probably selected, but might not be (for example, if the
  // mouse hasn't moved and there's been keyboard use in the mean time. Make
  // sure what we clicked on is selected).
  gResults.select(this);

  // Open the query frame
  gResults.go();
}

function closeQuery() {

  // Close the query frame
  $('#queryframe').remove();

  // Focus our window
  window.focus();
}

function resetPage() {

  // Clear the value from the search box
  $('#searchbox').prop('value', '')
                 .blur();

  // Reset the results
  gResults.reset();

  // Refocus the search box
  $('#searchbox').focus();
}
