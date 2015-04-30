$(function(){

    // Plot dimensions
    var height = 100;
    var width = 400;

    // Create the svg drawing canvas
    var plot_svg = d3.select('#plot-container').append("svg")
	.attr("height",height)
	.attr("width", width);

    var plot = plot_svg.append("g");

    // Make the axis scales. These will eventually map data 
    // coordinates to svg image coordinates
    var ampScale = d3.scale.linear().range([height,0]);
    var tScale = d3.scale.linear().range([0,width]);


    // Function that displays the line. 
    var lineFunc = d3.svg.line()
	.x(function(d) {
	    return tScale(d.t);
	})
	.y(function(d) {
	    var amp = ampScale(d.wavelet); 
	    console.log(amp);
	    return amp;
	});



    function update_plot(data){
	// Updates the wavelet plot based on data struct received
	// from the backend

	data = JSON.parse(data);
	// Make xy pairs for d3 lines
	var paired_data = [];

	for(var i=0; i < data.wavelet.length; i++){
	    var point = {};
	    point["wavelet"] = data.wavelet[i];
	    point["t"] = data.t[i];

  	    paired_data[i] = point;
	} // end of for

	// Set the yscale domain (amplitude)
	ampScale.domain([Math.min.apply(Math,data.wavelet), 
  			  Math.max.apply(Math,data.wavelet)]);

	// Set the time scale domain
	tScale.domain([Math.min.apply(Math,data.t), 
  			  Math.max.apply(Math,data.t)]);;
	
	// Remove the previous line
	plot.selectAll("path").remove();

	// Add the new plot, attach the paired data to the path
	var line = plot.append("path")
            .attr("d", lineFunc(paired_data))
            .attr('stroke', 'black')
            .attr('stroke-width', 1)
	    .attr('fill', 'none');

    }; // end of function update_plot


    // Server request for data
    function server_request(){

	var phase = $('#phase-slider').val();
	var f = $('#frequency-slider').val();

	// Requests data from the server then sends it to 
	// update plot
	$.get('/wavelet', {phase:phase, f:f},
	     update_plot);

    };


    // Slider handlers (these update the value display)
    $('#frequency-slider').on("input", 
			      function(){
			      $('#frequency-output').val(this.value);
			      });
    $('#phase-slider').on("input", 
			      function(){
			      $('#phase-output').val(this.value);
			      });


    // These will actually request data with the updated values
    $('#frequency-slider').on("change", server_request);
    $('#phase-slider').on("change", server_request);


    // update the data on initialization
    server_request();
});
