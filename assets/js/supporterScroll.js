//TimelineMax
const scroll = new TimelineMax({repeat: -1, delay: 2, repeatDelay: 3}),
	animate = $(".animate"),
	listHeight = animate.outerHeight();

scroll.to(animate, 180, { top: -listHeight, ease: Linear.easeNone });
