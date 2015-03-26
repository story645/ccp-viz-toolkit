/*
* ccpweb.js
*
* Hannah Aizenman, 2011-08
*
* builds server get requests 
*/ 

function getOptions(){ return {"startTime": $("#startTime").val(),
                              "endTime": $("#endTime").val(),
                              "topLat": $("#topLat").val(),
                              "bottomLat": $("#bottomLat").val(),
                              "leftLon": $("#leftLon").val(), 
                              "rightLon": $("#rightLon").val()};
};

$("#graphButton").click( function(){
    makeGraph('graph', getOptions()); 
});

function makeGraph(graph_url, options){
//source: http://jqueryfordesigners.com/image-loading/
    var baseURL = [$("#dataList :selected").text(), graph_url].join("/");
    var imgURL =  getKwargsURL(baseURL, options);
    console.log(["image url:", imgURL].join(" "));
    $("#graph").hide();
    $("#loading").show();
    $('#graph').load(function () { 
      $(this).hide();
      $('#loading').hide();
      $(this).show();
    })
    .error(function () { 
        alert("couldn't generate graph, check menu selections");
    })
    .attr('src', imgURL);
};

function getKwargsURL(baseURL, options){
    var algURL = ["ALG", $("#algList :selected").text()].join("");
    var timeURL = timeKwargs(options.startTime, options.endTime);
    var gridURL = gridKwargs(options.topLat, options.bottomLat, 
                             options.leftLon, options.rightLon);
    var kwargsURL = baseURL;
    $.each([algURL, gridURL, timeURL], function(key, value){
        if (value){
            kwargsURL+=["/",value].join("");
            //[kwargsURL, value].join("/");
        }
     });
   console.log(["kwargs url:", kwargsURL].join(" "));
   return kwargsURL;
};

function timeKwargs(timeStart, timeEnd){
    var timeSt = null;
    var timeEd = null;
    if (timeStart==timeEnd){
        return timeStart
    };
    if (timeStart){
        timeSt = [timeStart,'ST'].join("");
    };
    if (timeEnd){
        timeEd = [timeEnd, 'ED'].join("");
    };
    return [timeSt, timeEd].join("");
};

function gridKwargs(latTop, latBottom, lonLeft, lonRight){
    var latChoice = null;
    var lonChoice = null;
    if (!latTop && !lonLeft){
        return
    }
    if(latTop && latBottom){
        latChoice = [latTop, 'T',latBottom,'B'].join("");   
    }
    else if(latTop){
        latChoice = [latTop, 'T'].join("");
    };

    if(lonLeft && lonRight){
        lonChoice = [lonLeft, 'L', lonRight, 'R'].join("");
    }
    else if (lonLeft){
        lonChoice = [lonLeft, 'L'].join("");
    };

    return [latChoice, lonChoice].join("");
};
