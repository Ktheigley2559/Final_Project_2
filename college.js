var width = 950,
    height = 630;
var projection = d3.geo.albers()
   .scale(1300)
   .rotate([96.5,0.7])
   .center([0, 39.313])
   .translate([width/2, height/2]);
var div = d3.select("body").append("div") 
    .attr("class", "tooltip")       
    .style("opacity", 0);
var path = d3.geo.path()
    .projection(projection);
var svg = d3.select("#map").append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g");
var zoom = d3.behavior.zoom()
    .on("zoom",function() {
svg.attr("transform","translate("+ 
d3.event.translate.join(",")+")scale("+d3.event.scale+")");
svg.selectAll("circle")
    .attr("d", path.projection(projection))
    .attr("r", (2/zoom.scale()))//////
svg.selectAll("path")  
    .attr("d", path.projection(projection)); 
});
svg.call(zoom)
//var g = svg.append("g");
d3.json("data/golfusa.json", function(error, us) {
	if (error) return console.error(error);  
    var Countries = topojson.feature(us, us.objects.usa)
    var States = topojson.feature(us, us.objects.stateslakes)
    var Cities = topojson.feature(us, us.objects.usplaces);
////city/////
svg.selectAll(".city")
  .data(Cities.features)
  .enter().append("path")
  .attr("class","city")
   .attr("d", path.pointRadius(2))///////
  .attr("fill", "transparent")
  .style("stroke","silver")
  .style("stroke-width",2)
  .attr("d", path);
svg.selectAll(".place-label")
  .data(Cities.features)
  .enter().append("text")
  .attr("class", "place-label")
  .style("fill", function (d) { return "silver"; })
  .attr("transform", function(d) { return "translate(" + projection(d.geometry.coordinates) + ")"; })
  .attr("x", function(d) { return d.geometry.coordinates[0] > -1 ? 8 : -6; })
  .attr("dy", ".35em")
  .style("text-anchor", function(d) { return d.geometry.coordinates[0] > -1 ? "start" : "end"; })
  .text(function(d) { return d.properties.NAME; });
svg.selectAll(".state")
  .data(States.features)
  .enter().append("path")
  .attr("class","states")
  .attr("fill", "peru")
  .attr("fill-opacity",0.2)
  .style("stroke","white")
  .style("stroke-width",2)
  .attr("d", path);
svg.selectAll(".country")
  .data(Countries.features)
  .enter().append("path")
  .attr("class","countries")
  .attr("fill", "peru")
.style("fill-opacity", function(d) {
if (d.properties.ADM0_A3 == "USA"){return 0
} else {return 0.4;
}})
  .style("stroke","transparent")
  .style("stroke-width",2)
  .attr("d", path);
svg.selectAll(".uspark-label")
  .data(States.features)
  .enter().append("text")
  .attr("class", function(d) { return "uspark-label " + d.properties.postal; })
  .attr("transform", function(d) { return "translate(" + path.centroid(d) + ")"; })
  .attr("dy", ".35em")
  .text(function(d) { return d.properties.postal; })
//With map made, load data and add it to the map
d3.csv('data/college.csv', function(error2, wetland) {
    if (error2) return console.error(error2);
        addPointsToMap(wetland);
});
});
var addPointsToMap = function(wetland) {
var colorScale  = d3.scale.category10();
var tooltip = d3.select("#map").append("div")
  .attr("class", "tooltip")
  .style("opacity", 0);
//tooltip mouseover event handler
var tipMouseover = function(d) {
    this.setAttribute("class", "circle-hover");// add hover class to emphasize
var html  = "<b>" + "Name: " + "</b>" + d.Name + "<br/>" +
            "<b>" + "Address: " + "</b>" + d.ADDR + "<br/>" +
            "<b>" + "City: " + "</b>" + d.CITY + "<br/>" +
            "<b>" + "County: " + "</b>" + d.County + "<br/>" +
            "<b>" + "State: " + "</b>" + d.State ;
tooltip.html(html)
    .style("left", (d3.event.pageX + 15) + "px")
    .style("top", (d3.event.pageY - 28) + "px")
    .transition().duration(200)// ms
    .style("opacity", .9)// started as 0!
};
// tooltip mouseout event handler
var tipMouseout = function(d) {
    this.classList.remove("circle-hover"); // remove hover class
tooltip.transition()
    .duration(300)// ms
    .style("opacity", 0);// don't care about position!
};
svg.selectAll("circle")
    .data(wetland)
    .enter().append("circle")
    .attr("cx", function(d) { return projection([d.long, d.lat])[0]; })
    .attr("cy", function(d) { return projection([d.long, d.lat])[1]; })
    .attr("r",  function(d) { return 2; })//;
    .attr("fill", function(d) {
var str = d.Name;
if (null === str) { return "transparent";}
else if (str.includes("University")) { return "dodgerblue"; }
else if (str.includes("College")) { return "#ee4266"; }
else if (str.includes("Institute")) { return "blueviolet"; }
else {return "lime"; } 
    })
    .attr("fill-opacity",  function(d) { return 0.5; })
     .style("vector-effect","non-scaling-stroke")
    .on("mouseover", tipMouseover)
    .on("mouseout", tipMouseout);//addLegend(colorScale);
};