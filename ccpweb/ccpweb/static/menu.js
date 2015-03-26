/*
* ccpweb.js
*
* Hannah Aizenman, 2011-08
*
* builds interface menus
*/

$(document).ready(function(){
    hideMenu();  
    loadDataList();
    loadAlgList();
});

// changes menus if dataset selection changes
$("#dataList").change(function() { hideMenu(); 
    loadDataOptions($("#dataList :selected").text()) 
});


// helper function 'cause I couldn't find an auto version
function fieldLabel(field) { return [field, "Label"].join(""); };

//creates menu
function loadDataOptions(dataSet){
    validRange(dataSet);    
    loadTime(dataSet);
    loadGrid(dataSet);
    //uncomment to have a default graph of the most recent data
    //defaultGraph(dataSet);
};

// hides and clears menu options
function hideMenu(){
    $.each(["#validRange", "#startTime", "#endTime", "#topLat", "#bottomLat", 
            "#rightLon", "#leftLon"], function(index, value){     
            $(value).empty().hide();
            $(fieldLabel(value)).hide();  
           });
    $("#loading").hide();
};

function loadDataList(){
  // get list of datasets from server
     $.getJSON("datalist", function(data) {
                  fillDropDown("#dataList", data.names);
                  loadDataOptions($("#dataList :selected").text());
                  })
                  .error(function(data, status, xhr) { 
                        alert("can't obtain datalist"); })
                  .complete(function(data, status, xhr) {
                        console.log("dataList obtained"); });
};        

function loadAlgList(){
  // get list of datasets from server
     $.getJSON("alglist", function(data) {
                fillDropDown("#algList", data.names);
                  })
                  .error(function(data, status, xhr) {
                        alert("can't obtain alglist"); })
                  .complete(function(data, status, xhr) {
                   console.log("get alglist finished"); });
};

function validRange(dataSet){
    validURL = [dataSet, "validrange"].join("/");
    $.getJSON(validURL, function(data){
        if (data.time){
            var time_str = ["Time ranges from", data.time.start, 
                            "to", data.time.end, "<br />"].join(" ") 
            $("#validRange").append(time_str);
        };
        if (data.grid){    
            var lat_str = ["Latitude ranges from", data.grid.bottom, 
                           "to", data.grid.top, "in increments of", 
                            data.grid.lat_inc, "degrees", "<br />"].join(" "); 

            var lon_str = ["Longitude ranges from", data.grid.left, 
                           "to", data.grid.right, "in increments of", 
                            data.grid.lon_inc, "degrees", "<br />"].join(" "); 
 
            $("#validRange").append(lat_str);
            $("#validRange").append(lon_str);        
        };
    $("#validRange").show();
    });
};

function defaultGraph(dataSet){
    validURL = [dataSet, "validrange"].join("/");
    $.getJSON(validURL, function(data){
        if (data.time){
            $('#startTime').val(data.time.end);
            $('#endTime').val(data.time.end);
            makeGraph('graph', getOptions()); 
        };
    });
};


function loadTime(dataSet){   
    var timeURL = [dataSet, "time"].join("/");
    $.each(["#startTime", "#endTime"], function(index, value){
            loadAutoComplete(value, timeURL, 12)
    });
};

function loadGrid(dataSet){
    var gridURL = [dataSet, "grid"].join("/");
     $.getJSON(gridURL, function(data){
        var latStr = maxString(data.lat);
        var lonStr = maxString(data.lon);
        $.each(["#topLat", "#bottomLat"], function(index, value){
                loadAutoComplete(value, data.lat, latStr);
               });
        $.each(["#leftLon", "#rightLon"], function(index, value){
                loadAutoComplete(value, data.lon, lonStr);   
               });
        //add in menu for latlon here
    });
};

function fillDropDown(menu, options) {
    for (var i = 0; i<options.length; ++i){ 
        $(menu).append(new Option(options[i], i));
        };    
};

function loadAutoComplete(field, data, strLen){
    $(field).val(null);
    $(field).attr('size', strLen);
    $(field).unautocomplete();
    $(field).autocomplete(data, {mustMatch:true} );
    $(field).show();
    $(fieldLabel(field)).show();
};

function maxString(strLst){
    var maxLen = 0;
    $.each(strLst, function(index, value){
        if (value.length > maxLen){
           maxLen = value.length;
           }
        });
    return maxLen;
};

