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
