/*! jQuery-ui-Slider-Pips - v1.9.0 - 2015-04-06
* Copyright (c) 2015 Simon Goellner <simey.me@gmail.com>; Licensed MIT */

// PIPS

(function($) {

    "use strict";

    var extensionMethods = {

        pips: function( settings ) {

            var i,
                p,
                slider = this,
                collection = "",
                pips = ( slider.options.max - slider.options.min ) / slider.options.step,
                $handles = slider.element.find(".ui-slider-handle"),
                $pips;

            var options = {

                first: "label",
                // "label", "pip", false

                last: "label",
                // "label", "pip", false

                rest: "pip",
                // "label", "pip", false

                labels: false,
                // [array], { first: "string", rest: [array], last: "string" }, false

                prefix: "",
                // "", string

                suffix: "",
                // "", string

                step: ( pips > 100 ) ? Math.floor( pips * 0.05 ) : 1,
                // number

                formatLabel: function(value) {
                    return this.prefix + value + this.suffix;
                }
                // function
                // must return a value to display in the pip labels

            };

            $.extend( options, settings );

            slider.options.pipStep = options.step;

            // get rid of all pips that might already exist.
            slider.element
                .addClass("ui-slider-pips")
                .find(".ui-slider-pip")
                .remove();

            // small object with functions for marking pips as selected.

            var selectPip = {

                single: function(value) {

                    this.resetClasses();

                    $pips
                        .filter(".ui-slider-pip-" + value )
                        .addClass("ui-slider-pip-selected");

                },

                range: function(values) {

                    this.resetClasses();

                    for( i = 0; i < values.length; i++ ) {

                        $pips
                            .filter(".ui-slider-pip-" + values[i] )
                            .addClass("ui-slider-pip-selected-" + (i+1) );

                    }

                },

                resetClasses: function() {

                    $pips.removeClass( function (index, css) {
                        return ( css.match(/(^|\s)ui-slider-pip-selected(\S+|\s|$)/g) || [] ).join(" ");
                    });

                }

            };

            // when we click on a label, we want to make sure the
            // slider's handle actually goes to that label!
            // so we check all the handles and see which one is closest
            // to the label we clicked. If 2 handles are equidistant then
            // we move both of them. We also want to trigger focus on the
            // handle.

            // without this method the label is just treated like a part
            // of the slider and there's no accuracy in the selected value
            
            function labelClick( label ) {

                if (slider.option("disabled")) {
                    return;
                }

                var h,
                    val = $(label).data("value"),
                    $thisSlider = slider.element,
                    sliderVals,
                    comparedVals,
                    finalVals,
                    closestVal;

                if ( slider.options.values && slider.options.values.length ) {

                    finalVals = sliderVals = $thisSlider.slider("values");
                    comparedVals = sliderVals.map(function(v) {
                        return Math.abs( v - val );
                    });

                    closestVal = Math.min.apply( Math, comparedVals );

                    for( h = 0; h < comparedVals.length; h++ ) {
                        if( comparedVals[h] === closestVal ) {
                            finalVals[h] = val;
                            $handles.eq(h).trigger("focus.selectPip");
                        }
                    }

                    $thisSlider.slider("values", finalVals);
                    selectPip.range( finalVals );

                } else {
                    
                    $handles.trigger("focus.selectPip");

                    $thisSlider.slider("value", val );
                    selectPip.single( val );

                }

            }

            // method for creating a pip. We loop this for creating all
            // the pips.

            function createPip( which ) {

                var label,
                    percent,
                    number = which,
                    classes = "ui-slider-pip",
                    css = "";

                if ( "first" === which ) { number = 0; }
                else if ( "last" === which ) { number = pips; }

                // labelValue is the actual value of the pip based on the min/step
                var labelValue = slider.options.min + ( slider.options.step * number );

                // classLabel replaces any decimals with hyphens
                var classLabel = labelValue.toString().replace(".","-");

                // We need to set the human-readable label to either the
                // corresponding element in the array, or the appropriate
                // item in the object... or an empty string.

                if( $.type(options.labels) === "array" ) {
                    label = options.labels[number] || "";
                }

                else if( $.type( options.labels ) === "object" ) {

                    // set first label
                    if( "first" === which ) {
                        label = options.labels.first || "";
                    }

                    // set last label
                    else if( "last" === which ) {
                        label = options.labels.last || "";
                    }

                    // set other labels, but our index should start at -1
                    // because of the first pip.
                    else if( $.type( options.labels.rest ) === "array" ) {
                        label = options.labels.rest[ number - 1 ] || "";
                    } 

                    // urrggh, the options must be f**ked, just show nothing.
                    else {
                        label = labelValue;
                    }
                }

                else {

                    label = labelValue;

                }



                // First Pip on the Slider
                if ( "first" === which ) {

                    percent = "0%";

                    classes += " ui-slider-pip-first";
                    classes += ( "label" === options.first ) ? " ui-slider-pip-label" : "";
                    classes += ( false === options.first ) ? " ui-slider-pip-hide" : "";

                // Last Pip on the Slider
                } else if ( "last" === which ) {

                    percent = "100%";

                    classes += " ui-slider-pip-last";
                    classes += ( "label" === options.last ) ? " ui-slider-pip-label" : "";
                    classes += ( false === options.last ) ? " ui-slider-pip-hide" : "";

                // All other Pips
                } else {

                    percent = ((100/pips) * which).toFixed(4) + "%";

                    classes += ( "label" === options.rest ) ? " ui-slider-pip-label" : "";
                    classes += ( false === options.rest ) ? " ui-slider-pip-hide" : "";

                }

                classes += " ui-slider-pip-" + classLabel;


                // add classes for the initial-selected values.
                if ( slider.options.values && slider.options.values.length ) {

                    for( i = 0; i < slider.options.values.length; i++ ) {

                        if ( labelValue === slider.options.values[i] ) {
                            classes += " ui-slider-pip-initial-" + (i+1);
                            classes += " ui-slider-pip-selected-" + (i+1);
                        }

                    }

                } else {

                    if ( labelValue === slider.options.value ) {
                        classes += " ui-slider-pip-initial";
                        classes += " ui-slider-pip-selected";
                    }

                }



                css = ( slider.options.orientation === "horizontal" ) ?
                    "left: "+ percent :
                    "bottom: "+ percent;


                // add this current pip to the collection
                return  "<span class=\""+classes+"\" style=\""+css+"\">"+
                            "<span class=\"ui-slider-line\"></span>"+
                            "<span class=\"ui-slider-label\" data-value=\""+labelValue+"\">"+ options.formatLabel(label) +"</span>"+
                        "</span>";

            }

            // we don't want the step ever to be a floating point.
            slider.options.pipStep = Math.round( slider.options.pipStep );

            // create our first pip
            collection += createPip("first");

            // for every stop in the slider; we create a pip.
            for( p = 1; p < pips; p++ ) {
                if( p % slider.options.pipStep === 0 ) {
                    collection += createPip( p );
                }
            }

            // create our last pip
            collection += createPip("last");

            // append the collection of pips.
            slider.element.append( collection );

            // store the pips for setting classes later.
            $pips = slider.element.find(".ui-slider-pip");



            slider.element.on("mouseup.selectPip", ".ui-slider-label", function(e) {

                e.stopPropagation();
                labelClick( this );

            });




            slider.element.on( "slide.selectPip slidechange.selectPip", function(e,ui) {

                var value, values,
                    $slider = $(this);

                if ( !ui ) {

                    value = $slider.slider("value");
                    values = $slider.slider("values");

                    if ( values.length ) {
                        selectPip.range( values );
                    } else {
                        selectPip.single( value );
                    }

                } else {

                    if ( ui.values ) {
                        selectPip.range( ui.values );
                    } else {
                        selectPip.single( ui.value );
                    }

                }

            });




        }

    };

    $.extend(true, $.ui.slider.prototype, extensionMethods);

})(jQuery);










