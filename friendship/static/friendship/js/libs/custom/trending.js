$(document).ready(function(){
	$('.slide-container').slick({
    speed: 500,
    slidesToShow: 5,
    slidesToScroll: 5,
		autoplay: true,
		pauseOnFocus: false,
		autoplaySpeed: 2000,
		prevArrow:"<button class='prev'>&#10094</button>",
    nextArrow:"<button class='next'>&#10095</button>",
		responsive: [ //responsive to screen sizes
			{
	      breakpoint: 1500,
	      settings: {
	        slidesToShow: 4,
	        slidesToScroll: 4
	      }
	    },
	    {
	      breakpoint: 1200,
	      settings: {
	        slidesToShow: 3,
	        slidesToScroll: 3
	      }
	    },
	    {
	      breakpoint: 1000,
	      settings: {
	        slidesToShow: 2,
	        slidesToScroll: 2
	      }
	    },
	    {
	      breakpoint: 300,
	      settings: {
	        slidesToShow: 1,
	        slidesToScroll: 1
	      }
	    }
	  ]
	});

});
// var paused = false; // if the animation of the slideshow is paused
// var dotIndex = 3; // the index of the dot that is activated
// var pausedTime = 0; //time(Date().getTime) when the latest animation paused
// pauseSlides(); //constantly checks when to pause the animation
//
// //make a dot black, which means the image of the corresponding dot is displayed at the center now
// function activateDot(dot) {
// 	for(var i=1; i<=5; i++){
// 		if(i !== dot){
// 			if(document.getElementById('dot'+i).className.indexOf('active') !== -1){
// 				document.getElementById('dot'+i).className = document.getElementById('dot'+i).className.replace(" active", "");
// 			}
// 		}else{
// 			document.getElementById('dot'+dot).className += " active";
// 		}
// 	}
// }
//
// //return boolean if any slide(image) is positioned at the center of the screen
// function slideAtCenter() {
// 	var slides = document.getElementsByClassName('slide');
// 	for(var i=0; i< slides.length; i++){
// 		var center = ((slides[i].getBoundingClientRect().left + slides[i].getBoundingClientRect().right)/2);
// 		if(center >= $(window).width()/2 - 5 && center <= $(window).width()/2 + 5 && paused === false){
// 			return true;
// 		}
// 	}
// 	return false;
// }
//
// //recursive function that pauses the slideshow whenever a slide(image) is positioned at the center
// function pauseSlides() {
// 	var now = new Date().getTime();
// 	if(now - pausedTime > 2000 && paused === true){
// 		document.getElementById('slide1').style.animationPlayState="";
// 		$(".slideshow").animate({"margin-left": "-=10px"}, "fast");
// 		paused = false;
// 	}else if(paused === false){
// 		var slides = document.getElementsByClassName('slide');
// 		for(var i=0; i< slides.length; i++){
// 			var center = ((slides[i].getBoundingClientRect().left + slides[i].getBoundingClientRect().right)/2);
// 			if(center >= $(window).width()/2 - 1 && center <= $(window).width()/2 + 1 && paused === false && now-pausedTime>2500){
// 				document.getElementById('slide1').style.animationPlayState="paused";
// 				pausedTime = new Date().getTime();
// 				paused = true;
// 				dotIndex = dotIndex%5===0? 5: dotIndex%5;
// 				activateDot(dotIndex);
// 				dotIndex ++;
// 			}
// 		}
// 	}
// 	setTimeout(pauseSlides, 1);
// }
//
// //onclick event for dots to scroll through images
// var dots = document.getElementsByClassName('dot');
// for(var i in dots){
// 	dots[i].onclick = function(e){
// 		document.getElementById('slide1').style.animationPlayState="paused";
// 		pausedTime = new Date().getTime();
// 		var clickedIndex = parseInt(e.target.id[e.target.id.length-1]);
// 		if(dotIndex > clickedIndex){
// 			var distance = (dotIndex - clickedIndex -1)*220;
// 			$(".slideshow").animate({"margin-left": "+="+distance+"px"}, "slow");
// 		}else if(dotIndex < clickedIndex){
// 			var distance = (clickedIndex-dotIndex+1)*220;
// 			$(".slideshow").animate({"margin-left": "-="+distance+"px"}, "slow");
// 		}
// 		activateDot(clickedIndex);
// 		dotIndex = clickedIndex+1;
// 		paused = true;
// 	};
// }
