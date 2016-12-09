var initialLocations = [{
	name: "Harrisburg, PA",
	lat: 40.2821392,
	lng: -76.9154448
},{
	name: "ArcelorMittal",
	lat: 40.232537,
	lng: -76.83678
},{
	name: "Pennsylvania State Capital Complex",
	lat: 40.2694982,
	lng: -76.8926958
},{
	name: "HACC, Central Pennsylvania's Community College",
	lat: 40.2963235,
	lng: -76.8886755
},{
	name: "Whitaker Center for Science and the Arts",
	lat: 40.260784,
	lng: -76.8824813
},{
	name: "Harrisburg Midtown Arts Center",
	lat: 40.268145,
	lng: -76.8904567
},{
	name: "Oyster Mill Playhouse",
	lat: 40.261211,
	lng: -76.936234
}];

var map;

function Location(data) {
	if (!data){
		data = {};
	}

	var self = this;
	self.name = data.name;
	self.lat = data.lat;
	self.lng = data.lng;

	// create marker
	this.marker = new google.maps.Marker({
		position: new google.maps.LatLng(data.lat, data.lng),
		map: map,
		title: data.name
	});

	// Wikipedia API
    $.ajax({
        url: "https://en.wikipedia.org/w/api.php",
        data: {
            "action": "opensearch",
            "search": self.name,
            "format": "json"
        },
        dataType: "jsonp",
        success: function(response){
            var links = response[3];
            var titles = response[1];
            var header = "<div id='content'><h3>Wikipedia links:</h3>";
            self.contentString = "";
            for (var i=0; i<links.length; i++){
            	// append links to the content string
                self.contentString += "<p><a href='"+links[i]+"'>"+titles[i]+"</a></p>";
            };
            if (self.contentString.length<1) {
            	// if no links are displayed, report a lack of articles
            	self.contentString += "<p>No articles for " + self.name + "</p>"
            };
            self.contentString = header + self.contentString + "</div>";
        }
    }).error(function() {
    	// If there is an error, report in contentString
        self.contentString = "Relevant Wikipedia Links failed to load.";
    }).fail(function(err) {
    	// If there is a failure, report in contentString
    	self.contentString = "Relevant Wikipedia Links failed to load.";
      	throw err;
    });

    var infoWindow = new google.maps.InfoWindow({
      content: ""
    });

    this.clickHandler = function(){
    	// Make marker bounce twice
		self.marker.setAnimation(google.maps.Animation.BOUNCE);
		setTimeout(function(){ self.marker.setAnimation(null); }, 1450);
		// Move to marker location
		map.setZoom(13);
		map.panTo(self.marker.getPosition());
		// Open and set infowindow for marker
		infoWindow.open(map, self.marker);
		infoWindow.setContent(self.contentString);
    };

	this.marker.addListener('click', self.clickHandler);
};

function LocationViewModel() {
	var self = this;
	this.locList = ko.observableArray([]);
	initialLocations.forEach(function(loc){
		self.locList.push( new Location(loc));
	})

	//TODO: functionality to ADD a location

	//TODO: functionality to DELETE a location
};

function Filter(locations){
	var self = this;
	this.name = ko.observable();
	this.locList = locations;

	this.locationsToShow = ko.pureComputed(function() {
	    // Represents a filtered list of locations
	    var desiredName = this.name();
	    // If there is nothing typed
	    if (!desiredName || desiredName.length<1) {
	    	this.locList().forEach(function(loc){
	    		loc.marker.setMap(map);
	    	})
	    	return this.locList();
	    };
	    // Otherwise return a filtered list according to the below function
	    // i.e., only those containing the "name" condition
	    return ko.utils.arrayFilter(this.locList(), function(loc) {
	    	var bool = loc.name.toUpperCase().includes(desiredName.toUpperCase());
	    	if (bool) {
	    		loc.marker.setMap(map);
	    	} else {
	    		loc.marker.setMap(null);
	    	}
	        return bool;
	    });
	}, this);
};

function ViewModel() {
	var self = this;
	// Initialize map
	map = new google.maps.Map(document.getElementById('map'), {
		zoom: 11,
		center: initialLocations[0]
	});
	// Call location and filter setup
	this.locator = new LocationViewModel();
	this.filter = new Filter(this.locator.locList);
};


function initMap() {
	ko.applyBindings(new ViewModel());
};

function googleError(){
	var mapArea = $('#map');
	mapArea.append("<h1>Map was not able to load!</h1>");
};