// FLOATS

(function($) {

    "use strict";

    var extensionMethods = {

        float: function( settings ) {

            var i,
                slider = this,
                tipValues = [],
                $handles = slider.element.find(".ui-slider-handle");

            var options = {

                handle: true,
                // false

                pips: false,
                // true

                labels: false,
                // [array], { first: "string", rest: [array], last: "string" }, false

                prefix: "",
                // "", string

                suffix: "",
                // "", string

                event: "slidechange slide",
                // "slidechange", "slide", "slidechange slide"

                formatLabel: function(value) {
                    return this.prefix + value + this.suffix;
                }
                // function
                // must return a value to display in the floats

            };

            $.extend( options, settings );

            if ( slider.options.value < slider.options.min ) { 
                slider.options.value = slider.options.min; 
            }

            if ( slider.options.value > slider.options.max ) { 
                slider.options.value = slider.options.max; 
            }

            if ( slider.options.values && slider.options.values.length ) {

                for( i = 0; i < slider.options.values.length; i++ ) {

                    if ( slider.options.values[i] < slider.options.min ) { 
                        slider.options.values[i] = slider.options.min; 
                    }

                    if ( slider.options.values[i] > slider.options.max ) { 
                        slider.options.values[i] = slider.options.max; 
                    }

                }

            }

            // add a class for the CSS
            slider.element
                .addClass("ui-slider-float")
                .find(".ui-slider-tip, .ui-slider-tip-label")
                .remove();

            function getPipLabels( values ) {

                // when checking the array we need to divide
                // by the step option, so we store those values here.

                var vals = [],
                    steppedVals = values.map(function(v) {
                        return Math.ceil(( v - slider.options.min ) / slider.options.step);
                    });

                // now we just get the values we need to return
                // by looping through the values array and assigning the
                // label if it exists.

                if( $.type( options.labels ) === "array" ) {

                    for( i = 0; i < values.length; i++ ) {

                        vals[i] = options.labels[ steppedVals[i] ] || values[i];

                    }

                }

                else if( $.type( options.labels ) === "object" ) {

                    for( i = 0; i < values.length; i++ ) {

                        if( values[i] === slider.options.min ) {
                            vals[i] = options.labels.first || slider.options.min;
                        }

                        else if( values[i] === slider.options.max ) {
                            vals[i] = options.labels.last || slider.options.max;
                        }

                        else if( $.type( options.labels.rest ) === "array" ) {
                            vals[i] = options.labels.rest[ steppedVals[i] - 1 ] || values[i];
                        } 

                        else {
                            vals[i] = values[i];
                        }

                    }

                }

                else {

                    for( i = 0; i < values.length; i++ ) {

                        vals[i] = values[i];

                    }

                }

                return vals;

            }

            // apply handle tip if settings allows.
            if ( options.handle ) {

                // We need to set the human-readable label to either the
                // corresponding element in the array, or the appropriate
                // item in the object... or an empty string.

                tipValues = ( slider.options.values && slider.options.values.length ) ? 
                    getPipLabels( slider.options.values ) :
                    getPipLabels( [ slider.options.value ] );

                for( i = 0; i < tipValues.length; i++ ) {

                    $handles
                        .eq( i )
                        .append( $("<span class=\"ui-slider-tip\">"+ options.formatLabel(tipValues[i]) +"</span>") );

                }

            }

            if ( options.pips ) {

                // if this slider also has pip-labels, we make those into tips, too.
                slider.element.find(".ui-slider-label").each(function(k,v) {

                    var $this = $(v),
                        val = [ $this.data("value") ],
                        label,
                        $tip;


                    label = options.formatLabel( getPipLabels( val )[0] );

                    // create a tip element
                    $tip =
                        $("<span class=\"ui-slider-tip-label\">" + label + "</span>")
                            .insertAfter( $this );

                });

            }

            // check that the event option is actually valid against our
            // own list of the slider's events.
            if ( options.event !== "slide" &&
                options.event !== "slidechange" &&
                options.event !== "slide slidechange" &&
                options.event !== "slidechange slide" ) {

                options.event = "slidechange slide";

            }

            // when slider changes, update handle tip label.
            slider.element.on( options.event , function( e, ui ) {

                var uiValue = ( $.type( ui.value ) === "array" ) ? ui.value : [ ui.value ],
                    val = options.formatLabel( getPipLabels( uiValue )[0] );

                $(ui.handle)
                    .find(".ui-slider-tip")
                    .html( val );

            });

        }

    };

    $.extend(true, $.ui.slider.prototype, extensionMethods);

})(jQuery);
