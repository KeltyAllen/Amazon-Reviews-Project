$(function () {
		
		var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 400 - margin.top - margin.bottom;
		
		var graphData = function (data) {
			$("#graph_container").empty();
			
			// setup x 
			var xValue = function(d) { return new Date(d.time * 1000);}, // data -> value
			xScale = d3.time.scale().range([0, width]), // value -> display
			xMap = function(d) { return xScale(xValue(d));}, // data -> display
			xAxis = d3.svg.axis().scale(xScale).orient("bottom");
			
			// setup y
			var yValue = function(d) { return d.average_rating;}, // data -> value
			yScale = d3.scale.linear().range([height, 0]), // value -> display
			yMap = function(d) { return yScale(yValue(d));}, // data -> display
			yAxis = d3.svg.axis().scale(yScale).orient("left");
			
			// setup fill color
			//var cValue = function(d) { return d.Manufacturer;},
			//color = d3.scale.category10();
			
			// add the graph canvas to the body of the webpage
			var svg = d3.select("#graph_container").append("svg")
			.attr("width", width + margin.left + margin.right)
			.attr("height", height + margin.top + margin.bottom)
			.append("g")
			.attr("transform", "translate(" + margin.left + "," + margin.top + ")");
			
			// add the tooltip area to the webpage
			//var tooltip = d3.select("body").append("div")
			//.attr("class", "tooltip")
			//.style("opacity", 0);
			
			// load data
			//d3.csv("cereal.csv", function(error, data) {
			
			// change string (from CSV) into number format
			//data.forEach(function(d) {
			//d.Calories = +d.Calories;
			//d["Protein (g)"] = +d["Protein (g)"];
			//    console.log(d);
			//});
			
			// don't want dots overlapping axis, so add in buffer to data domain
			var oneMonthMilliseconds = 30 * 24 * 60 * 60 * 1000;
			var xAxisStartDate = new Date(d3.min(data, xValue).getTime() - oneMonthMilliseconds);
			xScale.domain([xAxisStartDate, d3.max(data, xValue)]);
			yScale.domain([1, 5]);
			
			// x-axis
			svg.append("g")
			.attr("class", "x axis")
			.attr("transform", "translate(0," + height + ")")
			.call(xAxis)
			.append("text")
			.attr("class", "label")
			.attr("x", width)
			.attr("y", -6)
			.style("text-anchor", "end")
			.text("Timestamp");
			
			// y-axis
			svg.append("g")
			.attr("class", "y axis")
			.call(yAxis)
			.append("text")
			.attr("class", "label")
			.attr("transform", "rotate(-90)")
			.attr("y", 6)
			.attr("dy", ".71em")
			.style("text-anchor", "end")
			.text("Avg rating");
			
			// draw dots
			svg.selectAll(".dot")
			.data(data)
			.enter().append("circle")
			.attr("class", "dot")
			.attr("r", 3.5)
			.attr("cx", xMap)
			.attr("cy", yMap);
			//.style("fill", function(d) { return color(cValue(d));}) 
			
			
			
			// draw legend
			
			
			
			
			
		};
		
		
		$("#fetch_product_button").click(function() {
				var product = $("#product").val(); 
				$.get( "/product/json/"+product)
				.done(function (data) {
						graphData(data.reviews);
				}); 
		});
});