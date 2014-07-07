$(function () {
		
		var margin = {top: 30, right: 20, bottom: 30, left: 40},
    width = 600 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;
		
		var graphData = function (data, prodname) {
			$("#graph_container").empty();
			
			// setup x 
			var xValue = function(d) { return new Date(d.time * 1000);}, // data -> value
			xScale = d3.time.scale().range([0, width]), // value -> display
			xMap = function(d) { return xScale(xValue(d));}, // data -> display
			xAxis = d3.svg.axis().scale(xScale).orient("bottom");
			
			// setup y
			var yValue = function(d) { return d.average_rating;}, // data -> value
			yScale = d3.scale.linear().range([height*.9, 0]), // value -> display
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
			yScale.domain([1, 5.5]);
			
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
			.text("Cumulative average rating");
			
			// draw dots
			svg.selectAll(".dot")
			.data(data)
			.enter().append("circle")
			.attr("class", "dot")
			.attr("r", 3.5)
			.attr("cx", xMap)
			.attr("cy", yMap)
			.style("opacity", .3);
			//.style("fill", function(d) { return color(cValue(d));}) 
			
			//Put a title maybe
			svg.append("text")
        .attr("x", (width / 2))             
        .attr("y", 0 - (margin.top / 5))
        .attr("text-anchor", "middle")  
        .style("font-size", "16px") 
        .style("text-decoration", "underline")  
        //.text("Cumulative Average Review" + " for "+ prodname);
        .text(prodname);
			
			
			
			// draw legend
			
			
			
			
			
		};
		
		var productstuff = function (title, reviews) {
			$("#prod-des").empty();
			$("#prod-des0").empty();
			$("#prod-des1").empty();
			$("#prod-des2").empty();
			$("#prod-des").append(title)
			$("#prod-des").append("Here's what people had to say: ")
			//$("#prod-des").append("<div>").addClass("my-description").append("Heyy its working");
		for (var i=0; i < reviews.length; i++) {
			var d = reviews[i];
			//console.log(d.rating);	
			//$("#prod-des"+i).append("<div>").attr("prod-des-id",i).addClass("my-description").css("padding","30px").append('"' + d + '"')
			$("#prod-des"+i).css("padding","40px").append('"' + d + '"')
			
			}
			//$("#prod-des").text("title?")
			

		};
		
		
		
		$("#fetch_product_button").click(function() {
				var product = $("#product").val(); 
				$("#loading").show();
				$.get( "/product/json/"+product)
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		

		$("#input_dates_button").click(function() {
				var time1 = $("#time1").val(); 
				var time2 = $("#time2").val();
				var product = $("#product").val();
				$("#loading").show();
				$.get( "/times/?time1="+time1+"&time2="+time2+"&product="+product)
				.done(function (data) {
						$("#loading").hide();
						//graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
				}); 
		});
		
		
		$("#zojirushi").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Zojirushi EC-BD15BA Fresh Brew Thermal Carafe Coffee Maker");
				$("#loading").show();
				$.get( "/product/json/"+"Zojirushi EC-BD15BA Fresh Brew Thermal Carafe Coffee Maker")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		$("#taylor").click(function() {
				//var product = $("#B0000X7CMQ").val();
				$("#product").val("Taylor 7506 Glass and Chrome Digital Scale");
				$("#loading").show();
				$.get( "/product/json/"+"Taylor 7506 Glass and Chrome Digital Scale")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		
		$("#airpurifier").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Honeywell Enviracaire HEPA Air Purifier");
				$("#loading").show();
				$.get( "/product/json/"+"Honeywell Enviracaire HEPA Air Purifier")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		$("#hamiltonbeach").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Hamilton Beach Big Mouth Juice Extractor 67650");
				$("#loading").show();
				$.get( "/product/json/"+"Hamilton Beach Big Mouth Juice Extractor 67650")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		$("#thermometer").click(function() {
				//var product = $("#B0000X7CMQ").val();
				$("#product").val("Maverick Wireless BBQ Thermometer Set - Maverick ET73");
				$("#loading").show();
				$.get( "/product/json/"+"Maverick Wireless BBQ Thermometer Set - Maverick ET73")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		$("#victorinox").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Victorinox 40520");
				$("#loading").show();
				$.get( "/product/json/"+"Victorinox 40520")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		$("#wabash").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Wabash Valley Farms 25008 Whirley-Pop Stovetop Popcorn Popper");
				$("#loading").show();
				$.get( "/product/json/"+"Wabash Valley Farms 25008 Whirley-Pop Stovetop Popcorn Popper")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
	
		
		$("#vicks").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Vicks 1.0 Gallon Cool Mist Humidifier");
				$("#loading").show();
				$.get( "/product/json/"+"Vicks 1.0 Gallon Cool Mist Humidifier")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		
		$("#playmobil").click(function() {
				//var product = $("#B0000X7CMQ").val(); 
				$("#product").val("Playmobil Security Check Point");
				$("#loading").show();
				$.get( "/product/json/"+"Playmobil Security Check Point")
				.done(function (data) {
						$("#loading").hide();
						graphData(data.ratings, data.prodname);
						productstuff(data.title, data.reviews);
						$('#timebutton').css("display","block")
						$('#datarow').css("display", "block")
						//$('#rowbackground').css("display", "block")
				}); 
		});
		
		
		
});
